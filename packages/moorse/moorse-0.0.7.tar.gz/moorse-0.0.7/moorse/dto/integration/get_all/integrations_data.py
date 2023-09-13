from moorse.dto.moorse_error import MoorseError
from moorse.dto.integration.get_all.integrations_content import IntegrationsContent

class IntegrationsData:

    data: IntegrationsContent = None
    errors: list[MoorseError] = []

    def __init__(self, data: dict[str, object]):
        if(data == None): return
        self.data = IntegrationsContent(data.get('data'))
        self.errors = [MoorseError(error) for error in data['errors']]