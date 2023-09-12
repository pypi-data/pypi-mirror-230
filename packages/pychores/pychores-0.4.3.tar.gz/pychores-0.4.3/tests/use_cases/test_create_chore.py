from collections import defaultdict
from datetime import date

import pytest

from pychores.domain.entity.chore import Chore
from pychores.domain.use_cases.create_chore import (
    CreateChore,
    ICreateChore,
    InvalidChorePayload,
)


class MemRepo(ICreateChore):
    def __init__(self):
        self.chores = defaultdict(list)

    def save_new_chore(self, username: str, chore: Chore):
        self.chores[username].append(chore)


def dp():
    return date(2000, 1, 1)


class TestCreateCore:
    def test_should_prevent_creation_if_period_is_invalid(self):
        payload = {
            "name": "wrong_period_type",
            "description": "A chore withe a wrong period type",
            "period": "str_should_be_int",
        }
        uc = CreateChore(MemRepo(), date_provider=dp)
        with pytest.raises(InvalidChorePayload):
            uc.execute("user1", payload=payload)
