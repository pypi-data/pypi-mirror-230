from abc import ABC, abstractmethod
from typing import Callable

from pychores.domain.entity.user import User


class ISaveUserRepo(ABC):
    @abstractmethod
    def save_user(self, user: User):
        """Save the domain part of user"""


class CreateUser:
    def __init__(self, repo: ISaveUserRepo, password_hasher: Callable[[str], str]):
        self.repo = repo
        self.password_hasher = password_hasher

    def execute(self, payload: dict) -> User:
        user = User(
            username=payload["username"],
            email=payload["email"],
            password=self.password_hasher(payload["password"]),
        )
        self.repo.save_user(user)
        return user
