from datetime import time
from typing import List, Optional
from enum import Enum
from pydantic import field_validator, ConfigDict, BaseModel


class QPUName(str, Enum):
    SMALLBERT = "SMALLBERT"
    BIGBERT = "BIGBERT"
    UNDEFINED = "UNDEFINED"

    def __str__(self):
        return str(self.value)


class QPUStatus(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"

    def __str__(self):
        return str(self.value)


class QPUJobType(BaseModel):
    name: str
    model_config = ConfigDict(from_attributes=True)


class QPUAccess(BaseModel):
    day: str
    start_time: time
    end_time: time
    model_config = ConfigDict(from_attributes=True)


class QPUBase(BaseModel):
    name: QPUName
    status: QPUStatus
    model_config = ConfigDict(from_attributes=True)


class QPU(QPUBase):
    qpu_access: List[QPUAccess]
    job_types: List[QPUJobType]

    @field_validator("job_types")
    @classmethod
    def job_type_names(cls, value):
        return [i.name for i in value]

    model_config = ConfigDict(from_attributes=True)


class QPUState(QPU):
    pending_internal_jobs: Optional[int] = None
    pending_external_jobs: Optional[int] = None


class QPUStatusUpdate(BaseModel):
    status: QPUStatus

    # @root_validator()
    # def check_status_or_hours(cls, values):
    #     if (values.get("status") is None) and (values.get("operation_hours") is None):
    #         raise ValueError("either status or operation_hours is required")
    #     return values
