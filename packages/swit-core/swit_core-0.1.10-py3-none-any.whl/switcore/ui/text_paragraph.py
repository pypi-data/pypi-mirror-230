from enum import Enum

from pydantic import BaseModel, validator


class TextParagraphColorTypes(str, Enum):
    gray900 = "gray900"
    gray800 = "gray800"
    gray700 = "gray700"


class TextParagraphSizeTypes(str, Enum):
    medium = "medium"
    large = "large"


class TextParagraphStyle(BaseModel):
    bold: bool = False
    color: TextParagraphColorTypes = TextParagraphColorTypes.gray900
    size: TextParagraphSizeTypes = TextParagraphSizeTypes.medium
    max_lines: int = 0

    @validator('max_lines', pre=True, always=True)
    def check_max_lines(cls, v):
        if v < 0 or v > 2:
            raise ValueError('max_lines must be between 0 and 2 inclusive.')
        return v


class TextParagraph(BaseModel):
    type: str = "text"
    markdown: bool = False
    content: str
    style: TextParagraphStyle | None = None
