from enums.url import URL
from dto.authorization.login_response import LoginResponse
import requests
import json

class AuthClient:

    def login(self, email: str, password: str) -> LoginResponse:
        data: dict[str, str] = { 'login': email, 'senha': password }
        response = requests.post(URL.AUTH_LOGIN.value, json=data).json()
        return LoginResponse(response)
