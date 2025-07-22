from lark import Lark, Transformer

# Load the grammar file
with open("../grammar/dronedsl_grammar.lark", "r") as f:
    grammar = f.read()

# Create the parser
parser = Lark(grammar, parser="lalr", start="start")

# Sample input from your DSL
dsl_code = '''
Task {
  DetectTask detect1 {
    area: [ (1,2,3), (4,5,6) ],
    timeout: 10
  }
}

Mission {
  Start detect1
  Transition(cond1(42)) detect1 -> detect1
}
'''

# Parse it
tree = parser.parse(dsl_code)
print(tree.pretty())