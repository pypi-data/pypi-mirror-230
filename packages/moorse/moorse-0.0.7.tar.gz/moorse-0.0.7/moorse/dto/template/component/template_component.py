from moorse.enums.template.component.template_component_type import TemplateComponentType
from moorse.enums.template.component.template_component_format import TemplateComponentFormat
from moorse.dto.template.component.template_component_example import TemplateComponentExample
from moorse.dto.template.button.button import Button

class TemplateComponent:

    type: TemplateComponentType = None
    text: str = None
    format: TemplateComponentFormat = None
    example: TemplateComponentExample = None
    buttons: list[Button] = None

    def __init__(
        self,
        type: TemplateComponentType,
        text: str,
        format: TemplateComponentFormat,
        example: TemplateComponentExample = None,
        buttons: list[Button] = None
    ):
        self.type = type
        self.text = text
        self.format = format
        self.example = example
        self.buttons = buttons

    def to_json(self):
        return {
            'type': self.type.value,
            'text': self.text,
            'format': self.format.value if self.type.value == TemplateComponentType.HEADER.value else None,
            'example': self.example.to_json() if self.example else None,
            'buttons': [button.to_json() for button in self.buttons] if isinstance(self.buttons, list) else None
        }