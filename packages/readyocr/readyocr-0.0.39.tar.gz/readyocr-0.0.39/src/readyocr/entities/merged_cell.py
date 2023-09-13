from readyocr.entities.bbox import BoundingBox
from readyocr.entities.cell import Cell


class MergedCell(Cell):
    """
    To create a new :class:`MergedCell` object we need the following

    :param id: Unique identifier of the MergedCell entity.
    :type id: str
    :param bbox: Bounding box of the MergedCell entity.
    :type bbox: BoundingBox
    :param text: Transcription of the MergedCell object.
    :type text: str
    :param confidence: value storing the confidence of detection out of 100.
    :type confidence: float
    """

    def __init__(
        self,
        id: str,
        row_index: int,
        col_index: int,
        row_span: int,
        col_span: int,
        text: str = "",
        confidence: float = 0,
        bbox: BoundingBox = None,
        page_number: int = None,
        metadata: dict = None,
    ):
        # super().__init__(id, bbox, row_index, col_index, text, confidence, metadata)
        super().__init__(
            id=id,
            row_index=row_index,
            col_index=col_index,
            text=text,
            confidence=confidence,
            bbox=bbox,
            page_number=page_number,
            metadata=metadata
        )
        self._row_span: int = int(row_span)
        self._col_span: int = int(col_span)

    @property
    def row_span(self) -> int:
        """
        :return: Returns the row span of the MergedCell
        :rtype: int
        """
        return self._row_span

    @row_span.setter
    def row_span(self, row_span: int):
        """
        Sets the row span of the MergedCell

        :param row_span: Row span of the MergedCell
        :type row_span: int
        """
        self._row_span = int(row_span)

    @property
    def col_span(self) -> int:
        """
        :return: Returns the column span of the MergedCell
        :rtype: int
        """
        return self._col_span

    @col_span.setter
    def col_span(self, col_span: int):
        """
        Sets the column span of the MergedCell

        :param col_span: Column span of the MergedCell
        :type col_span: int
        """
        self._col_span = int(col_span)

    def export_json(self):
        """
        :return: Returns the json representation of the merged cell
        :rtype: dict
        """
        response = super().export_json()
        response["rowSpan"] = self.row_span
        response["columnSpan"] = self.col_span

        return response
