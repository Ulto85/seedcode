class TaskManager:
    def __init__(self):
        pass

    def add_task(self, task_id: str) -> None:
        pass

    def add_dependency(self, task_id: str, dependency_id: str) -> None:
        pass

    def fail_task(self, task_id: str) -> None:
        pass

    def get_status(self, task_id: str) -> str:
        pass

    # ---- Follow-up ----
    def complete_task(self, task_id: str) -> bool:
        pass

    def get_ready(self) -> list:
        pass
