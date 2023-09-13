from moorse.dto.webhook.response.multiple.webhook_list import WebhookList
from moorse.dto.webhook.response.webhook_dto import WebhookDto
from moorse.dto.webhook.webhook_request import WebhookRequest
from moorse.enums.url import URL
import requests
import json

class WebhookClient:

    def create(self, token: str, webhook: WebhookRequest) -> WebhookDto:
        response = requests.post(
            URL.WEBHOOK.value, 
            json = webhook.to_json(),
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return WebhookDto(response)

    def update(self, token: str, webhook_id: str, webhook: WebhookRequest) -> WebhookDto:
        response = requests.put(
            URL.SEARCH_WEBHOOK.value.format(webhook_id), 
            json = webhook.to_json(),
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return WebhookDto(response)
    
    def delete(self, token: str, webhook_id: str) -> WebhookDto:
        response = None
        try:
            response = requests.delete(
                URL.SEARCH_WEBHOOK.value.format(webhook_id),
                headers = {'Authorization': f"Bearer {token}"}
            ).json()
        except: response = { 'data': None, 'errors': [] }
        return WebhookDto(response)

    def getOne(self, token: str, webhook_id: str) -> WebhookDto:
        response = requests.get(
            URL.SEARCH_WEBHOOK.value.format(webhook_id), 
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return WebhookDto(response)

    def getAll(self, token: str) -> WebhookList:
        response = requests.get(
            URL.WEBHOOK.value, 
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return WebhookList(response)
