from tasks.base import task_registry

def check_availability(task_type: str):
    if task_type not in task_registry:
        raise ValueError(f"Unregistered task type: {task_type}")
    return task_registry[task_type]

def check_args():
    # Placeholder for argument checking logic
    pass
