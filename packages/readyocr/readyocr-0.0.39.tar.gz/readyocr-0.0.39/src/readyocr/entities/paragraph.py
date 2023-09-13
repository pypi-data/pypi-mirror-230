from readyocr.entities.bbox import BoundingBox
from readyocr.entities.textbox import TextBox


class Paragraph(TextBox):
    """
    To create a new :class:`Paragraph` object we need the following

    :param id: Unique identifier of the Paragraph entity.
    :type id: str
    :param bbox: Bounding box of the Paragraph entity.
    :type bbox: BoundingBox
    :param text: Transcription of the Paragraph object.
    :type text: str
    :param confidence: value storing the confidence of detection out of 100.
    :type confidence: float
    """

    def __init__(
        self,
        id: str,
        bbox: BoundingBox,
        text: str = "",
        confidence: float = 0,
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