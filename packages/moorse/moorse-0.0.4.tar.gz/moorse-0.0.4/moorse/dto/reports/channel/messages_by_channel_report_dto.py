from dto.reports.channel.report_channel_data import ReportChannelData
from dto.moorse_error import MoorseError

class MessagesByChannelReportDto:

    data: ReportChannelData = None
    errors: list[MoorseError] = []

    def __init__(self, data: dict[str, object]):
        if(data == None): return
        self.data = ReportChannelData(data.get('data'))
        self.errors = [MoorseError(error) for error in data.get('errors')]