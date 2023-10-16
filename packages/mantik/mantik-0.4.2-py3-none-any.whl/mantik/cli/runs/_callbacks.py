import typing as t

import click

T = t.TypeVar("T", bound=t.Type)


def cast_optional(type_: T) -> t.Callable[[str], t.Optional[T]]:
    """Create a function to cast an optional value.

    Returns
    -------
    Callable
        Casts an optional value to the given type.

    """

    def parse(ctx, param: str, value: str) -> type_:
        if value is None or value.lower() == "none":
            return None
        try:
            return type_(value)
        except ValueError:
            raise click.BadParameter(
                f"Invalid value for {param!r}: "
                f"'{value}' is not a valid {type_}."
            )

    return parse
