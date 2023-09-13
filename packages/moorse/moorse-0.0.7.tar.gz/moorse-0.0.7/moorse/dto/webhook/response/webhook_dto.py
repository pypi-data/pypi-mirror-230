from moorse.dto.webhook.response.webhook_response import WebhookResponse
from moorse.dto.moorse_error import MoorseError

class WebhookDto:

    data: WebhookResponse = None
    errors: list[MoorseError] = []

    def __init__(self, data: dict[str, object]):
        
        if(data == None): return

        self.data = WebhookResponse(data.get('data'))
        for error in data.get('errors'):
            self.errors.append(
                MoorseError(error)
            )