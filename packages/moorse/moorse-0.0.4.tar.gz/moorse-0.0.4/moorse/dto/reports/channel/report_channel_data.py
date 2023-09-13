class ReportChannelData:

    whatsapp: int = None
    messenger: int = None
    instagram: int = None
    telegram: int = None
    sms: int = None
    email: int = None

    def __init__(self, data: dict[str, object]):

        if(data == None): return

        self.whatsapp = data.get('whatsapp')
        self.messenger = data.get('messenger')
        self.instagram = data.get('instagram')
        self.telegram = data.get('telegram')
        self.sms = data.get('sms')
        self.email = data.get('email')