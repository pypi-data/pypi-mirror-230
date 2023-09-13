class DateMessageCounter:

    date: str = None
    total: int = None

    def __init__(self, data: dict[str, object]):
        if(data == None): return
        self.date = data.get('date')
        self.total = data.get('total')