from enum import Enum
from typing import Type


def enum_list(enum: Type[Enum]) -> list[str]:
    return [member.name.replace("_", " ").title() for member in enum]
