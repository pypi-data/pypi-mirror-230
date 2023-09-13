class MessageSentResponseData:

    control: str
    creation_date: str
    message: str

    def __init__(self, data: dict[str, object]):
        if(data == None or not isinstance(data, dict)): return
        self.control = data.get('control')
        self.creation_date = data.get('creation_date')
        self.message = data.get('message')