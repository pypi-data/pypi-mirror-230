class WebhookIntegration:

    id: str = None
    client_id: str = None
    creation_date: str = None
    last_update_date: str = None

    name: str = None
    description: str = None
    account_name: str = None

    def __init__(self, data: dict[str, object]):

        if(data == None): return

        self.id = data.get('id')
        self.client_id = data.get('clientId')
        self.creation_date = data.get('creationDate')
        self.last_update_date = data.get('lastUpdateDate')

        self.name = data.get('name')
        self.description = data.get('description')
        self.account_name = data.get('accountName')