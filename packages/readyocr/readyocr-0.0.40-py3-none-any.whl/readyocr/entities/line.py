from readyocr.entities.bbox import BoundingBox
from readyocr.entities.textbox import TextBox


class Line(TextBox):
    """
    To create a new :class:`Line` object we need the following

    :param id: Unique identifier of the Line entity.
    :type id: str
    :param text: Transcription of the Line object.
    :type text: str
    :param confidence: value storing the confidence of detection out of 100.
    :type confidence: float
    :param bbox: Bounding box of the Line entity.
    :type bbox: BoundingBox
    :param page_number: page number of the Line
    :type page_number: int
    :param metadata: Optional information about the Line
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