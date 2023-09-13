from dto.integration.get_one.integration_data_attributes import IntegrationDataAttributes
from dto.moorse_error import MoorseError

class IntegrationData:

    data: IntegrationDataAttributes = None
    errors: list[MoorseError] = []

    def __init__(self, data: dict[str, object]):

        if(data == None): return

        self.data = IntegrationDataAttributes(data.get('data'))
        self.errors = [MoorseError(error) for error in data.get('errors')]

