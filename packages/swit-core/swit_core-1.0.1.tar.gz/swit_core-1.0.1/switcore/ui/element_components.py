from enum import Enum

from pydantic import BaseModel


class StyleColorTypes(str, Enum):
    primary = "primary"
    secondary = "secondary"
    danger = "danger"


class StyleShapeTypes(str, Enum):
    rectangular = "rectangular"
    rounded = "rounded"


class Style(BaseModel):
    color: StyleColorTypes
    shape: StyleShapeTypes


class Tag(BaseModel):
    type: str = "tag"
    content: str
    style: Style | None = None


class SubText(BaseModel):
    type: str = "subtext"
    content: str


class OpenOauthPopup(BaseModel):
    action_type: str = "open_oauth_popup"
    link_url: str


class OpenLink(BaseModel):
    action_type: str = "open_link"
    link_url: str


class CloseView(BaseModel):
    action_type: str = "close_view"


class WriteToClipboard(BaseModel):
    action_type: str = "write_to_clipboard"
    content: str


StaticAction = OpenOauthPopup | OpenLink | WriteToClipboard | CloseView
