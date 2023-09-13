from moorse.enums.webhook.webhook_method import WebhookMethod
from moorse.dto.pair import Pair

class WebhookRequest:

    name: str
    url: str
    method: WebhookMethod
    active: bool
    integrations: list[str]
    headers: list[Pair]
    
    answered: bool
    received: bool
    sent: bool
    retries: int
    timeout: int

    def __init__(
        self, 
        name: str, 
        url: str, 
        method: WebhookMethod, 
        active: bool, 
        integrations: list[str], 
        headers: list[Pair],
        answered: bool,
        received: bool,
        sent: bool,
        retries: int,
        timeout: int
    ):
        self.name = name
        self.url = url
        self.method = method
        self.active = active
        self.integrations = integrations
        self.headers = headers
        self.answered = answered
        self.received = received
        self.sent = sent
        self.retries = retries
        self.timeout = timeout

    def to_json(self):

        headers_list = []
        for header in self.headers:
            headers_list.append({
                "key": header.key, 
                "value": header.value
            })

        return {
            'name': self.name,
            'url': self.url,
            'method': self.method.value,
            'active': self.active,
            'integrations': self.integrations,
            'headers': headers_list,
            'answered': self.answered,
            'received': self.received,
            'sent': self.sent,
            'retries': self.retries,
            'timeout': self.timeout
        }