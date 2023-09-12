import pytest
from ecs.owned_entity import OwnedEntity
from ecs.essentials import add, update


@pytest.fixture
def pairs_system():
    class PairsSystem(OwnedEntity):
        ecs_targets = dict(
            first=[],
            second=[],
            container=[],
        )

        ecs_requirements = dict(
            first={'name'},
            second={'name'},
            container={'pairs'},
        )

        def process(self, first, second, container):
            container.pairs.append("{} & {}".format(first.name, second.name))

    return PairsSystem()


class TestAdd:
    def test_adds_targets(self, pairs_system):
        entities = [
            OwnedEntity(name='OwnedEntity1'),
            OwnedEntity(name='OwnedEntity2', something='123'),
            OwnedEntity(name_='OwnedEntity3'),
        ]

        for e in entities:
            add(pairs_system, e)

        assert set(pairs_system.ecs_targets['first'])  == set(entities[:2])
        assert set(pairs_system.ecs_targets['second']) == set(entities[:2])

    def test_is_repetition_safe(self, pairs_system):
        e = OwnedEntity(name='OwnedEntity1')

        add(pairs_system, e)
        add(pairs_system, e)

        assert len(pairs_system.ecs_targets['first']) == 1
        assert len(pairs_system.ecs_targets['second']) == 1


class TestUpdate:
    def test_bruteforces_entities(self, pairs_system):
        npcs = [
            OwnedEntity(name='Eric'),
            OwnedEntity(name='Red'),
            OwnedEntity(name='Kitty'),
        ]

        container = OwnedEntity(pairs=[])

        pairs_system.ecs_targets['first'] += npcs
        pairs_system.ecs_targets['second'] += npcs
        pairs_system.ecs_targets['container'] += [container]

        update(pairs_system)

        assert set(container.pairs) == {
            'Eric & Eric',  'Eric & Red',  'Eric & Kitty',
            'Red & Eric',   'Red & Red',   'Red & Kitty',
            'Kitty & Eric', 'Kitty & Red', 'Kitty & Kitty',
        }
