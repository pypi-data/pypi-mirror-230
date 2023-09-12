from abc import ABC, abstractmethod

from pychores.domain.entity.chore import Chore


class IGetChore(ABC):
    @abstractmethod
    def get_chore(self, username: str, chore_id: int) -> Chore:
        """Return chore owned by username"""


class GetChore:
    def __init__(self, repo: IGetChore):
        self.repo = repo

    def execute(self, username: str, chore_id: int) -> Chore:
        return self.repo.get_chore(username, chore_id)
