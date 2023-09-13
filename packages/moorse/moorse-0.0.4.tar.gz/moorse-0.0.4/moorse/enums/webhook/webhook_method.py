from enum import Enum

class WebhookMethod(Enum):
    POST: str = "POST"
    GET: str = "GET"