import pytest

from pychores.domain.entity.user import User
from pychores.domain.use_cases.sign_user_in import IGetUserRepo, SignUserIn


class DumyGetUserRepo(IGetUserRepo):
    def get_user(self, username: str) -> User:
        return User(email="fake@example.com", username="fake", password="hunter2")


def dumy_password_checker(crypted_pass: str, raw_pass: str) -> bool:
    return crypted_pass == raw_pass


class TestSignUserIn:
    def test_wrong_password_should_raise_value_error(self):
        uc = SignUserIn(DumyGetUserRepo(), dumy_password_checker)
        with pytest.raises(ValueError):
            uc.execute({"username": "fake", "password": "bad pass"})
