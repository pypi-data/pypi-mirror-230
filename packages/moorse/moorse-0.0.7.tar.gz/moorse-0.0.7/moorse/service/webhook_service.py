from moorse.service.auth_service import AuthService
from moorse.clients.webhook_client import WebhookClient
from moorse.dto.webhook.webhook_request import WebhookRequest

class WebhookService:

    __auth: AuthService

    def __init__(self, auth: AuthService):
        self.__auth = auth

    def create(self, webhook: WebhookRequest):
        return WebhookClient().create(self.__auth.get_token(), webhook)

    def get_all(self):
        return WebhookClient().getAll(self.__auth.get_token())

    def get_one(self, webhook_id: str):
        return WebhookClient().getOne(self.__auth.get_token(), webhook_id)
    
    def update(self, webhook_id: str, webhook: WebhookRequest):
        return WebhookClient().update(self.__auth.get_token(), webhook_id, webhook)
    
    def delete(self, webhook_id: str):
        return WebhookClient().delete(self.__auth.get_token(), webhook_id)