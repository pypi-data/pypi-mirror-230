class WebhookHeader:

    id: str = None
    client_id: str = None
    creation_date: str = None
    last_update_date: str = None
    key: str = None
    value: str = None

    def __init__(self, data: dict[str, object]):

        if(data == None): return

        self.id = data.get('id')
        self.client_id = data.get('clientId')
        self.creation_date = data.get('creationDate')
        self.last_update_date = data.get('lastUpdateDate')
        self.key = data.get('key')
        self.value = data.get('value')