from moorse.dto.billing.billing_data import BillingData

class BillingDto:

    data: BillingData = None
    errors: list[str] = []

    def __init__(self, data: dict[str, object]):

        if(data == None): return
        
        self.data = BillingData(data.get('data'))
        self.errors = data.get('errors')