from ecs.metasystem import Metasystem
from ecs.system import create_system
from ecs.owned_entity import OwnedEntity


def test_works():
    processed_entities = []

    metasystem = Metasystem()

    class system(OwnedEntity):
        ecs_targets = dict(
            entity=[]
        )

        ecs_requirements = dict(
            entity={'name'}
        )

        def process(self, entity):
            processed_entities.append(entity.name)

    system = system()

    for e in [
        system,
        OwnedEntity(name="Hyde"),
        OwnedEntity(name="Jackie"),
    ]:
        metasystem.add(e)

    metasystem.update()

    assert set(processed_entities) == {"Hyde", "Jackie"}


def test_dynamic_distribution():
    processed_entities = []

    ms = Metasystem()

    @ms.add
    @create_system
    def test_system(entity: "name_"):
        processed_entities.append(entity.name_)

    e = ms.create()

    e.name_ = 'Mike'
    ms.update()
    assert processed_entities == ['Mike']

    del e.name_
    ms.update()
    assert processed_entities == ['Mike']


def test_yield():
    ms = Metasystem()

    @ms.add
    @create_system
    def wait_for_condition(e: 'flag'):
        while not e.flag: yield
        e.success = True

    @ms.add
    @create_system
    def activate_flag(e: 'flag'):
        e.flag = True

    entities = [ms.create(flag=False, success=False) for _ in range(10)]

    ms.update()
    print(entities)
    assert all(not e.success for e in entities)

    ms.update()
    assert all(e.success for e in entities)
