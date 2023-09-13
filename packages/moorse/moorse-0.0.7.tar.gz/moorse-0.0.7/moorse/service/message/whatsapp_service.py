from moorse.service.auth_service import AuthService
from moorse.clients.message.whatsapp_client import WhatsappClient
from moorse.dto.message.message_sent_response import MessageSentResponse
from moorse.dto.message.menu.menu_message_request import MenuMessageRequest
from moorse.dto.message.buttons.buttons_message_request import ButtonsMessageRequest
from moorse.dto.message.template.template_message_request import TemplateMessageRequest

class WhatsappService:

    __auth: AuthService

    def __init__(self, auth: AuthService):
        self.__auth = auth
    
    def send_text(self, to: str, body: str, integration_id: str) -> MessageSentResponse:
        return WhatsappClient().send_text(self.__auth.get_token(), to, body, integration_id)
    
    def send_file(self, to: str, body: str, filename: str, integration_id: str, caption: str = None) -> MessageSentResponse:
        return WhatsappClient().send_file(self.__auth.get_token(), to, body, filename, integration_id, caption)
    
    def send_list_menu(self, menu: MenuMessageRequest, integration_id: str) -> MessageSentResponse:
        return WhatsappClient().send_list_menu(self.__auth.get_token(), menu, integration_id)
    
    def send_buttons(self, buttons: ButtonsMessageRequest, integration_id: str) -> MessageSentResponse:
        return WhatsappClient().send_buttons(self.__auth.get_token(), buttons, integration_id)
    
    def send_template(self, template: TemplateMessageRequest, integration_id: str) -> MessageSentResponse:
        return WhatsappClient().send_template(self.__auth.get_token(), template, integration_id)