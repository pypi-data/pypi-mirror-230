from readyocr.entities.bbox import BoundingBox
from readyocr.entities.textbox import TextBox


class Value(TextBox):
    """
    To create a new :class:`Value` object we need the following

    :param id: Unique identifier of the Value entity.
    :type id: str
    :param text: Transcription of the Value object.
    :type text: str
    :param confidence: value storing the confidence of detection out of 100.
    :type confidence: float
    :param bbox: Bounding box of the Value entity.
    :type bbox: BoundingBox
    :param page_number: Page number in the document linked to this Value object
    :type page_number: int
    :param metadata: Optional information about the entity
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