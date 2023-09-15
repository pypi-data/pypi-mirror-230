from configcronos.core.entities import Segment
from configcronos.core.repositories import SegmentRepository


class SegmentService:

    def __init__(self, segment_repository: SegmentRepository):
        self.segment_repository = segment_repository

    def get_segments(self):

        response = self.segment_repository.get_segments()

        data = response['data'][0]

        segmento = Segment(data['tipo_segmento'], data['regra'])

        return segmento
