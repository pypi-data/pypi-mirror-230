from pydantic import BaseModel

from switcore.ui.item import Item


class InfoCard(BaseModel):
    type: str = 'info_card'
    items: list[Item]
    action_id: str
    draggable: bool = False
