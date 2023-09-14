from readyocr.entities.bbox import BoundingBox
from readyocr.entities.page_entity import PageEntity


class Table(PageEntity):
    """
    To create a new :class:`Table` object we need the following

    :param id: Unique identifier of the Table entity.
    :type id: str
    :param confidence: value storing the confidence of detection out of 100.
    :type confidence: float
    :param title: title of the Table
    :type title: str
    :param bbox: Bounding box of the Table entity.
    :type bbox: BoundingBox
    :param page_number: page number of the Table
    :type page_number: int
    :param metadata: Optional information about the Table
    :type metadata: dict
    """

    def __init__(
        self,
        id: str,
        bbox: BoundingBox,
        title: str = "",
        confidence: float = 0,
        page_number: int = None,
        metadata: dict = None,
    ):
        super().__init__(
            id=id,
            bbox=bbox,
            page_number=page_number,
            metadata=metadata,
        )
        self._title = title
        self.confidence = confidence

    @property
    def title(self) -> str:
        """
        :return: Returns the title of the Table
        :rtype: str
        """
        return self._title

    @title.setter
    def title(self, title: str):
        """
        Sets the title of the Table

        :param title: title of the Table
        :type title: str
        """
        self._title = title

    def export_json(self):
        """
        :return: Returns the json representation of the cell
        :rtype: dict
        """
        response = super().export_json()
        if self._title:
            response["title"] = self._title
        response["confidence"] = self.confidence

        return response