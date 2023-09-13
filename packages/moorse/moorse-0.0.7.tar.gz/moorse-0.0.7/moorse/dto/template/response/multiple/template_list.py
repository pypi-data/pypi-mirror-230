from moorse.dto.template.response.multiple.template_list_content import TemplateListContent
from moorse.dto.moorse_error import MoorseError

class TemplateList:

    data: TemplateListContent = None
    errors: list[MoorseError] = []

    def __init__(self, data: dict[str, object]):
            
        if(data == None or not isinstance(data, dict)): return

        if(data.get("errors") == None): data["errors"] = []

        self.data = TemplateListContent(data.get("data"))
        self.errors = [MoorseError(error) for error in data.get("errors", [])]