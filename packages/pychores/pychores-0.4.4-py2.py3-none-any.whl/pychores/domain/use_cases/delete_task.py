from abc import ABC, abstractmethod

from pychores.domain.entity.task import Task


class IDeleteTask(ABC):
    @abstractmethod
    def delete_task(self, task: Task):
        """Delete task"""

    @abstractmethod
    def get_task(self, username: str, task_id: int) -> Task:
        """Get task owned by username"""


class DeleteTask:
    def __init__(self, repo: IDeleteTask):
        self.repo = repo

    def execute(self, username: str, task_id: int):
        task = self.repo.get_task(username=username, task_id=task_id)
        self.repo.delete_task(task)
