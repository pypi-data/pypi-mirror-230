from ecs.system import create_system


def test_creation():
    def protosystem(subject: "attribute1"):
        pass

    system = create_system(protosystem)

    assert system.process is protosystem
    assert system.ecs_targets is not None
