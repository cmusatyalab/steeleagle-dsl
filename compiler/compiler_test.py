from lark import Lark, Transformer

# Load the grammar file
with open("../grammar/dronedsl.lark", "r") as f:
    grammar = f.read()

# Create the parser
parser = Lark(grammar, parser="lalr", start="start")

# Sample input from your DSL
dsl_code = '''
Actions:
  Patrol patrol1 (area: sectorA)
  Land   land1
  Avoid  avoid1 (sensitivity: high)

Events:
  HSVDetect person_detected (target: person)
  Timeout   patrol_timeout  (after: 60s)

Mission:
  Start patrol1

  During patrol1:
    person_detected -> avoid1
    patrol_timeout  -> land1
    # done is implicit: patrol_done -> land1

  During avoid1:
    avoid_cleared -> patrol1
    # done is implicit: avoid_done -> land1
'''

# Parse it
tree = parser.parse(dsl_code)
print(tree.pretty())