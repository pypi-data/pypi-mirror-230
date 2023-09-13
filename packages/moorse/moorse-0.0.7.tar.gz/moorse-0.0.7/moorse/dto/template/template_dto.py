from moorse.dto.template.response.single.template_response import TemplateResponse
from moorse.dto.moorse_error import MoorseError

class TemplateDto:

    data: TemplateResponse
    errors: list[MoorseError]

    def __init__(self, data: dict[str, object]):
            
        if(data == None or not isinstance(data, dict)): return

        self.data = TemplateResponse(data.get("data"))
        self.errors = data.get("errors")
