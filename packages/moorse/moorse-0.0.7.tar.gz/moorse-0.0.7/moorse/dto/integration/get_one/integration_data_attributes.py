from moorse.dto.webhook.response.webhook_response import WebhookResponse

class IntegrationDataAttributes:

    id: str = None
    name: str = None
    description: str = None
    account_name: str = None
    account_description: str = None
    type: str = None
    external_id: str = None
    moorse_management: bool = None
    billing_type: str = None
    device: str = None
    model: str = None
    battery: int = None
    state: str = None
    avatar: str = None
    phone_description: str = None
    trial: bool = None
    official: bool = None
    external_client_id: str = None
    external_channel_id: str = None
    webhooks: list[WebhookResponse] = []

    def __init__(self, data: dict[str, object]):

        if(data == None): return

        self.id = data.get('id')
        self.name = data.get('name')
        self.description = data.get('description')
        self.account_name = data.get('accountName')
        self.account_description = data.get('accountDescription')
        self.type = data.get('type')
        self.external_id = data.get('externalId')
        self.moorse_management = data.get('moorseManagement')
        self.billing_type = data.get('billingType')
        self.device = data.get('device')
        self.model = data.get('model')
        self.battery = data.get('battery')
        self.state = data.get('state')
        self.avatar = data.get('avatar')
        self.phone_description = data.get('phoneDescription')
        self.trial = data.get('trial')
        self.official = data.get('official')
        self.external_client_id = data.get('externalClientId')
        self.external_channel_id = data.get('externalChannelId')
        self.webhooks = [WebhookResponse(webhook) for webhook in data.get('webhooks')]