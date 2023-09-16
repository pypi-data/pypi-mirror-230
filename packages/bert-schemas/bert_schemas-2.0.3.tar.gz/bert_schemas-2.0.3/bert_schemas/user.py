# type: ignore
from datetime import datetime
from typing import List, Optional, Type
from enum import Enum

from pydantic import StringConstraints, ConfigDict, BaseModel, EmailStr, HttpUrl

from .questionnaire import RegistrationQandA
from typing_extensions import Annotated

external_user_id: Type[str] = Annotated[
    str, StringConstraints(pattern=r"^auth0|[a-z0-9]{24}$")
]


class RoleName(str, Enum):
    SUPERUSER = "SUPERUSER"
    ORG_ADMIN = "ORG_ADMIN"

    def __str__(self):
        return str(self.value)


class PurchaseEntity(str, Enum):
    USER = "USER"
    PAID = "PAID"
    ORG = "ORG"


class JobLimitType(str, Enum):
    JOB_RATE = "JOB_RATE"
    JOB_QUOTA = "JOB_QUOTA"


class ExternalUserId(BaseModel):
    external_user_id: external_user_id


class RoleBase(BaseModel):
    name: RoleName
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class Role(RoleBase):
    pass


class Organization(BaseModel):
    name: str
    id: int
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    email: EmailStr
    affiliation: str
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class OrganizationUser(UserBase):
    external_user_id: external_user_id
    jobs_run_today: int


class EmailPreference(BaseModel):
    jobs: bool
    general: bool
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(UserBase):
    email_preferences: Optional[EmailPreference] = None


class UserResponse(UserBase):
    signup_date: datetime
    external_user_id: external_user_id
    roles: Optional[List[Role]] = None
    organization: Optional[Organization] = None
    active: bool
    email_preferences: EmailPreference


class UserSearchResponse(UserBase):
    external_user_id: str
    organization: Optional[Organization] = None


class User(UserBase):
    id: int
    external_user_id: external_user_id
    signup_date: datetime
    roles: Optional[List[Role]] = None
    organization: Optional[Organization] = None


class UserCreate(UserBase):
    external_user_id: external_user_id


class UserSignUp(UserBase):
    questionnaire: RegistrationQandA
    response: Optional[str] = None
    model_config = ConfigDict(use_enum_values=True)


class JobLimit(BaseModel):
    daily_limit: int
    daily_used: int
    daily_remaining: int
    purchased: Optional[int] = None
    purchased_remaining: Optional[int] = None


class JobPurchase(BaseModel):
    purchase_date: datetime
    quantity: int
    model_config = ConfigDict(from_attributes=True)


class UserJobPurchase(JobPurchase):
    user_id: int


class OrgJobPurchase(JobPurchase):
    org_id: int


class PurchasePriceData(BaseModel):
    currency: str
    product_data: dict
    unit_amount: int


class PurchaseLineItem(BaseModel):
    amount: int | None = None
    currency: str | None = None
    description: str | None = None
    price: str
    quantity: int
    price_data: PurchasePriceData | None = None


class CheckoutSessionLineItem(BaseModel):
    quantity: int


class CheckoutSession(BaseModel):
    status: str
    created: datetime
    amount_total: int
    line_items: list[CheckoutSessionLineItem]


class PurchaseCharge(BaseModel):
    created: datetime
    amount_captured: int
    currency: str
    card_last4: int
    card_brand: str
    receipt_url: str


class CheckoutSessionLineItem(BaseModel):
    quantity: int


class CheckoutSession(BaseModel):
    status: str
    created: datetime
    amount_total: int
    line_items: list[CheckoutSessionLineItem]


class PurchaseCharge(BaseModel):
    created: datetime
    amount_captured: int
    currency: str
    card_last4: int
    card_brand: str
    receipt_url: str


class CheckoutSessionResponse(BaseModel):
    session_url: HttpUrl


class ContactUs(BaseModel):
    subject: str
    email: EmailStr
    content: Annotated[str, StringConstraints(min_length=1, max_length=500)]
