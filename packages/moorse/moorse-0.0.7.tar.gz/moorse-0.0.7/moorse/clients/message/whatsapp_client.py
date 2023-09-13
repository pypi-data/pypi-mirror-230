import requests
from moorse.enums.url import URL
from moorse.dto.message.message_sent_response import MessageSentResponse
from moorse.dto.message.menu.menu_message_request import MenuMessageRequest
from moorse.dto.message.buttons.buttons_message_request import ButtonsMessageRequest
from moorse.dto.message.template.template_message_request import TemplateMessageRequest

class WhatsappClient:

    def send_text(self, token: str, to: str, body: str, integration_id: str) -> MessageSentResponse:
        response = requests.post(
            URL.WHATSAPP_TEXT_MESSAGE.value.format(integration_id), 
            json = {'to': to, 'body': body},
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return MessageSentResponse(response)

    def send_file(self, token: str, to: str, body: str, filename: str, integration_id: str, caption: str = None) -> MessageSentResponse:
        response = requests.post(
            URL.WHATSAPP_FILE_MESSAGE.value.format(integration_id),
            json = {'to': to, 'body': body, 'filename': filename, 'caption': caption},
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return MessageSentResponse(response) 

    def send_list_menu(self, token: str, menu: MenuMessageRequest, integration_id: str) -> MessageSentResponse:
        response = requests.post(
            URL.WHATSAPP_LIST_MENU_MESSAGE.value.format(integration_id),
            json = menu.to_json(),
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return MessageSentResponse(response)

    def send_buttons(self, token: str, buttons: ButtonsMessageRequest, integration_id: str) -> MessageSentResponse:
        response = requests.post(
            URL.WHATSAPP_BUTTONS_MESSAGE.value.format(integration_id),
            json = buttons.to_json(),
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return MessageSentResponse(response)

    def send_template(self, token: str, template: TemplateMessageRequest, integration_id: str) -> MessageSentResponse:
        response = requests.post(
            URL.WHATSAPP_TEMPLATE_MESSAGE.value.format(integration_id),
            json = template.to_json(),
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return MessageSentResponse(response)