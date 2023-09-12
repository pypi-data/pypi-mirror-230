from ecs.entity import Entity


def test_is_anonymous_object():
    entity = Entity(
        name='custom-entity',
        some_parameter=42,
    )

    assert entity.name == 'custom-entity'
    assert entity.some_parameter == 42


def test_attribute_is_item():
    entity = Entity()

    entity['first_field'] = 1
    entity.second_field = 2
    entity['Third field'] = 3

    assert entity.first_field == 1
    assert entity['second_field'] == 2
    assert entity['Third field'] == 3
    assert 'Third field' in entity


def test_get_attribute_with_default_value():
    assert Entity()['a', 1] == 1


def test_converts_to_dict():
    assert dict(Entity(a=1, b=2)) == {'a': 1, 'b': 2}


def test_is_iterable():
    assert list(Entity(a=1, b=2)) == [('a', 1), ('b', 2)]


def test_len():
    assert len(Entity(a=1, b=2)) == 2


def test_repr():
    print(repr(Entity(a=1)))