from readyocr.entities.entity_list import EntityList


class ChildrenMixin:
    @property
    def children(self) -> EntityList:
        """
        :return: Returns all the objects present in the Page.
        :rtype: EntityList
        """
        assert self not in self._children, "Recursive children is not allowed"
        return self._children

    @property
    def descendants(self) -> EntityList:
        """
        :return: Returns all the children of the entity.
        :rtype: EntityList
        """
        descendants = []
        for x in self.children:
            descendants.append(x)
            descendants.extend(x.descendants)

        return EntityList(descendants)

    def add(self, child) -> EntityList:
        """
        Adds a child to the entity.

        :param child: Child entity to be added
        :type child: PageEntity
        """
        # not allow add it self as child
        if child == self:
            raise ValueError("Cannot add child to itself")
        # check loop of children
        for x in child.descendants:
            if x == self:
                raise ValueError("Child cannot be added as it will create a loop")
        self._children.__add__(child)
        # children will have same page number as parent
        child.page_number = self.page_number
        # propagate the page number to all descendants
        for x in child.descendants:
            x.page_number = self.page_number

        return self._children

    def remove(self, child) -> EntityList:
        """
        Removes a child from the entity.

        :param child: Child entity to be removed
        :type child: PageEntity
        """
        # not allow remove it self as child
        if child == self:
            raise ValueError("Cannot remove child from itself")
        self._children.__remove__(child)
        return self._children

    def remove_descendant(self, descendant) -> EntityList:
        """
        Removes a descendant from the entity.

        :param descendant: Descendant entity to be removed
        :type descendant: PageEntity
        """
        # not allow remove it self as child
        if descendant == self:
            raise ValueError("Cannot remove descendant from itself")
        if descendant in self._children:
            self._children.__remove__(descendant)
        else:
            for child in self._children:
                child.remove_descendant(descendant)

        return self._children

    def pop(self, index: int) -> EntityList:
        """
        Removes a child from the entity.

        :param index: Index of the child entity to be removed
        :type index: int
        """
        self._children.__pop__(index)
        return self._children

    def find_parent_by_child_id(self, child_id: str) -> EntityList:
        """
        Find the parent of a child entity by its ID.

        :param child_id: ID of the child entity.
        :type child_id: str
        :return: Returns the parent entity of the child entity.
        :rtype: EntityList
        """
        parents = []
        for desc in self.descendants:
            child_ids = [x.id for x in desc.children]
            if child_id in child_ids:
                parents.append(desc)
        # remove mutual parents
        parents = list(set(parents))
        return EntityList(parents)
