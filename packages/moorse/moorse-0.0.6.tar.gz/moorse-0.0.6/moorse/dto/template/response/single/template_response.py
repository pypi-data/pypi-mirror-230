from dto.template.request.template_request import TemplateRequest
from dto.template.component.template_component import TemplateComponent
from dto.template.button.button import Button
from enums.template.component.template_component_format import TemplateComponentFormat
from enums.template.template_type import TemplateType
from enums.template.template_language import TemplateLanguage
from enums.template.template_category import TemplateCategory
from enums.template.button_type import ButtonType
import json

class TemplateResponse(TemplateRequest):

    id: str = None
    creation_date: str = None
    last_update_date: str = None
    client_id: str = None
    status: str = None
    rejected_reason: str = None
    template_fb: str = None

    def __init__(self, data: dict[str, object]):
        
        if(data == None or not isinstance(data, dict)): return

        self.id = data.get("id")
        self.creation_date = data.get("creationDate")
        self.last_update_date = data.get("lastUpdateDate")
        self.client_id = data.get("clientId")
        self.status = data.get("status")
        self.rejected_reason = data.get("rejectedReason")
        self.template_fb = data.get("templateFb")

        super().__init__(
            data.get("name"),
            data.get("description"),
            TemplateType(data.get("type")) if data.get("type") != None else None,
            data.get("integrationId"),
            TemplateCategory(data.get("category")) if data.get("category") != None else None,
            TemplateLanguage(data.get("language")) if data.get("language") != None else None,
            self.__getComponentsList(data.get("components"))
        )

    def __getComponentsList(self, components: list[dict[str, object]]) -> list[TemplateComponent]:
        
        if(components == None or not isinstance(components, list)): return None
        
        answer: list[TemplateComponent] = []

        for comp in components:
            if(comp == None or not isinstance(comp, dict)): continue
            answer.append(TemplateComponent(
                comp.get("type"),
                comp.get("text"),
                TemplateComponentFormat(comp.get("format")),
                None,
                self.__getButtonList(comp.get("buttons"))
            ))

    def __getButtonList(self, buttons: list[dict[str, object]]) -> list[Button]:
        
        if(buttons == None or not isinstance(buttons, list)): return None
        
        answer: list[Button] = []

        for button in buttons:
            if(button == None or not isinstance(button, dict)): continue
            answer.append(Button(
                ButtonType(button.get("type")),
                button.get("text"),
                button.get("url"),
                button.get("phoneNumber"),
                None
            ))

        return answer