from enums.communication_channel import CommunicationChannel
from service.auth_service import AuthService
from service.webhook_service import WebhookService
from service.report_service import ReportService
from service.billing_service import BillingService
from service.message.whatsapp_service import WhatsappService
from service.message.instagram_service import InstagramService
from service.message.sms_service import SmsService
from service.integration_service import IntegrationService
from service.template_service import TemplateService
from dto.message.menu.menu_message_request import MenuMessageRequest
from dto.message.buttons.buttons_message_request import ButtonsMessageRequest
from dto.message.template.template_message_request import TemplateMessageRequest
from dto.message.message_sent_response import MessageSentResponse

class Moorse:

    auth: AuthService
    webhook: WebhookService
    report: ReportService
    billing: BillingService
    template: TemplateService
    integration: IntegrationService
    __message_sender: object

    channel: CommunicationChannel

    def __init__(self, email: str, password: str, channel: CommunicationChannel):

        self.auth = AuthService(email, password)
        self.webhook = WebhookService(self.auth)
        self.report = ReportService(self.auth)
        self.billing = BillingService(self.auth)
        self.template = TemplateService(self.auth)
        self.integration = IntegrationService(self.auth)
        self.channel = channel

        if(channel.value == CommunicationChannel.WHATSAPP.value):
            self.__message_sender = WhatsappService(self.auth)
        if(channel.value == CommunicationChannel.INSTAGRAM.value):
            self.__message_sender = InstagramService(self.auth)
        if(channel.value == CommunicationChannel.SMS.value):
            self.__message_sender = SmsService(self.auth)

    def send_text(self, to: str, body: str, integration_id: str) -> MessageSentResponse:
        return self.__message_sender.send_text(to, body, integration_id)
    
    def send_file(self, to: str, body: str, filename: str, integration_id: str, caption: str = None) -> MessageSentResponse:
        return self.__message_sender.send_file(to, body, filename, integration_id, caption)
    
    def send_list_menu(self, menu: MenuMessageRequest, integration_id: str) -> MessageSentResponse:
        return self.__message_sender.send_list_menu(menu, integration_id)
    
    def send_buttons(self, buttons: ButtonsMessageRequest, integration_id: str) -> MessageSentResponse:
        return self.__message_sender.send_buttons(buttons, integration_id)
    
    def send_template(self, template: TemplateMessageRequest, integration_id: str) -> MessageSentResponse:
        return self.__message_sender.send_template(template, integration_id)