from pydantic import BaseModel

from switcore.ui.select_item import SelectItem


class Tabs(BaseModel):
    """
        An element representing an array of tabs.
    """
    type: str = "tabs"
    tabs: list[SelectItem]
    value: str
