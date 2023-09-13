class IntegrationDeletionMessage:

    message: str = None

    def __init__(self, data: dict[str, object]):
        if(data == None): return
        self.message = data['message']