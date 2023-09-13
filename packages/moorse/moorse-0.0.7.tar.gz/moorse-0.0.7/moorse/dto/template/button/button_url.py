from moorse.dto.template.button.button import Button
from moorse.enums.template.button_type import ButtonType

class ButtonUrl(Button):

    def __init__(
        self,
        text: str,
        url: str,
        example: list[str] = None
    ):
        super().__init__(
            ButtonType.URL,
            text,
            url,
            None,
            example
        )