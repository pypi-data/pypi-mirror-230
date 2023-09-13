from clients.auth_client import AuthClient
from dto.authorization.login_response import LoginResponse
from service.validators.email_validator import EmailValidator

class AuthService:

    __email: str = None
    __password: str = None
    __token: str = None

    def __init__(self, email: str, password: str) -> None:
        self.__email = email
        self.__password = password

    def login(self) -> LoginResponse:

        if(self.__email == None or self.__password == None):
            raise Exception("Email and password must be set before log in!")
        
        response: LoginResponse = AuthClient().login(
            self.__email, 
            self.__password
        )

        self.__token = response.data

        return response

    def set_email(self, email: str) -> None:
        if(not EmailValidator().is_valid(email)): raise Exception("You are trying to set an invalid email!")
        self.__email = email

    def get_email(self) -> str:
        return self.__email
    
    def set_password(self, password: str) -> None:
        self.__password = password

    def get_password(self) -> str:
        return self.__password
    
    def set_token(self, token: str) -> None:
        self.__token = token

    def get_token(self) -> str:
        if(self.__token == None):
            raise Exception("Seems that you token is not set!\nTry to log in first or set the token manually!")
        return self.__token
