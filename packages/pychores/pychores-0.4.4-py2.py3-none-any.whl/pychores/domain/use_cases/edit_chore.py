from abc import ABC, abstractmethod

from pychores.domain.entity.chore import Chore


class IEditChore(ABC):
    @abstractmethod
    def get_chore(self, username: str, chore_id: int) -> Chore:
        """Return Chore with chore_id for username if exists"""

    @abstractmethod
    def save_chore(self, chore: Chore) -> Chore:
        """Save the chore"""


class EditChore:
    def __init__(self, repo: IEditChore):
        self.repo = repo

    def execute(self, username: str, chore_id: int, payload: dict) -> Chore:
        old_chore = self.repo.get_chore(username, chore_id)
        new_chore = Chore(
            id=old_chore.id,
            name=payload.get("name", old_chore.name),
            current_date=old_chore.current_date,
            description=payload.get("description", old_chore.description),
            period=payload.get("period", old_chore.period),
            last_execution=old_chore.last_execution,
        )
        self.repo.save_chore(new_chore)
        return new_chore
