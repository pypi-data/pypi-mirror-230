from pydantic import BaseModel

from switcore.ui.button import Button


class ContextMenuItem(BaseModel):
    label: str
    action_id: str


class Header(BaseModel):
    title: str
    subtitle: str | None
    context_menu: list[ContextMenuItem] | None
    buttons: list[Button] | None


class AttachmentHeader(BaseModel):
    title: str
    subtitle: str | None
    app_id: str
