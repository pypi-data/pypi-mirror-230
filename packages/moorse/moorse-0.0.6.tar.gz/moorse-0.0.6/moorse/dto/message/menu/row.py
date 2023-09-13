class Row:

    id: str
    title: str

    def __init__(self, id: str, title: str):
        self.id = id
        self.title = title

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title
        }