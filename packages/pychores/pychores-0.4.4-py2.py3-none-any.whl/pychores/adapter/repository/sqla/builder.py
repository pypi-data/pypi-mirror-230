from datetime import date

from pychores.domain.entity.chore import Chore
from pychores.model import Chore as DbChore


def build_chore(db_chore: DbChore) -> Chore:
    return Chore(
        id=db_chore.id,
        name=db_chore.name,
        description=db_chore.description,
        period=db_chore.period,
        current_date=date.today(),
        last_execution=max(t.execution_date for t in db_chore.tasks)
        if db_chore.tasks
        else None,
    )
