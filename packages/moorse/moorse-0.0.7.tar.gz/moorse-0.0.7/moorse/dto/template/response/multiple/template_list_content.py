from moorse.dto.template.response.single.template_response import TemplateResponse

class TemplateListContent:

    content: list[TemplateResponse] = []

    def __init__(self, data: dict[str, object]):
            
        if(data == None or not isinstance(data, dict)): return
        if(data.get("content") == None): data["content"] = []

        self.content = [TemplateResponse(template) for template in data.get("content")]