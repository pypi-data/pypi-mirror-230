from dataclasses import field
from datetime import date, timedelta

from pydantic.dataclasses import dataclass


@dataclass
class Chore:
    name: str
    description: str
    period: int
    current_date: date
    last_execution: date | None
    id: int | None = None
    next_execution: date = field(init=False)
    is_overdue: bool = field(init=False)

    def __post_init__(self):
        self.next_execution = (
            self.last_execution + timedelta(days=self.period)
            if self.last_execution
            else date.today()
        )
        self.is_overdue = self.next_execution < self.current_date
