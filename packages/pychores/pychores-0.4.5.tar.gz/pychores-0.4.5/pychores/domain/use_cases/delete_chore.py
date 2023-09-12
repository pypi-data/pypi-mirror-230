from abc import ABC, abstractmethod

from pychores.domain.entity.chore import Chore


class IDeleteChore(ABC):
    @abstractmethod
    def get_chore(self, username: str, chore_id: int) -> Chore:
        """Return a Chore owned by username"""

    @abstractmethod
    def delete_chore(self, chore: Chore):
        """Delete `chore`"""


class DeleteChore:
    def __init__(self, repo: IDeleteChore):
        self.repo = repo

    def execute(self, username: str, chore_id: int):
        Chore = self.repo.get_chore(username=username, chore_id=chore_id)
        self.repo.delete_chore(Chore)
