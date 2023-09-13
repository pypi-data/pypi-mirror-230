class IntegrationsDataAttributes:

    id: str = None
    name: str = None
    description: str = None
    account_name: str = None
    account_description: str = None
    type: str = None
    external_id: str = None
    trial: bool = None
    official: bool = None

    def __init__(self, data: dict[str, object]):

        if(data == None): return

        self.id = data.get('id')
        self.name = data.get('name')
        self.description = data.get('description')
        self.account_name = data.get('accountName')
        self.account_description = data.get('accountDescription')
        self.type = data.get('type')
        self.external_id = data.get('externalId')
        self.trial = data.get('trial')
        self.official = data.get('official')