from datetime import datetime
from typing import Union

from pydantic import field_validator, ConfigDict, BaseModel


class MessageBase(BaseModel):
    location: int = 1
    message: str
    start_datetime: datetime
    end_datetime: datetime
    model_config = ConfigDict(from_attributes=True, validate_assignment=True)


class Message(MessageBase):
    id: int


class MessageResponse(Message):
    location: int = 1
    message: str
    start_datetime: Union[str, datetime]
    end_datetime: Union[str, datetime]

    @field_validator("start_datetime", mode="before")
    @classmethod
    def formate_start_datetime(cls, value):
        return value.strftime("%m/%d/%Y @ %H:%M")

    @field_validator("end_datetime", mode="before")
    @classmethod
    def formate_end_datetime(cls, value):
        return value.strftime("%m/%d/%Y @ %H:%M")
