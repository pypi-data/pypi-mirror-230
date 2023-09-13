from dto.template.component.template_component import TemplateComponent
from dto.template.component.template_component_example import TemplateComponentExample
from enums.template.component.template_component_format import TemplateComponentFormat
from enums.template.component.template_component_type import TemplateComponentType

class TemplateTextComponent(TemplateComponent):

    def __init__(
        self,
        type: TemplateComponentType,
        text: str,
        example: TemplateComponentExample = None
    ):
        super().__init__(
            type = type,
            text = text,
            format = TemplateComponentFormat.TEXT,
            example = example,
            buttons = None
        )