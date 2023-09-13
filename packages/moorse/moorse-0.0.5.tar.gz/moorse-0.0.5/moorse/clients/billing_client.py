from dto.billing.billing_dto import BillingDto
from dto.moorse_error import MoorseError
from enums.url import URL
import requests
import json

class BillingClient:

    def get_credits(self, token: str, integration_id: str):
        response = requests.get(
            URL.BILLING.value.format(integration_id),
            headers = {'Authorization': f"Bearer {token}"}
        )
        try:
            response = response.json()
        except:
            response = {
                "data": None, 
                "errors": ["Integração não encontrada"]
            }
        return BillingDto(response)