from moorse.dto.reports.standard.report_data import ReportData
from moorse.dto.moorse_error import MoorseError

class MessagesReportDto:

    data: ReportData = None
    errors: list[MoorseError] = []

    def __init__(self, data: dict[str, object]):

        if(data == None): return

        self.data = ReportData(data.get('data'))
        self.errors = [MoorseError(error) for error in data.get('errors')]