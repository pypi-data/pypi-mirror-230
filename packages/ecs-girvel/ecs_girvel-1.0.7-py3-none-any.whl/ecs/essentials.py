from __future__ import annotations

import inspect
from . import owned_entity as oe


def add(system: oe.OwnedEntity, entity: oe.OwnedEntity):
    """Tries to register entity as a system target.

    Succeeds if entity has all the required fields to be a target for the
    system (they are listed in system.ecs_requirements[target_name]). Success
    means that the next iteration of the system will use entity one or multiple
    times.
    """

    assert all(hasattr(system, a) for a in (
        'process', 'ecs_targets', 'ecs_requirements'
    ))

    for member_name, requirements in system.ecs_requirements.items():
        if all(p in entity for p in requirements):
            targets = system.ecs_targets[member_name]
            if entity not in targets:
                targets.append(entity)


def remove(system: oe.OwnedEntity, entity: oe.OwnedEntity):
    """Tries to unregister entity from a system.

    Guarantees that the entity will no longer be processed by the system.
    """

    for targets in system.ecs_targets.values():
        if entity in targets:
            targets.remove(entity)


def update(system: oe.OwnedEntity):
    """Launches a system one time.

    Calls a system.process with each possible combination of targets.
    """

    keys = list(system.ecs_targets.keys())

    def _update(members):
        i = len(members)
        if i == len(keys):
            if inspect.isgeneratorfunction(system.process):
                tuple_members = tuple(members.values())
                if tuple_members not in system.ecs_generators:
                    system.ecs_generators[tuple_members] \
                        = system.process(**members)

                try:
                    next(system.ecs_generators[tuple_members])
                except StopIteration:
                    del system.ecs_generators[tuple_members]
            else:
                system.process(**members)
            return

        if len(system.ecs_targets[keys[i]]) > 0:
            for target in system.ecs_targets[keys[i]].copy():
                members[keys[i]] = target
                _update(members)

            del members[keys[i]]

    return _update({})


def register_attribute(
    metasystem: oe.OwnedEntity, entity: oe.OwnedEntity, attribute: str
):
    """Notifies systems that the entity gained new attribute.

    Args:
        metasystem: metasystem itself, not a facade
        entity: entity that gained new attribute
        attribute: name of the attribute
    """

    add(metasystem, entity)
    for system in metasystem.ecs_targets["system"]:
        if any(attribute in r for r in system.ecs_requirements.values()):
            add(system, entity)

    return entity


def unregister_attribute(
    metasystem: oe.OwnedEntity, entity: oe.OwnedEntity, attribute: str = None
):
    """Notifies systems that entity lost an attribute or that entity itself
    should be deleted.

    Args:
        metasystem: metasystem itself, not a facade
        entity: entity that lost an attribute or should be deleted
        attribute: name of the attribute or None if entity itself should be
            deleted
    """

    systems = [metasystem, *metasystem.ecs_targets["system"]]

    if attribute is None:
        del entity.__metasystem__
    else:
        systems = [
            s for s in systems
            if any(
                attribute in r for r in s.ecs_requirements.values()
            )
        ]

    for system in systems:
        remove(system, entity)

    return entity
