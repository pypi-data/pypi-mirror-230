from moorse.dto.message.menu.action import Action

class MenuMessageRequest:

    to: str
    body: str
    action: Action

    def __init__(self, to: str, body: str, action: Action):
        self.to = to
        self.body = body
        self.action = action

    def to_json(self):
        return {
            'to': self.to,
            'body': self.body,
            'action': self.action.to_json()
        }