from dto.reports.standard.messages_report_dto import MessagesReportDto
from dto.reports.channel.messages_by_channel_report_dto import MessagesByChannelReportDto
from dto.reports.timeline.messages_by_timeline_report_dto import MessagesByTimelineReportDto
from clients.report_client import ReportClient
from service.auth_service import AuthService

class ReportService:

    __auth: AuthService

    def __init__(self, auth):
        self.__auth = auth

    def get_messages(self, integration_id: str, begin: str, end: str) -> MessagesReportDto:
        return ReportClient().get_messages(
            self.__auth.get_token(), begin, end
        )
    
    def get_messages_by_channel(self, integration_id: str, begin: str, end: str) -> MessagesByChannelReportDto:
        return ReportClient().get_messages_by_channel(
            self.__auth.get_token(), begin, end
        )
    
    def get_messages_by_timeline(self, integration_id: str, begin: str, end: str) -> MessagesByTimelineReportDto:
        return ReportClient().get_messages_by_timeline(
            self.__auth.get_token(), begin, end
        )