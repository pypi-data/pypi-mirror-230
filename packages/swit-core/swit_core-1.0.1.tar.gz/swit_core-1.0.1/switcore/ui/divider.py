from pydantic import BaseModel


class Divider(BaseModel):
    type: str = "divider"
