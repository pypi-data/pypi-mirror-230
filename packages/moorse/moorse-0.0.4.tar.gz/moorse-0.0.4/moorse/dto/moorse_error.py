class MoorseError:

    code: str = None
    message: str = None

    def __init__(self, data: dict[str, object]):

        if(data == None): return

        self.code = data.get('code')
        self.message = data.get('message')