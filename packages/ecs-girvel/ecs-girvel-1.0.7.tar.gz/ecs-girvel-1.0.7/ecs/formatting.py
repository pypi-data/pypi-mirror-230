from . import entity


def pretty(x, max_length=50):
    if isinstance(x, entity.Entity):
        return ('name' in x
            and short(x.name)
            or f"<Entity l={len(x)}>"
        )

    if any(isinstance(x, primitive) for primitive in [int, float, str]):
        return short(repr(x))

    return f"<{short(type(x).__name__)}>"


def short(string, max_length=50):
    string = str(string)
    if len(string) > max_length:
        string = string[:max_length - 3] + "..."
    return string