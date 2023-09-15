from enum import Enum

from pydantic import BaseModel

from switcore.ui.element_components import Tag
from switcore.ui.image import Image
from switcore.ui.select_item import SelectItem


class Option(SelectItem):
    """
        https://devdocs.swit.io/docs/user-actions/ref/schemas/select
    """
    icon: Image | None = None
    tags: list[Tag] | None = None


class OptionGroup(BaseModel):
    label: str
    options: list[Option]


class SelectStyleTypes(str, Enum):
    filled = "filled"
    outlined = "outlined"
    ghost = "ghost"


class Style(BaseModel):
    variant: SelectStyleTypes = SelectStyleTypes.outlined


class SelectQuery(BaseModel):
    query_server: bool = True
    disabled: bool = False
    placeholder: str | None = None
    value: str | None = None
    action_id: str


class Select(BaseModel):
    type: str = 'select'
    placeholder: str | None
    multiselect: bool = False
    trigger_on_input: bool = False
    value: list[str] | None
    options: list[Option] = []
    option_groups: list[OptionGroup] = []
    style: Style | None = None
    query: SelectQuery | None = None
