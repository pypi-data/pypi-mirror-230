from service.auth_service import AuthService
from clients.template_client import TemplateClient
from dto.template.request.template_request import TemplateRequest
from dto.template.template_dto import TemplateDto
from dto.template.response.multiple.template_list import TemplateList

class TemplateService:

    __auth: AuthService

    def __init__(self, auth: AuthService):
        self.__auth = auth

    def create(self, webhook: TemplateRequest) -> TemplateDto:
        return TemplateClient().create(self.__auth.get_token(), webhook)

    def get_all(self) -> TemplateList:
        return TemplateClient().get_all(self.__auth.get_token())

    def get_one(self, webhook_id: str) -> TemplateDto:
        return TemplateClient().get_one(self.__auth.get_token(), webhook_id)
    
    def delete(self, webhook_id: str) -> TemplateDto:
        return TemplateClient().delete(self.__auth.get_token(), webhook_id)