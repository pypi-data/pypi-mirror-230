import dataclasses
import typing

from discord import context


__all__: list[str] = [
    "Command",
]


@dataclasses.dataclass
class Command:
    name: str
    description: str
    callback: typing.Callable[[context.Context, ...], typing.Awaitable[typing.Any]]
