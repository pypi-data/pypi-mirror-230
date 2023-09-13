from dto.message.menu.row import Row

class Section:

    title: str
    rows: list[Row]

    def __init__(self, title: str, rows: list[Row]):
        self.title = title
        self.rows = rows

    def to_json(self):
        return {
            "title": self.title,
            "rows": [row.to_json() for row in self.rows]
        }