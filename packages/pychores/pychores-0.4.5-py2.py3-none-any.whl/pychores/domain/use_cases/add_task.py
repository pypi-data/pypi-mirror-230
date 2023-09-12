from abc import ABC, abstractmethod

from pychores.domain.entity.chore import Chore
from pychores.domain.entity.task import Task


class IGetChore(ABC):
    @abstractmethod
    def get_chore(self, username: str, chore_id: int) -> Chore:
        """Return a chore owned by username"""


class IAddTask(ABC):
    @abstractmethod
    def save_task(self, task: Task) -> Task:
        """Add a new task for a chore"""


class AddTask:
    def __init__(self, chore_repo: IGetChore, task_repo: IAddTask):
        self.task_repo = task_repo
        self.chore_repo = chore_repo

    def execute(self, username: str, chore_id: int, payload: dict) -> Task:
        chore = self.chore_repo.get_chore(username=username, chore_id=chore_id)
        task = Task(
            chore=chore,
            execution_date=payload.get("execution_date", chore.current_date),
        )
        task = self.task_repo.save_task(task)
        return task
