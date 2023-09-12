from abc import ABC, abstractmethod

from pychores.domain.entity.task import Task


class IGetTask(ABC):
    @abstractmethod
    def get_task(self, username: str, task_id: int) -> Task:
        """Get task owned by username"""


class GetTask:
    def __init__(self, repo: IGetTask):
        self.repo = repo

    def execute(self, username: str, task_id: int):
        task = self.repo.get_task(username=username, task_id=task_id)
        return task
