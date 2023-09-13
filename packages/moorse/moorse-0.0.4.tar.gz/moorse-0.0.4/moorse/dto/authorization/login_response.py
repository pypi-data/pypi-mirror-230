import json

class LoginResponse:
    
    data: str
    errors: list[str]

    def __init__(self, data: dict[str, object]):
        self.data = data.get('data')
        self.errors = data.get('errors')