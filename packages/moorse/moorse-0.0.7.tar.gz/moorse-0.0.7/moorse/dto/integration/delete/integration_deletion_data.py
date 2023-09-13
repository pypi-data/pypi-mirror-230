from moorse.dto.integration.delete.integration_deletion_message import IntegrationDeletionMessage
from moorse.dto.moorse_error import MoorseError

class IntegrationDeletionData:

    data: IntegrationDeletionMessage = None
    errors: list[MoorseError] = []

    def __init__(self, data: dict[str, object]):
        if(data == None): return
        self.data = IntegrationDeletionMessage(data['data'])
        self.errors = [MoorseError(error) for error in data['errors']]