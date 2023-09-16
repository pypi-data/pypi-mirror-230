from typing import List, Literal, Optional, Union
from enum import Enum

from pydantic import ConfigDict, BaseModel


class QuestionnaireName(str, Enum):
    REGISTRATION = "Registration"
    ACCT_UPGRADE = "Account Upgrade"

    def __str__(self):
        return str(self.value)


class UseReason(str, Enum):
    """
    # TECH_USE = "Technology Development"
    # SCI_USE = "Scientific Research"
    # EDU_USE = "Education"
    # CUR_USE = "Curious"
    # OTH_USE = "Other" """

    SCI_USE = "SCI_USE"
    TECH_USE = "TECH_USE"
    EDU_USE = "EDU_USE"
    CUR_USE = "CUR_USE"
    OTH_USE = "OTH_USE"

    def __str__(self):
        return str(self.value)


class SchoolLevel(str, Enum):
    """
    # PRIMARY = "Primary (K-8)"
    # SECONDARY = "Secondary (9-12)"
    # COLLEGE = "College/University"
    # POSTGRAD = "Post-Graduate"
    # NOTGIVEN = "Not Given"
    PRIMARY = "PRIMARY" """

    SECONDARY = "SECONDARY"
    COLLEGE = "COLLEGE"
    POSTGRAD = "POSTGRAD"
    NOTGIVEN = "NOTGIVEN"

    def __str__(self):
        return str(self.value)


class RegistrationQandA(BaseModel):
    uses: List[UseReason]
    school_level: Optional[SchoolLevel] = SchoolLevel.NOTGIVEN
    model_config = ConfigDict(validate_assignment=True, use_enum_values=True)


class AcctUpgradeQandA(BaseModel):
    uses: List[UseReason]
    more: Optional[str] = None
    model_config = ConfigDict(validate_assignment=True, use_enum_values=True)


class Questionnaire(BaseModel):
    name: QuestionnaireName
    q_and_a: Union[RegistrationQandA, AcctUpgradeQandA]
    model_config = ConfigDict(validate_assignment=True, use_enum_values=True)


class RegistrationQuestionnaire(Questionnaire):
    name: Literal[QuestionnaireName.REGISTRATION] = QuestionnaireName.REGISTRATION
    q_and_a: RegistrationQandA


class AcctUpgradeQuestionnaire(Questionnaire):
    name: Literal[QuestionnaireName.ACCT_UPGRADE] = QuestionnaireName.ACCT_UPGRADE
    q_and_a: AcctUpgradeQandA
