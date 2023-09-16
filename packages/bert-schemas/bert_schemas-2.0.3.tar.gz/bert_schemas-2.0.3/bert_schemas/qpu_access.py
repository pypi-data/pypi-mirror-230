from datetime import date, time
from enum import Enum
from pydantic import BaseModel
from typing import Optional

from . import qpu


class DayOfWeek(str, Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"

    def __str__(self):
        return str(self.value)


class AccessType(str, Enum):
    GROUP = "GROUP"
    ROLE = "ROLE"
    ORG = "ORG"
    QPU = "QPU"

    def __str__(self):
        return str(self.value)


class AccessSlot(BaseModel):
    day: DayOfWeek
    start_date: date
    end_date: Optional[date] = None
    start_time: time
    end_time: time


class Access(BaseModel):
    qpu_name: qpu.QPUName
    access_name: Optional[str] = None
    access_type: AccessType
    access_slots: list[AccessSlot] = []
