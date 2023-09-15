from readyocr.entities.bbox import BoundingBox
from readyocr.entities.page_entity import PageEntity


class DrawRectangle(PageEntity):
    """
    To create a new :class:`DrawRectangle` object we need the following

    :param id: Unique identifier of the DrawRectangle entity.
    :type id: str
    :param bbox: Bounding box of the DrawRectangle entity.
    :type bbox: BoundingBox
    :param page_number: page number of the DrawRectangle
    :type page_number: int
    :param metadata: Metadata of the DrawRectangle entity.
    :type metadata: dict
    """

    def __init__(
        self,
        id: str,
        confidence: float = 0,
        bbox: BoundingBox = None,
        page_number: int = None,
        metadata: dict = None,
    ):
        super().__init__(
            id=id,
            bbox=bbox,
            page_number=page_number,
            metadata=metadata,
        )
        self.confidence = confidence

    def export_json(self):
        response = super().export_json()
        response['confidence'] = self.confidence
        
        return response