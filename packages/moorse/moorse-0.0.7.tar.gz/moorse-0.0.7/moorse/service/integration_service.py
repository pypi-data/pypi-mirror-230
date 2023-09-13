from moorse.service.auth_service import AuthService
from moorse.clients.integration_client import IntegrationClient

class IntegrationService:

    __auth: AuthService

    def __init__(self, auth: AuthService):
        self.__auth = auth

    def delete(self, integration_id: str):
        return IntegrationClient().delete(self.__auth.get_token(), integration_id)
    
    def get_one(self, integration_id: str):
        return IntegrationClient().get_one(self.__auth.get_token(), integration_id)
    
    def get_all(self):
        return IntegrationClient().get_all(self.__auth.get_token())
    
    def get_status(self, integration_id: str):
        return IntegrationClient().get_status(self.__auth.get_token(), integration_id)