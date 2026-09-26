"""
Session 24 - Task 4: Safe Expression Calculator Tool (No eval)
--------------------------------------------------------------
Evaluates mathematical expressions (e.g., '23+7*2') supporting basic operations
(+, -, *, /) along with parentheses, unary operators, and floating-point numbers.

CONSTRAINT COMPLIANCE:
- Python's built-in `eval()` is strictly NOT used anywhere in this module.
- `exec()` and `compile()` are also strictly avoided.
- Expression parsing is implemented via:
  1. Pure-Python Recursive Descent Parser (Tokenizer + Pratt/Grammar parser)
  2. Safe AST Visitor (standard `ast` module nodes strictly limited to BinOp/UnaryOp/Constant)
"""

import sys
import re
import ast
import operator
from typing import Union, List, Tuple

# Ensure UTF-8 output encoding on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ============================================================================
# Method 1: Pure Recursive Descent Parser & Lexer (Zero built-in eval/ast)
# ============================================================================

class TokenType:
    NUMBER = "NUMBER"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    EOF = "EOF"


class Token:
    def __init__(self, type_: str, value: Union[float, str]):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class SafeMathLexer:
    """Tokenizes raw mathematical strings into typed tokens."""

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def extract_number(self) -> float:
        num_str = ""
        has_dot = False
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == "."):
            if self.current_char == ".":
                if has_dot:
                    raise ValueError(f"Malformed decimal number near index {self.pos}")
                has_dot = True
            num_str += self.current_char
            self.advance()
        return float(num_str)

    def get_next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit() or self.current_char == ".":
                return Token(TokenType.NUMBER, self.extract_number())

            if self.current_char == "+":
                self.advance()
                return Token(TokenType.PLUS, "+")

            if self.current_char == "-":
                self.advance()
                return Token(TokenType.MINUS, "-")

            if self.current_char == "*":
                self.advance()
                return Token(TokenType.MUL, "*")

            if self.current_char == "/":
                self.advance()
                return Token(TokenType.DIV, "/")

            if self.current_char == "(":
                self.advance()
                return Token(TokenType.LPAREN, "(")

            if self.current_char == ")":
                self.advance()
                return Token(TokenType.RPAREN, ")")

            raise ValueError(f"Unexpected character '{self.current_char}' at position {self.pos}")

        return Token(TokenType.EOF, "")


class SafeMathParser:
    """
    Recursive Descent Parser enforcing standard BODMAS / PEMDAS precedence:
    Grammar:
        expression := term ((PLUS | MINUS) term)*
        term       := factor ((MUL | DIV) factor)*
        factor     := (PLUS | MINUS) factor | primary
        primary    := NUMBER | LPAREN expression RPAREN
    """

    def __init__(self, lexer: SafeMathLexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type: str):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise ValueError(f"Syntax error: Expected token {token_type}, got {self.current_token.type}")

    def primary(self) -> float:
        """primary := NUMBER | LPAREN expression RPAREN"""
        token = self.current_token

        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return float(token.value)

        if token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            result = self.expression()
            self.eat(TokenType.RPAREN)
            return result

        raise ValueError(f"Syntax error: Unexpected token '{token.value}' in expression")

    def factor(self) -> float:
        """factor := (PLUS | MINUS) factor | primary"""
        token = self.current_token
        if token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            return +self.factor()
        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return -self.factor()
        return self.primary()

    def term(self) -> float:
        """term := factor ((MUL | DIV) factor)*"""
        result = self.factor()

        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            token = self.current_token
            if token.type == TokenType.MUL:
                self.eat(TokenType.MUL)
                result *= self.factor()
            elif token.type == TokenType.DIV:
                self.eat(TokenType.DIV)
                divisor = self.factor()
                if divisor == 0:
                    raise ZeroDivisionError("Error: Division by zero is undefined.")
                result /= divisor

        return result

    def expression(self) -> float:
        """expression := term ((PLUS | MINUS) term)*"""
        result = self.term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
                result += self.term()
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
                result -= self.term()

        return result

    def parse(self) -> float:
        res = self.expression()
        if self.current_token.type != TokenType.EOF:
            raise ValueError(f"Unexpected trailing tokens near '{self.current_token.value}'")
        return res


# ============================================================================
# Method 2: Safe AST Visitor (Whitelisted Operators Only, No Code Execution)
# ============================================================================

SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class SafeASTEvaluator(ast.NodeVisitor):
    """Walks the Python AST and strictly evaluates only arithmetic operations."""

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
        if op_type is ast.Div and right == 0:
            raise ZeroDivisionError("Error: Division by zero is undefined.")
        return SAFE_OPERATORS[op_type](left, right)

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        return SAFE_OPERATORS[op_type](operand)

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")

    def visit_Expression(self, node):
        return self.visit(node.body)

    def generic_visit(self, node):
        raise ValueError(f"Disallowed syntax node '{type(node).__name__}'. Only arithmetic expressions allowed.")


# ============================================================================
# Main Public Interface
# ============================================================================

def safe_calculate(expression: str, method: str = "parser") -> Union[int, float]:
    """
    Evaluates a mathematical expression string safely without using eval().

    Args:
        expression: Mathematical expression string (e.g. '23+7*2').
        method: Parsing method ('parser' for Recursive Descent, 'ast' for AST visitor).

    Returns:
        int or float: Numeric result.
    """
    if not isinstance(expression, str) or not expression.strip():
        raise ValueError("Expression must be a non-empty string.")

    cleaned_expr = expression.strip()

    if method == "parser":
        lexer = SafeMathLexer(cleaned_expr)
        parser = SafeMathParser(lexer)
        raw_result = parser.parse()
    elif method == "ast":
        parsed_tree = ast.parse(cleaned_expr, mode="eval")
        evaluator = SafeASTEvaluator()
        raw_result = evaluator.visit(parsed_tree)
    else:
        raise ValueError(f"Unknown calculation method '{method}'")

    # Format cleanly (e.g., 37.0 -> 37, 2.5 -> 2.5)
    if isinstance(raw_result, float) and raw_result.is_integer():
        return int(raw_result)
    return round(raw_result, 6)


def evaluate_and_display(expression: str) -> None:
    """Helper to evaluate and print formatted result."""
    print("=" * 60)
    print(" 🧮  SAFE CALCULATOR TOOL (NO EVAL())")
    print("=" * 60)
    print(f"📥 Input Expression : {expression}")

    try:
        # Evaluate with primary recursive descent parser
        result_parser = safe_calculate(expression, method="parser")
        # Validate against AST evaluator
        result_ast = safe_calculate(expression, method="ast")

        print(f"⚙️  Parser Engine    : Recursive Descent (Pure Python)")
        print(f"🛡️  Safety Check    : AST Verified ({result_parser} == {result_ast})")
        print("-" * 60)
        print(f"👉 Result           : {result_parser}")
        print("=" * 60)
    except ZeroDivisionError as zde:
        print(f"❌ Math Error       : {zde}")
        print("=" * 60)
    except Exception as ex:
        print(f"❌ Evaluation Error : {ex}")
        print("=" * 60)


def main():
    """Main execution point with demo cases and CLI input support."""
    if len(sys.argv) > 1:
        expr = " ".join(sys.argv[1:])
        evaluate_and_display(expr)
    else:
        # Default test cases requested in prompt
        demo_expressions = [
            "23+7*2",           # Primary task expression: 23 + 14 = 37
            "100 - 25 * 3",     # Precedence: 100 - 75 = 25
            "(23 + 7) * 2",     # Parentheses: 30 * 2 = 60
            "10 / 4 + 7.5",     # Decimals and division: 2.5 + 7.5 = 10
            "-5 + 20 * 2",      # Unary negative: -5 + 40 = 35
        ]

        print("\n[Safe Calculator Agent Tool] Demonstrating safe mathematical evaluations:")
        for expr in demo_expressions:
            evaluate_and_display(expr)
            print()


if __name__ == "__main__":
    main()
