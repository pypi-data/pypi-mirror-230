from dataclasses import dataclass
from datetime import date

from .chore import Chore


@dataclass
class Task:
    chore: Chore
    execution_date: date
    id: int | None = None
