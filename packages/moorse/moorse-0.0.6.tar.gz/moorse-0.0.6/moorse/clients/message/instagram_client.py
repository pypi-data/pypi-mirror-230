import requests
from enums.url import URL
from dto.message.message_sent_response import MessageSentResponse

class InstagramClient:

    def send_text(self, token: str, integration_id: str, to: str, body: str):
        response = requests.post(
            URL.INSTAGRAM_TEXT_MESSAGE.value.format(integration_id),
            json = {'to': to, 'body': body},
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return MessageSentResponse(response)