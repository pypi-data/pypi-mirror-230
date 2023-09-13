from dto.message.template.component import Component

class TemplateMessageRequest:

    to: str
    template_name: str
    components: list[Component]

    def __init__(self, to: str, template_name: str, components: list[Component]):
        self.to = to
        self.template_name = template_name
        self.components = components

    def to_json(self):
        return {
            'to': self.to,
            'template_name': self.template_name,
            'components': [component.to_json() for component in self.components]
        }