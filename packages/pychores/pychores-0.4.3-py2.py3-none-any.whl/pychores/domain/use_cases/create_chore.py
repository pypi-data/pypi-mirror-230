from abc import ABC, abstractmethod
from datetime import date
from typing import Callable

from pychores.domain.entity.chore import Chore


class ICreateChore(ABC):
    @abstractmethod
    def save_new_chore(self, username: str, chore: Chore) -> Chore:
        """Save a new Chore for username"""


class InvalidChorePayload(Exception):
    pass


class CreateChore:
    def __init__(self, repo: ICreateChore, date_provider: Callable[[], date]):
        self.repo = repo
        self.date_provider = date_provider

    def execute(self, username: str, payload: dict) -> Chore:
        try:
            chore = Chore(
                name=payload["name"],
                description=payload["description"],
                period=payload["period"],
                current_date=self.date_provider(),
                last_execution=None,
            )
        except ValueError:
            raise InvalidChorePayload()
        created_chore = self.repo.save_new_chore(username=username, chore=chore)
        return created_chore
