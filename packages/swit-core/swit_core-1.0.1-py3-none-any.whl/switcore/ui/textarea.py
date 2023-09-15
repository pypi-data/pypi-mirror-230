from enum import Enum

from pydantic import BaseModel


class TextareaSizeTypes(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"


class Textarea(BaseModel):
    type: str = "textarea"
    action_id: str
    placeholder: str | None
    value: str | None
    height: TextareaSizeTypes = TextareaSizeTypes.small
    disabled: bool = False
