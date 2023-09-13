from dto.message.template.parameter.parameter import Parameter

class Component:

    type: str
    parameters: list[Parameter]

    def __init__(self, type: str, parameters: list[Parameter]):
        self.type = type
        self.parameters = parameters

    def to_json(self):
        return {
            "type": self.type,
            "parameters": [parameter.to_json() for parameter in self.parameters]
        }