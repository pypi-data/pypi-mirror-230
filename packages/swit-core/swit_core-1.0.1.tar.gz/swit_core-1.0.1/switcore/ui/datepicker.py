from pydantic import BaseModel


class DatePicker(BaseModel):
    type: str = "datepicker"
    action_id: str
    placeholder: str | None
    trigger_on_input: bool = False
    value: str | None
