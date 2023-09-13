import requests
from enums.url import URL
from dto.integration.delete.integration_deletion_data import IntegrationDeletionData
from dto.integration.get_one.integration_data import IntegrationData
from dto.integration.get_all.integrations_data import IntegrationsData
from dto.integration.get_status.integration_status_data import IntegrationStatusData
import json

class IntegrationClient:

    def delete(self, token: str, integration_id: str) -> IntegrationDeletionData:
        response = requests.delete(
            URL.SEARCH_INTEGRATION.value.format(integration_id),
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return IntegrationDeletionData(response)
    
    def get_one(self, token: str, integration_id: str) -> IntegrationData:
        response = requests.get(
            URL.SEARCH_INTEGRATION.value.format(integration_id),
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return IntegrationData(response)
    
    def get_all(self, token: str) -> IntegrationsData:
        response = requests.get(
            URL.INTEGRATION.value,
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return IntegrationsData(response)
    
    def get_status(self, token: str, integration_id: str) -> IntegrationStatusData:
        response = requests.get(
            URL.SEARCH_INTEGRATION_STATUS.value.format(integration_id),
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return IntegrationStatusData(response)