from dto.template.component.template_component import TemplateComponent
from dto.template.button.button import Button
from dto.template.component.template_component_example import TemplateComponentExample
from enums.template.component.template_component_type import TemplateComponentType

class TemplateButtonComponent(TemplateComponent):

    def __init__(
        self,
        buttons: list[Button],
        example: TemplateComponentExample = None
    ):
        super().__init__(
            type = TemplateComponentType.BUTTONS,
            text = None,
            format = None,
            example = example,
            buttons = buttons
        )