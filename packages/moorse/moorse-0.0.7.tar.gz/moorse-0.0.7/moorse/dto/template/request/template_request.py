from moorse.enums.template.template_type import TemplateType
from moorse.enums.template.template_language import TemplateLanguage
from moorse.enums.template.template_category import TemplateCategory
from moorse.dto.template.component.template_component import TemplateComponent

class TemplateRequest:

    name: str = None
    description: str = None
    type: TemplateType = None
    integration_id: str = None
    category: TemplateCategory = None
    language: TemplateLanguage = None
    components: list[TemplateComponent] = []

    def __init__(
        self,
        name: str,
        description: str,
        type: TemplateType,
        integration_id: str,
        category: TemplateCategory,
        language: TemplateLanguage,
        components: list[TemplateComponent]
    ):
        self.name = name
        self.description = description
        self.type = type
        self.integration_id = integration_id
        self.category = category
        self.language = language
        self.components = components

    def to_json(self):
        return {
            'name': self.name,
            'description': self.description,
            'type': self.type.value,
            'integrationId': self.integration_id,
            'category': self.category.value,
            'language': self.language.value,
            'components': [component.to_json() for component in self.components]
        }