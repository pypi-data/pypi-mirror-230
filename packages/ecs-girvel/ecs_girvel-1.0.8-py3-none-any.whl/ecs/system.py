import inspect

from .owned_entity import OwnedEntity


def create_system(protosystem) -> OwnedEntity:
    """Creates system from an annotated function

    Args:
        protosystem: function annotated in ECS style

    Returns:
        New entity with `process`, `ecs_targets` and `ecs_requirements` fields
    """

    result = OwnedEntity(
        name=protosystem.__name__,
        process=protosystem,
        ecs_targets={
            member_name: [] for member_name in protosystem.__annotations__
        },
        ecs_requirements={
            member_name: set(annotation.split(', '))
            for member_name, annotation
            in protosystem.__annotations__.items()
        }
    )

    if inspect.isgeneratorfunction(protosystem):
        result.ecs_generators = {}

    return result
