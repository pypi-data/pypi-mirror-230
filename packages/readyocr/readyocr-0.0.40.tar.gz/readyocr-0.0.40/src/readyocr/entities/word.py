from readyocr.entities.bbox import BoundingBox
from readyocr.entities.textbox import TextBox


class Word(TextBox):
    """
    To create a new :class:`Word` object we need the following

    :param id: Unique identifier of the Word entity.
    :type id: str
    :param text: Transcription of the Word object.
    :type text: str
    :param confidence: value storing the confidence of detection out of 100.
    :type confidence: float
    :param bbox: Bounding box of the Word entity.
    :type bbox: BoundingBox
    :param page_number: page number of the Word
    :type page_number: int
    :param metadata: Optional information about the Word
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