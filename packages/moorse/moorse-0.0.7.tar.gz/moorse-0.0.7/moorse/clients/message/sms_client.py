import requests
from moorse.enums.url import URL
from moorse.dto.message.message_sent_response import MessageSentResponse

class SmsClient:

    def send_text(self, token: str, integration_id: str, to: str, body: str):
        response = requests.post(
            URL.SMS_TEXT_MESSAGE.value.format(integration_id),
            json = {'to': to, 'body': body},
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return MessageSentResponse(response)