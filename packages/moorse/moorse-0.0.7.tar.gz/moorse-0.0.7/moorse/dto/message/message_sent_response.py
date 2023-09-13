from moorse.dto.message.message_sent_response_data import MessageSentResponseData

class MessageSentResponse:

    data: MessageSentResponseData = None
    errors: list[str] = []

    def __init__(self, data: dict[str, object]):
        if(data == None or not isinstance(data, dict)): return
        self.data = MessageSentResponseData(data.get('data'))
        self.errors = data.get('errors')