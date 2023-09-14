import statistics
from collections.abc import Iterable
from copy import deepcopy
from typing import List


def sort_by_position(entities: List) -> List:
    return sorted(entities, key=lambda e: (e.bbox.y + e.bbox.height, e.bbox.x))
