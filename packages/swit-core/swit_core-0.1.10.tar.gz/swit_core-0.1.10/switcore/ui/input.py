from enum import Enum

from pydantic import BaseModel


class InputVariant(str, Enum):
    text = 'text'
    select = 'select'


class Input(BaseModel):
    type: str = 'text_input'
    action_id: str
    placeholder: str | None
    trigger_on_input: bool = False
    value: str | None
    variant: InputVariant = InputVariant.text
