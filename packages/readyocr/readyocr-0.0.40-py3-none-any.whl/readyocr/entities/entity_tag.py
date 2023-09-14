

class EntityTag(set):
    """
    Creates a set tag object, initially empty but extended with the set passed in objs.

    :param tags: Custom set of tags.
    :type tags: set
    """

    def __init__(self, objs=None):
        super().__init__()

        if objs is None:
            objs = set()
        elif isinstance(objs, list):
            objs = set(objs)
        elif not isinstance(objs, set):
            objs = set([objs])

        self.update(objs)

    def has(self, tags) -> bool:
        """
        Checks if the tag object has the input tag/s.

        :param tags: Tag/s to check for.
        :type tags: str or list
        :return: Returns True if the tag object has the input tag/s, else False.
        :rtype: bool
        """

        if isinstance(tags, list):
            return all([x in self for x in tags])
        elif isinstance(tags, str):
            return tags in self
        else:
            assert False, "Invalid type for tags"

    def __repr__(self):
        return ",".join(self)
