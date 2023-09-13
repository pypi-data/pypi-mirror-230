from moorse.enums.webhook.webhook_method import WebhookMethod
from moorse.dto.webhook.response.webhook_header import WebhookHeader
from moorse.dto.webhook.response.webhook_integration import WebhookIntegration

class WebhookResponse:

    id: str = None
    client_id: str = None
    creation_date: str = None
    last_update_date: str = None

    name: str = None
    url: str = None
    method: WebhookMethod = None
    active: bool = None
    sended: bool = None
    received: bool = None
    readed: bool = None
    answered: bool = None
    retries: int = None
    timeout: int = None

    status_integration: bool = None

    headers: list[WebhookHeader] = []
    integrations: list[WebhookIntegration] = []

    def __init__(self, data: dict[str, object]):

        if(data == None): return

        self.id = data.get('id')
        self.client_id = data.get('clientId')
        self.creation_date = data.get('creationDate')
        self.last_update_date = data.get('lastUpdateDate')

        self.name = data.get('name')
        self.url = data.get('url')
        self.method = WebhookMethod(data.get('method').upper())
        self.active = data.get('active')
        self.sended = data.get('sended')
        self.received = data.get('received')
        self.readed = data.get('readed')
        self.answered = data.get('answered')
        self.retries = data.get('retries')
        self.timeout = data.get('timeout')

        self.headers = [WebhookHeader(header) for header in data.get('headers', [])]
        self.integrations = [WebhookIntegration(integration) for integration in data.get('integrations', [])]