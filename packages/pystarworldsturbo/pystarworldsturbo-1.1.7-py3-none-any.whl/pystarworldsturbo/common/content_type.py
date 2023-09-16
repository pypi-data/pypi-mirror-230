from __future__ import annotations
from typing import TypeAlias


MessageContentSimpleType: TypeAlias = int | float | str | bool
MessageContentType: TypeAlias = MessageContentSimpleType | bytes | list["MessageContentType"] | dict[MessageContentSimpleType, "MessageContentType"]
