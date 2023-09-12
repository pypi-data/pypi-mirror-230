"""Ecs is an entity-component-system framework that manages the game cycle.

In this interpretation entities are dynamic objects, components are entities'
fields, and systems are functions that take entities as an argument and
brute-force through all their possible combinations. Also, there is a
metasystem, which is a system that launches other systems and is basically a
facade for all important interactions with the game.
"""

from .entity import Entity
from .owned_entity import OwnedEntity
from .metasystem import Metasystem
from .system import create_system

__all__ = [e.__name__ for e in [
  Entity, OwnedEntity, Metasystem, create_system,
]]
