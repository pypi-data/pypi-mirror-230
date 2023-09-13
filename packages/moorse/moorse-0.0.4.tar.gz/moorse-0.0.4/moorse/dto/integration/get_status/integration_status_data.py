from dto.moorse_error import MoorseError
from dto.integration.get_status.integration_status import IntegrationStatus

class IntegrationStatusData:

    data: IntegrationStatus = None
    errors: list[MoorseError] = []

    def __init__(self, data: dict[str, object]):

        if(data == None): return

        self.data = IntegrationStatus(data.get('data'))
        self.errors = [MoorseError(error) for error in data.get('errors')]