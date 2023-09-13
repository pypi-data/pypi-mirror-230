from dto.template.button.button import Button
from enums.template.button_type import ButtonType

class ButtonPhoneNumber(Button):

    def __init__(
        self,
        phone_number: str,
        example: list[str] = None
    ):
        super().__init__(
            ButtonType.PHONE_NUMBER,
            None,
            None,
            phone_number,
            example
        )