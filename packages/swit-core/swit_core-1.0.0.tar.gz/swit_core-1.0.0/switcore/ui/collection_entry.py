from enum import Enum

from pydantic import BaseModel

from switcore.ui.element_components import SubText, Tag, StaticAction
from switcore.ui.image import Image
from switcore.ui.text_paragraph import TextParagraph


class TextStyle(BaseModel):
    bold: bool = False
    color: str
    size: str
    max_lines: int


class BackgroundType(str, Enum):
    none = "none"
    lightblue = "lightblue"


class Background(BaseModel):
    color: BackgroundType = BackgroundType.none


class MetadataItem(BaseModel):
    type: str
    content: str | None
    style: dict | None
    image_url: str | None


class TextSection(BaseModel):
    text: TextParagraph
    metadata_items: list[SubText | Image | Tag] | None


class VerticalAlignmentTypes(str, Enum):
    top = "top"
    middle = "middle"
    bottom = "bottom"


class CollectionEntry(BaseModel):
    type: str = "collection_entry"
    start_section: Image | None
    text_sections: list[TextSection]
    vertical_alignment: VerticalAlignmentTypes = VerticalAlignmentTypes.top
    background: Background | None
    action_id: str | None
    static_action: StaticAction | None
    draggable: bool = False
