from readyocr.entities.bbox import BoundingBox
from readyocr.entities.textbox import TextBox


class Cell(TextBox):
    """
    To create a new :class:`Cell` object we need the following

    :param id: Unique identifier of the Cell entity.
    :type id: str
    :param bbox: Bounding box of the Cell entity.
    :type bbox: BoundingBox
    :param text: Transcription of the Cell object.
    :type text: str
    :param confidence: value storing the confidence of detection out of 100.
    :type confidence: float
    """

    def __init__(
        self,
        id: str,
        row_index: int,
        col_index: int,
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
        self._row_index: int = int(row_index)
        self._col_index: int = int(col_index)

    @property
    def row_index(self) -> int:
        """
        :return: Returns the row index of the cell
        :rtype: int
        """
        return self._row_index

    @row_index.setter
    def row_index(self, row_index: int):
        """
        Sets the row index of the cell

        :param row_index: Row index of the cell
        :type row_index: int
        """
        self._row_index = int(row_index)

    @property
    def col_index(self) -> int:
        """
        :return: Returns the column index of the cell
        :rtype: int
        """
        return self._col_index

    @col_index.setter
    def col_index(self, col_index: int):
        """
        Sets the column index of the cell

        :param col_index: Column index of the cell
        :type col_index: int
        """
        self._col_index = int(col_index)

    def export_json(self):
        """
        :return: Returns the json representation of the cell
        :rtype: dict
        """
        response = super().export_json()
        response["rowIndex"] = self.row_index
        response["columnIndex"] = self.col_index

        return response
