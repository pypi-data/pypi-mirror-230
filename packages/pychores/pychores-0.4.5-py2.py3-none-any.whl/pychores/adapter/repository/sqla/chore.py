from sqlalchemy import func

from pychores.domain.entity.chore import Chore
from pychores.domain.use_cases.create_chore import ICreateChore
from pychores.domain.use_cases.get_chore import IGetChore
from pychores.domain.use_cases.get_user_chores import IGetChores
from pychores.model import Chore as DbChore
from pychores.model import Task as DbTask
from pychores.model import User as DbUser

from .builder import build_chore


class ChoreRepo(IGetChores, ICreateChore, IGetChore):
    def __init__(self, session):
        self.session = session

    def get_chores(self, username: str) -> list[Chore]:
        last_tasks = (
            self.session.query(
                DbTask.chore_id,
                func.max(DbTask.execution_date).label("last_execution"),
            )
            .group_by(DbTask.chore_id)
            .subquery()
        )
        db_chores = (
            self.session.query(DbChore)
            .join(DbUser)
            .outerjoin(last_tasks, last_tasks.c.chore_id == Chore.id)
            .filter(DbUser.username == username)
        )

        return [build_chore(c) for c in db_chores]

    def get_chore(self, username: str, chore_id: int) -> Chore:
        db_chore = self.session.get(DbChore, chore_id)
        assert db_chore.user.username == username
        return build_chore(db_chore)

    def save_new_chore(self, username: str, chore: Chore) -> Chore:
        db_user = self.session.query(DbUser).filter_by(username=username).one()
        db_chore = DbChore(
            name=chore.name, description=chore.description, period=chore.period
        )
        db_user.chores.append(db_chore)
        self.session.commit()
        return build_chore(db_chore)

    def save_chore(self, chore: Chore) -> Chore:
        db_chore = self.session.get(DbChore, chore.id)
        db_chore.name = chore.name
        db_chore.description = chore.description
        db_chore.period = chore.period
        self.session.commit()
        return chore

    def delete_chore(self, chore: Chore):
        db_chore = self.session.get(DbChore, chore.id)
        self.session.delete(db_chore)
        self.session.commit()
