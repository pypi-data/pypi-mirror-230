# type: ignore

from enum import Enum


class ReportFormat(str, Enum):
    JSON = "JSON"
    CSV = "CSV"

    def __str__(self):
        return str(self.value)
