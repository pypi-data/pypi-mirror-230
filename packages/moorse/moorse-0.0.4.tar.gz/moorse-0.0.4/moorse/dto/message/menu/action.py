from dto.message.menu.section import Section

class Action:

    sections: list[Section]

    def __init__(self, sections: list[Section]):
        self.sections = sections

    def to_json(self):
        return {
            'sections': [section.to_json() for section in self.sections]
        }