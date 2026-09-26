"""
Session 24 - Task 2: Expense Tracker CSV Reader
-----------------------------------------------
Reads 'my_expenses.csv' (with columns: date, amount, category)
and prints the total amount spent in the 'Food' category.

Features:
- Case-insensitive category matching ('Food', 'food', 'FOOD')
- Robust numeric parsing (strips whitespace, currency symbols, commas)
- Fallback path resolution (locates CSV in current dir or script dir)
- Auto-generates sample CSV if missing
- Complete breakdown across all expense categories
"""

import sys
import os
import csv
from typing import Dict, List, Tuple, Any

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def resolve_expenses_file(filename: str = "my_expenses.csv") -> str:
    """
    Locates the expenses CSV file either in current working directory,
    script directory, or creates a default file if not found.
    """
    if os.path.isabs(filename) and os.path.exists(filename):
        return filename

    # Check cwd
    cwd_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(cwd_path):
        return cwd_path

    # Check script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, filename)
    if os.path.exists(script_path):
        return script_path

    # If neither exists, create sample file in script directory
    print(f"⚠️  '{filename}' not found. Generating default sample file at: {script_path}")
    sample_content = (
        "date,amount,category\n"
        "2026-09-20,250.50,Food\n"
        "2026-09-20,150.00,Travel\n"
        "2026-09-21,450.00,Food\n"
        "2026-09-21,1200.00,Utilities\n"
        "2026-09-22,120.00,Food\n"
        "2026-09-22,350.00,Entertainment\n"
        "2026-09-23,800.00,Groceries\n"
        "2026-09-24,380.00,Food\n"
        "2026-09-25,500.00,Travel\n"
        "2026-09-26,600.00,Books\n"
    )
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(sample_content)
    return script_path


def parse_amount(raw_val: Any) -> float:
    """Cleans currency symbols, commas, and whitespace, converting to float."""
    if isinstance(raw_val, (int, float)):
        return float(raw_val)
    val_str = str(raw_val).strip()
    for symbol in ["$", "₹", "€", "£", ","]:
        val_str = val_str.replace(symbol, "")
    return float(val_str)


def calculate_food_expenses(
    filepath: str = "my_expenses.csv",
    target_category: str = "Food"
) -> float:
    """
    Reads the given CSV file (with columns: date, amount, category)
    and prints the total amount spent in the 'Food' (or specified) category.

    Args:
        filepath: Path to the CSV file (defaults to 'my_expenses.csv').
        target_category: Category to calculate total for (defaults to 'Food').

    Returns:
        float: Total amount spent in the target category.
    """
    resolved_path = resolve_expenses_file(filepath)
    normalized_target = target_category.strip().lower()

    matching_records: List[Dict[str, Any]] = []
    total_spent: float = 0.0
    all_categories: Dict[str, float] = {}
    row_count = 0

    with open(resolved_path, mode="r", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)

        # Normalize column header names
        if reader.fieldnames:
            field_map = {col.strip().lower(): col for col in reader.fieldnames}
        else:
            field_map = {}

        date_col = field_map.get("date", "date")
        amount_col = field_map.get("amount", "amount")
        cat_col = field_map.get("category", "category")

        for row_idx, row in enumerate(reader, start=1):
            row_count += 1
            raw_cat = row.get(cat_col, "").strip()
            raw_amt = row.get(amount_col, "").strip()
            date_val = row.get(date_col, "").strip()

            if not raw_amt:
                continue

            try:
                amount_num = parse_amount(raw_amt)
            except ValueError:
                print(f"⚠️ Warning: Skipping row {row_idx} due to invalid amount: '{raw_amt}'")
                continue

            # Accumulate overall breakdown
            cleaned_cat_name = raw_cat.title() if raw_cat else "Uncategorized"
            all_categories[cleaned_cat_name] = all_categories.get(cleaned_cat_name, 0.0) + amount_num

            # Match target category
            if raw_cat.lower() == normalized_target:
                matching_records.append({
                    "date": date_val,
                    "amount": amount_num,
                    "category": raw_cat,
                })
                total_spent += amount_num

    # Formatted terminal display
    print("=" * 65)
    print(f" 💳  EXPENSE REPORT: CATEGORY '{target_category.upper()}'")
    print("=" * 65)
    print(f"📁 Source File      : {resolved_path}")
    print(f"📊 Total Rows Read  : {row_count}")
    print(f"🎯 Matching Entries : {len(matching_records)}")
    print("-" * 65)

    if matching_records:
        print(f"{'Date':<15} | {'Category':<15} | {'Amount (INR / Base)':>18}")
        print("-" * 65)
        for rec in matching_records:
            print(f"{rec['date']:<15} | {rec['category']:<15} | {rec['amount']:>18.2f}")
        print("-" * 65)

    print(f"👉 Total Amount Spent in '{target_category}': {total_spent:.2f}")
    print("=" * 65)

    # Optional overview of other categories
    if len(all_categories) > 1:
        print("\n📈 Category-wise Spending Overview:")
        grand_total = sum(all_categories.values())
        for cat, amt in sorted(all_categories.items(), key=lambda x: x[1], reverse=True):
            pct = (amt / grand_total * 100) if grand_total > 0 else 0.0
            bar = "█" * int(pct / 5)
            print(f"  • {cat:<15}: {amt:>10.2f} ({pct:>5.1f}%) {bar}")
        print(f"  • Grand Total    : {grand_total:>10.2f}\n" + "=" * 65)

    return total_spent


def main():
    """Main execution point."""
    file_arg = sys.argv[1] if len(sys.argv) > 1 else "my_expenses.csv"
    cat_arg = sys.argv[2] if len(sys.argv) > 2 else "Food"
    calculate_food_expenses(filepath=file_arg, target_category=cat_arg)


if __name__ == "__main__":
    main()
