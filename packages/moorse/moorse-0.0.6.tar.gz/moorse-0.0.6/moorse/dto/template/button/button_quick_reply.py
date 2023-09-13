from dto.template.button.button import Button
from enums.template.button_type import ButtonType

class ButtonQuickReply(Button):

    def __init__(
        self,
        text: str,
        example: list[str] = None
    ):
        super().__init__(
            ButtonType.QUICK_REPLY,
            text,
            None,
            None,
            example
        )