from pychores.domain.entity.task import Task
from pychores.domain.use_cases.add_task import IAddTask
from pychores.model import Task as DbTask

from .builder import build_chore


class TaskRepo(IAddTask):
    def __init__(self, session):
        self.session = session

    def save_task(self, task: Task) -> Task:
        db_task = DbTask(
            id=task.id,
            chore_id=task.chore.id,
            execution_date=task.execution_date,
        )
        self.session.add(db_task)
        self.session.commit()
        return Task(
            id=db_task.id, execution_date=db_task.execution_date, chore=task.chore
        )

    def get_task(self, username: str, task_id: int) -> Task:
        db_task = self.session.get(DbTask, task_id)
        assert db_task.chore.user.username == username
        return Task(
            execution_date=db_task.execution_date,
            id=db_task.id,
            chore=build_chore(db_task.chore),
        )

    def delete_task(self, task: Task):
        db_task = self.session.get(DbTask, task.id)
        self.session.delete(db_task)
        self.session.commit()
