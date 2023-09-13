from dto.message.buttons.button import Button

class ButtonsMessageRequest:

    to: str
    title: str
    buttons: list[Button]

    def __init__(self, to: str, title: str, buttons: list[Button]):
        self.to = to
        self.title = title
        self.buttons = buttons

    def to_json(self):
        return {
            'to': self.to,
            'title': self.title,
            'buttonsId': [button.to_json() for button in self.buttons],
        }