# parser/parser.py

from lark import Lark
import os

# Load grammar from file
GRAMMAR_PATH = os.path.join(os.path.dirname(__file__), "grammar.lark")

with open(GRAMMAR_PATH, "r") as f:
    grammar = f.read()

# Create the Lark parser
dsl_parser = Lark(
    grammar,
    start="start",       # Starting rule in your grammar
    parser="lalr",       # Efficient parser for LALR grammars
    propagate_positions=True,
    maybe_placeholders=False
)

def parse_script(script_text: str):
    """
    Parse the given DroneDSL script and return a raw parse tree.
    """
    try:
        return dsl_parser.parse(script_text)
    except Exception as e:
        raise SyntaxError(f"Failed to parse DSL script:\n{e}")