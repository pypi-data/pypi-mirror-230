import os
from typing import List

from readyocr.entities.field import Field, LineItemGroup


class Invoice:
    def __init__(
        self,
        fields: List[Field],
        line_item_groups: List[LineItemGroup],
        page_numbers: List[int],
    ):
        self._fields = fields
        self._line_item_groups = line_item_groups
        self.page_numbers = page_numbers
        self.metadata = {}

    @property
    def fields(self):
        return self._fields

    @fields.setter
    def fields(self, fields: List[Field]):
        self._fields = fields

    @property
    def line_item_groups(self):
        return self._line_item_groups

    @line_item_groups.setter
    def line_item_groups(self, line_item_groups: List[LineItemGroup]):
        self._line_item_groups = line_item_groups

    def __repr__(self):
        return os.linesep.join(
            [
                f"Invoice(fields: {len(self._fields)}, line_item_groups: {len(self._line_item_groups)}, page_numbers: {self.page_numbers})"
            ]
        )

    def export_json(self):
        return {
            "pageNumbers": self.page_numbers,
            "fields": [i.export_json() for i in self._fields],
            "lineItemGroups": [i.export_json() for i in self._line_item_groups],
        }
