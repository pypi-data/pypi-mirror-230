from moorse.dto.integration.get_all.integrations_data_attributes import IntegrationsDataAttributes

class IntegrationsContent:

    content: list[IntegrationsDataAttributes] = []

    def __init__(self, data: dict[str, object]):
        if(data == None): return
        self.content = [IntegrationsDataAttributes(content) for content in data.get('content')]