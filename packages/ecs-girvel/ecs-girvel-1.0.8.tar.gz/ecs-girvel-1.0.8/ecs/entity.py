from .formatting import pretty


class Entity:
    """Entity is a mixture of dict and object.

    You can access attributes as items.
    """

    def __init__(self, **attributes):
        """
        Args:
            **attributes: entity's future attributes in format
        """
        for k, v in attributes.items():
            setattr(self, k, v)

    def __delitem__(self, key):
        """Deletes an attribute with the given name."""
        return delattr(self, key)

    def __getitem__(self, item):
        """Gets an attribute with the given name.

        Args:
            item: a name of the attribute or a tuple (name, default_value)

        Returns:
            Attribute value or default value if specified
        """
        if isinstance(item, tuple):
            return getattr(self, *item)

        return getattr(self, item)

    def __setitem__(self, item, value):
        """Sets an attribute with the given name."""
        return setattr(self, item, value)

    def __contains__(self, item):
        """Checks if entity contains an attribute with the given name."""
        return hasattr(self, item)

    def __len__(self):
        """Counts number of attributes inside the entity."""
        return len(list(self.__iter__()))

    def __repr__(self):
        name = self["name", None]

        return 'Entity{}({})'.format(
            name and f" '{name}'" or "",
            ', '.join(
                f'{key}={pretty(value)}'
                for key, value in self
                if key != 'name'
            )
        )

    def __iter__(self):
        """Iterates entity as pairs: (attribute_name, attribute_value)"""

        for attr_name in dir(self):
            if not attr_name.startswith('__') or not attr_name.endswith('__'):
                yield attr_name, getattr(self, attr_name)
