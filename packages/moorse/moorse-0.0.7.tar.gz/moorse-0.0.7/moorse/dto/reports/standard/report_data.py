class ReportData:

    total_messages_sent: int = None
    total_messages_received: int = None
    total_contacts: int = None

    def __init__(self, data: dict[str, object]):

        if(data == None): return

        self.total_messages_sent = data.get('totalMessageSent')
        self.total_messages_received = data.get('totalMessagesReceived')
        self.total_contacts = data.get('totalContacts')