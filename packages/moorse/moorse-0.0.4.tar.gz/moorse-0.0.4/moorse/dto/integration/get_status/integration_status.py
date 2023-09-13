class IntegrationStatus:

    status: str = None

    def __init__(self, data: dict[str, object]):
        
        if(data == None): return
    
        self.status = data.get('status')