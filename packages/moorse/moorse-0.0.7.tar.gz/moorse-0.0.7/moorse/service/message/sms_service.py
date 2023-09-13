from moorse.service.auth_service import AuthService
from moorse.clients.message.sms_client import SmsClient
from moorse.dto.message.message_sent_response import MessageSentResponse
from moorse.dto.message.menu.menu_message_request import MenuMessageRequest
from moorse.dto.message.buttons.buttons_message_request import ButtonsMessageRequest
from moorse.dto.message.template.template_message_request import TemplateMessageRequest

class SmsService:

    __auth: AuthService

    def __init__(self, auth: AuthService):
        self.__auth = auth
    
    def send_text(self, to: str, body: str, integration_id: str) -> MessageSentResponse:
        return SmsClient().send_text(self.__auth.get_token(), integration_id, to, body)
    
    def send_file(self, to: str, body: str, filename: str, integration_id: str, caption: str = None) -> MessageSentResponse:
        raise NotImplementedError("SMS does not support file messages")
    
    def send_list_menu(self, menu: MenuMessageRequest, integration_id: str) -> MessageSentResponse:
        return NotImplementedError("SMS does not support list menu messages")
    
    def send_buttons(self, buttons: ButtonsMessageRequest, integration_id: str) -> MessageSentResponse:
        return NotImplementedError("SMS does not support buttons messages")
    
    def send_template(self, template: TemplateMessageRequest, integration_id: str) -> MessageSentResponse:
        return NotImplementedError("SMS does not support template messages")