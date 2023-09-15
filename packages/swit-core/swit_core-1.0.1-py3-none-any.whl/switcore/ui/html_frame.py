from pydantic import BaseModel


class HtmlFrame(BaseModel):
    type: str = 'html_frame'
    html_content: str
