from moorse.dto.reports.timeline.date_message_counter import DateMessageCounter

class ReportTimelineData:

    total_send: int = None
    total_received: int = None
    send: list[DateMessageCounter] = []
    received: list[DateMessageCounter] = []

    def __init__(self, data: dict[str, object]):
        
        if(data == None): return
        
        self.total_send = data.get('totalSend')
        self.total_received = data.get('totalReceived')
        
        for i in data.get('send'):
            self.send.append(DateMessageCounter(i))
        
        for i in data.get('received'):
            self.received.append(DateMessageCounter(i))