from pathlib import Path
from lark import Lark
from compiler.transformer import DroneDSLTransformer

# Load grammar
GRAMMAR_PATH = Path("../grammar/dronedsl.lark")
grammar = GRAMMAR_PATH.read_text(encoding="utf-8")

# Create parser
parser = Lark(grammar, parser="lalr", start="start")

# Sample DSL

dsl_code_naive = """
Actions:
  TakeOff takeoff1 (test: nope)
  Land   land1

Mission:
  Start takeoff1
"""

dsl_code = """
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
"""

def main():
    # Parse
    tree = parser.parse(dsl_code_naive)
    print(tree.pretty())
    # Transform
    mission = DroneDSLTransformer(implicit_done=True).transform(tree)

    # Print results
    print("Start:", mission.start_action_id)
    print("Actions:", sorted(mission.actions.keys()))
    print("Events:", sorted(mission.events.keys()))
    print("Transitions:")
    for (state, ev), nxt in sorted(mission.transitions.items()):
        print(f"  {state} + {ev} -> {nxt}")

if __name__ == "__main__":
    main()