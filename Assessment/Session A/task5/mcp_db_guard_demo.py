"""
Guarded query engine for a Database MCP Server (list_tables / describe_table /
run_select_query), demonstrating the safeguards that stop an LLM from ever
seeing sensitive columns -- enforced server-side, not by prompting.

This version uses only the Python standard library (sqlite3 + re), so it
runs with zero installs. In production, swap the regex-based SQL inspection
for a real parser (e.g. `pip install sqlglot --break-system-packages`) --
an AST walk is far more robust than regex against obfuscated or nested
queries. The enforcement *logic and order of checks* below is unchanged
either way.

Install: none required.
Run:
    python3 mcp_db_guard_demo.py
"""

import re
import sqlite3

DB_PATH = ":memory:"

# Column sensitivity map -- this is the source of truth describe_table() reads from,
# and what run_select_query() enforces against, independent of what the LLM asks for.
SCHEMA_SENSITIVITY = {
    "orders": {
        "order_id": "public",
        "restaurant_id": "public",
        "status": "public",
        "created_at": "public",
        "delivery_partner_id": "public",
        "customer_id": "public",
        "customer_phone": "pii",
        "payment_token": "financial",
    },
    "delivery_partner_locations": {
        "order_id": "public",
        "delivery_partner_id": "public",
        "latitude": "public",
        "longitude": "public",
        "updated_at": "public",
    },
}

DENIED_SENSITIVITY_LEVELS = {"pii", "financial"}
ROW_LIMIT = 100


def setup_demo_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE orders (
            order_id INTEGER, restaurant_id INTEGER, status TEXT,
            created_at TEXT, delivery_partner_id INTEGER, customer_id INTEGER,
            customer_phone TEXT, payment_token TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE delivery_partner_locations (
            order_id INTEGER, delivery_partner_id INTEGER,
            latitude REAL, longitude REAL, updated_at TEXT
        )
    """)
    cur.execute("""INSERT INTO orders VALUES
        (48213, 12, 'delayed', '2026-09-17T18:40:00', 7, 501,
         '+91-98765-43210', 'tok_live_abc123')""")
    cur.execute("""INSERT INTO delivery_partner_locations VALUES
        (48213, 7, 12.9716, 77.5946, '2026-09-17T18:55:00')""")
    conn.commit()
    return conn


# ---------- MCP-style tools ----------

def list_tables() -> list[str]:
    return list(SCHEMA_SENSITIVITY.keys())


def describe_table(table_name: str) -> dict:
    if table_name not in SCHEMA_SENSITIVITY:
        return {"error": f"unknown table: {table_name}"}
    return {"table": table_name, "columns": SCHEMA_SENSITIVITY[table_name]}


FORBIDDEN_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|ATTACH|PRAGMA|CREATE|REPLACE|TRUNCATE)\b",
    re.IGNORECASE,
)
MULTI_STATEMENT = re.compile(r";.*\S")  # anything meaningful after a semicolon


def run_select_query(conn: sqlite3.Connection, sql: str) -> dict:
    stripped = sql.strip().rstrip(";")

    # 1. Must be a single SELECT statement -- no INSERT/UPDATE/DELETE/DROP,
    #    no stacked statements smuggled in after a semicolon.
    if not re.match(r"^\s*SELECT\b", stripped, re.IGNORECASE):
        return {"error": "only SELECT statements are permitted"}
    if FORBIDDEN_KEYWORDS.search(stripped):
        return {"error": "query contains a disallowed write/DDL keyword"}
    if MULTI_STATEMENT.search(sql):
        return {"error": "multiple statements are not permitted"}

    # 2. No SELECT * on tables containing sensitive columns.
    if re.match(r"^\s*SELECT\s+\*", stripped, re.IGNORECASE):
        return {"error": "SELECT * is not permitted -- name columns explicitly"}

    # 3. Enumerate every identifier token referenced and check it against the
    #    sensitivity map. This is what stops leakage even if the LLM's stated
    #    intent ("I only need delivery status") doesn't match what it wrote.
    #    (A real implementation should walk a parsed AST rather than regex
    #    tokens, to be robust against aliases/subqueries/obfuscation.)
    referenced_columns = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", stripped))
    denied = []
    for table_cols in SCHEMA_SENSITIVITY.values():
        for col, level in table_cols.items():
            if col in referenced_columns and level in DENIED_SENSITIVITY_LEVELS:
                denied.append(col)

    if denied:
        return {
            "error": f"query references restricted column(s): {sorted(set(denied))}. "
                     f"Remove them and retry."
        }

    # 4. Enforce row limit regardless of what the query asked for.
    limited_sql = f"SELECT * FROM ({sql}) LIMIT {ROW_LIMIT}"

    cur = conn.cursor()
    try:
        cur.execute(limited_sql)
    except sqlite3.Error as e:
        return {"error": f"execution failed: {e}"}

    columns = [d[0] for d in cur.description]
    rows = cur.fetchall()
    return {"columns": columns, "rows": rows}


def main():
    conn = setup_demo_db()

    print("== list_tables() ==")
    print(list_tables())
    print()

    print("== describe_table('orders') ==")
    print(describe_table("orders"))
    print()

    print("== Support agent question: why is order 48213 delayed, and where is it? ==")
    good_sql = """
        SELECT o.order_id, o.status, o.created_at, d.latitude, d.longitude, d.updated_at
        FROM orders o
        JOIN delivery_partner_locations d ON o.order_id = d.order_id
        WHERE o.order_id = 48213
    """
    result = run_select_query(conn, good_sql)
    print("Query:", good_sql.strip())
    print("Result:", result)
    print()

    print("== Attempt to also pull customer_phone (should be blocked) ==")
    bad_sql = "SELECT order_id, status, customer_phone FROM orders WHERE order_id = 48213"
    result = run_select_query(conn, bad_sql)
    print("Query:", bad_sql)
    print("Result:", result)
    print()

    print("== Attempt SELECT * (should be blocked) ==")
    star_sql = "SELECT * FROM orders WHERE order_id = 48213"
    result = run_select_query(conn, star_sql)
    print("Query:", star_sql)
    print("Result:", result)
    print()

    print("== Attempt a write statement (should be blocked) ==")
    write_sql = "UPDATE orders SET status = 'delivered' WHERE order_id = 48213"
    result = run_select_query(conn, write_sql)
    print("Query:", write_sql)
    print("Result:", result)


if __name__ == "__main__":
    main()
