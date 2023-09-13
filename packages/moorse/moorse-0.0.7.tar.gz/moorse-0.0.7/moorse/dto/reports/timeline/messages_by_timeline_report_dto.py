from moorse.dto.reports.timeline.report_timeline_data import ReportTimelineData
from moorse.dto.moorse_error import MoorseError

class MessagesByTimelineReportDto:

    data: ReportTimelineData = None
    errors: list[MoorseError] = []

    def __init__(self, data: dict[str, object]):
            
        if(data == None): return
        
        self.data = ReportTimelineData(data.get('data'))
        
        for i in data.get('errors'):
            self.errors.append(MoorseError(i))