import os
from typing import Any, List, Set, Type, Union

T = Type["PageEntity"]


class EntityList(List[T]):
    """
    Creates a list type object, initially empty but extended with the list passed in objs.

    :param initial_entities: Custom list of objects.
    :type initial_entities: list entity
    """

    def __init__(self, initial_entities: Union[T, List[T], Set[T]] = None):
        super().__init__()
        if initial_entities is None:
            initial_entities = set()
        elif isinstance(initial_entities, list):
            initial_entities = set(initial_entities)
        elif not isinstance(initial_entities, set):
            initial_entities = set([initial_entities])

        self._entities = list(initial_entities)

    def add(self, *args, **kwargs):
        # not allow direct add method
        raise NotImplementedError("Not allow direct add method")

    def remove(self, *args, **kwargs):
        # not allow direct remove method
        raise NotImplementedError("Not allow direct add method")

    def pop(self, *args, **kwargs):
        # not allow direct pop method
        raise NotImplementedError("Not allow direct add method")

    def __add__(self, entity: T):
        if entity not in self._entities:
            self._entities.append(entity)

    def __remove__(self, entity: T):
        if entity in self._entities:
            self._entities.remove(entity)

    def __pop__(self, index: int):
        self._entities.pop(index)

    def __contains__(self, item):
        return item in self._entities

    def __iter__(self):
        return iter(self._entities)

    def __len__(self):
        return len(self._entities)

    def __repr__(self):
        return os.linesep.join([str(x) for x in self])

    def __getitem__(self, index):
        return self._entities[index]

    def filter_by_class(self, entity_type: type) -> "EntityList[T]":
        """
        Filters the list of entities by class type.
        """
        return EntityList([x for x in self if isinstance(x, entity_type)])

    def filter_by_attr(self, attr: str, value: Any) -> "EntityList[T]":
        """
        Filters the list of entities by attribute value.
        """
        return EntityList(
            [x for x in self if hasattr(x, attr) and getattr(x, attr) == value]
        )

    def filter_by_tags(self, tags: Union[str, List[str]]) -> "EntityList[T]":
        """
        Filters the list of entities by tags. tags could be a list of tags or a single tag.
        """
        if isinstance(tags, str):
            tags = [tags]
        return EntityList([x for x in self if x.tags.intersection(tags)])

    def get_all_tags(self) -> List[str]:
        """
        Gets a list of all tags.
        """
        tags = []
        for entity in self:
            tags.extend(entity.tags)
        return list(set(tags))
