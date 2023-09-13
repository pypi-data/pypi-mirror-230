from moorse.dto.template.component.template_component import TemplateComponent
from moorse.dto.template.component.template_component_example import TemplateComponentExample
from moorse.enums.template.component.template_component_format import TemplateComponentFormat
from moorse.enums.template.component.template_component_type import TemplateComponentType

class TemplateDocumentComponent(TemplateComponent):

    def __init__(
        self,
        type: TemplateComponentType,
        example: TemplateComponentExample = None
    ):
        super().__init__(
            type = type,
            text = None,
            format = TemplateComponentFormat.DOCUMENT,
            example = example,
            buttons = None
        )