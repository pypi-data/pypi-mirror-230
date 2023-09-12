from abc import ABC, abstractmethod
from typing import Callable

from pychores.domain.entity.user import User


class IGetUserRepo(ABC):
    @abstractmethod
    def get_user(self, username: str) -> User:
        """Retrieve a user by username"""


class SignUserIn:
    def __init__(
        self, repo: IGetUserRepo, password_checker: Callable[[str, str], bool]
    ):
        self.repo = repo
        self.password_checker = password_checker

    def execute(self, payload: dict) -> User:
        user = self.repo.get_user(payload["username"])
        if not self.password_checker(user.password, payload["password"]):
            raise ValueError("Wrong password or username")
        return user
