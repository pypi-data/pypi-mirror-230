from pydantic import BaseModel

from switcore.ui.Icon import Icon
from switcore.ui.button import Button


class IntegratedService(BaseModel):
    icon: Icon


class SignInPage(BaseModel):
    id: str | None = None
    type: str = "sign_in_page"
    integrated_service: IntegratedService
    title: str
    description: str
    button: Button
