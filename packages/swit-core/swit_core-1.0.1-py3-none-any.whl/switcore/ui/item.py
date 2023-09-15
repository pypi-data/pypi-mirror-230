from pydantic import BaseModel
from switcore.ui.text_paragraph import TextParagraph


class Item(BaseModel):
    label: str
    text: TextParagraph
