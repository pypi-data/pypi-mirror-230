from pydantic import BaseModel


class Icon(BaseModel):
    type: str
    image_url: str
    alt: str
