from lark import Transformer
from tasks.base import task_registry
from compiler.ir import MissionIR, TransitionIR


class DroneDSLTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self.task_definitions = {}
        self.transitions = []
        self.start_task = None

    def task_decl(self, items):
        task_type_name, task_name, attributes = items
        task_type_str = str(task_type_name)
        task_name_str = str(task_name)

        task_cls = task_registry.get(task_type_str)
        if task_cls is None:
            raise ValueError(f"Unregistered task type: {task_type_str}")

        kwargs = {k: v for k, v in attributes}
        kwargs['task_id'] = task_name_str

        instance = task_cls(**kwargs)
        self.task_definitions[task_name_str] = instance

    def attribute(self, items):
        key, value = items
        return str(key), value

    def paren_tuple(self, items):
        return tuple(float(x) for x in items)

    def attribute_expr(self, items):
        return items[0]

    def mission_start_decl(self, items):
        self.start_task = str(items[0])

    def mission_transition(self, items):
        cond, from_task, to_task = items
        self.transitions.append(TransitionIR(
            cond_id=cond['id'],
            cond_arg=cond.get('arg'),
            from_task=str(from_task),
            to_task=str(to_task)
        ))

    def cond(self, items):
        cond_id = str(items[0])
        if len(items) == 2:
            arg = items[1]
            return {'id': cond_id, 'arg': arg}
        return {'id': cond_id}

    def start(self, _):
        return MissionIR(
            tasks=self.task_definitions,
            transitions=self.transitions,
            start=self.start_task
        )

    # Simple terminals
    def ID(self, token):
        return str(token)

    def NUMBER(self, token):
        return float(token) if '.' in token else int(token)
