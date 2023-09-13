import numpy as np
from PIL import Image

from readyocr.entities.bbox import BoundingBox
from readyocr.entities.page_entity import PageEntity


class Image(PageEntity):
    """
    To create a new :class:`Image` object we need the following

    :param id: Unique identifier of the TextBox entity.
    :type id: str
    :param image: Image of the TextBox entity.
    :type image: Image
    :param bbox: Bounding box of the TextBox entity.
    :type bbox: BoundingBox
    :param page_number: page number of the TextBox
    :type page_number: int
    :param metadata: Optional information about the TextBox
    :type metadata: dict
    """

    def __init__(
        self,
        id: str,
        image: Image = None,
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
        self.image = image
        self.confidence = confidence

    def export_json(self):
        response = super().export_json()
        response['confidence'] = self.confidence
        
        return response
