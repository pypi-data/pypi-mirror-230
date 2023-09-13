class BillingData:

    integration_id: str = None
    balance: int = None
    credit: int = None
    channel: str = None
    billing_type: str = None

    def __init__(self, data: dict[str, object]):
        
        if(data == None): return
        
        self.integration_id = data.get('integrationId')
        self.balance = data.get('balance')
        self.credit = data.get('credit')
        self.channel = data.get('channel')
        self.billing_type = data.get('billingType')