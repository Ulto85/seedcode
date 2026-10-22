class GpuCluster:
    def __init__(self, hosts: list):
        pass

    def place(self, task_id: str, gpus: int, mem: int) -> int:
        pass

    def release(self, task_id: str) -> bool:
        pass

    def host_of(self, task_id: str):
        pass

    # Follow-up
    def submit(self, task_id: str, gpus: int, mem: int) -> int:
        pass

    def pending(self) -> list:
        pass
