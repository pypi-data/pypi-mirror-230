from typing import TypeVar

from .owned_entity import OwnedEntity, OwnershipException
from .system import create_system
from .essentials import update, register_attribute, unregister_attribute


class Metasystem:
    """Facade for a metasystem and all interactions with the game."""

    def __init__(self):
        """Initializes a new game; creates a metasystem."""
        def metasystem(system: 'process, ecs_requirements, ecs_targets'):
            update(system)

        self._metasystem = create_system(metasystem)

    def create(self, **attributes) -> OwnedEntity:
        """Creates in-game entity.

        Args:
            **attributes: attributes (components) that entity will contain

        Returns:
            In-game entity
        """
        return self.add(OwnedEntity(**attributes))

    T = TypeVar("T")
    def add(self, entity: T, **attributes) -> T:
        """Adds an entity to the metasystem; adds __metasystem__ attribute.

        Args:
            entity: entity to be added

        Returns:
            The same entity
        """

        for name, value in attributes.items():
            entity[name] = value

        if '__metasystem__' in entity:
            raise OwnershipException(
                "Entity {entity} is already belongs to a metasystem"
            )

        entity.__metasystem__ = self._metasystem

        for attribute, _ in entity:
            register_attribute(self._metasystem, entity, attribute)

        return entity

    def delete(self, entity: OwnedEntity) -> None:
        """Removes entity from the game.

        Args:
            entity: in-game entity to be removed
        """
        assert "__metasystem__" in entity, "Entity should belong to the metasystem to be deleted from it"
        unregister_attribute(self._metasystem, entity)

    def update(self) -> None:
        """Updates all the systems once."""
        update(self._metasystem)
