from service.auth_service import AuthService
from dto.billing.billing_dto import BillingDto
from clients.billing_client import BillingClient

class BillingService:

    __auth: AuthService

    def __init__(self, auth: AuthService):
        self.__auth = auth

    def get_credits(self, integration_id: str) -> BillingDto:
        return BillingClient().get_credits(self.__auth.get_token(), integration_id)