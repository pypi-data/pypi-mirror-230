from moorse.enums.template.button_type import ButtonType

class Button:

    type: ButtonType = None
    text: str = None
    url: str = None
    phone_number: str = None
    example: list[str] = None

    def __init__(
        self, 
        type: ButtonType, 
        text: str, 
        url: str, 
        phone_number: str, 
        example: list[str] = None
    ):
        self.type = type
        self.text = text
        self.url = url
        self.phone_number = phone_number
        self.example = example
    
    def to_json(self) -> dict:
        return {
            "type": self.type.value,
            "text": self.text,
            "url": self.url,
            "phoneNumber": self.phone_number,
            "example": self.example
        }