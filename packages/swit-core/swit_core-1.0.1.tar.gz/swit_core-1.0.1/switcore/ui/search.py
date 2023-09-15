from pydantic import BaseModel


class SearchInput(BaseModel):
    type: str = 'search_input'
    action_id: str
    placeholder: str | None
    value: str | None
    disabled: bool = False
