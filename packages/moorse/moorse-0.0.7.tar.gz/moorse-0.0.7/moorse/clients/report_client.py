from moorse.dto.reports.standard.messages_report_dto import MessagesReportDto
from moorse.dto.reports.channel.messages_by_channel_report_dto import MessagesByChannelReportDto
from moorse.dto.reports.timeline.messages_by_timeline_report_dto import MessagesByTimelineReportDto
from moorse.enums.url import URL
import requests
import json

class ReportClient:

    def get_messages(self, token: str, begin: str, end: str) -> MessagesReportDto:
        response = requests.get(
            URL.REPORT.value.format(begin, end),
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return MessagesReportDto(response)
    
    def get_messages_by_channel(self, token: str, begin: str, end: str) -> MessagesByChannelReportDto:
        response = requests.get(
            URL.REPORT_BY_CHANNEL.value.format(begin, end),
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return MessagesByChannelReportDto(response)
    
    def get_messages_by_timeline(self, token: str, begin: str, end: str) -> MessagesByTimelineReportDto:
        response = requests.get(
            URL.REPORT_BY_TIMELINE.value.format(begin, end),
            headers = {'Authorization': f"Bearer {token}"}
        ).json()
        return MessagesByTimelineReportDto(response)