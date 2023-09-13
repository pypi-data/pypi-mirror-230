from readyocr.entities.bbox import BoundingBox
from readyocr.entities.textbox import TextBox


class Key(TextBox):
    """
    To create a new :class:`Key` object we need the following

    :param id: Unique identifier of the Key entity.
    :type id: str
    :param text: Transcription of the Key object.
    :type text: str
    :param confidence: value storing the confidence of detection out of 100.
    :type confidence: float
    :param bbox: Bounding box of the Key entity.
    :type bbox: BoundingBox
    :param page_number: page number of the Key
    :type page_number: int
    :param metadata: Optional information about the Key
    :type metadata: dict
    """

    def __init__(
        self,
        id: str,
        text: str = "",
        confidence: float = 0,
        bbox: BoundingBox = None,
        page_number: int = None,
        metadata: dict = None,
    ):
        super().__init__(
            id=id,
            text=text,
            confidence=confidence,
            bbox=bbox,
            page_number=page_number,
            metadata=metadata
        )
        self.confidence = confidence

    def export_json(self):
        response = super().export_json()
        response['confidence'] = self.confidence
        
        return response
