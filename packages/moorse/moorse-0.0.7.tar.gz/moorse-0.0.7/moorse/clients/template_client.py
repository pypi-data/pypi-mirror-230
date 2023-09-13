from moorse.dto.template.template_dto import TemplateDto
from moorse.dto.template.request.template_request import TemplateRequest
from moorse.dto.template.response.multiple.template_list import TemplateList
from moorse.enums.url import URL
import requests

class TemplateClient:

    def create(self, token: str, template: TemplateRequest) -> TemplateDto:
        response = requests.post(
            URL.TEMPLATE.value, 
            json = template.to_json(),
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return TemplateDto(response)
    
    def delete(self, token: str, template_id: str) -> TemplateDto:
        response = None
        try:
            response = requests.delete(
                URL.SEARCH_TEMPLATE.value.format(template_id),
                headers = {'Authorization': f"Bearer {token}"}
            ).json()
        except: response = { 'data': None, 'errors': [] }
        return TemplateDto(response)

    def get_one(self, token: str, template_id: str) -> TemplateDto:
        response = requests.get(
            URL.SEARCH_TEMPLATE.value.format(template_id), 
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return TemplateDto(response)

    def get_all(self, token: str) -> TemplateList:
        response = requests.get(
            URL.TEMPLATE.value, 
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return TemplateList(response)
