from configcronos.core.entities import Phase3
from configcronos.core.repositories import Phase3Repository


class Phase3Service:

    def __init__(self, phase3_repository: Phase3Repository) -> None:
        self.phase3_repository = phase3_repository

    def get_phase3(self) -> Phase3:
        response = self.phase3_repository.get_phase3()
        data = response['data'][0]
        phase3 = Phase3.from_dict(data)
        return phase3
