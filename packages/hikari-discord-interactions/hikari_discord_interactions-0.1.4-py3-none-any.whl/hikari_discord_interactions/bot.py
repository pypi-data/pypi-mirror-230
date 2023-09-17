from __future__ import annotations

import typing

import hikari
from hikari import api
from hikari.impl import special_endpoints

from hikari_discord_interactions import command, context


__all__: list[str] = [
    "Bot",
]


class Bot:
    def __init__(self, token: str, guild_id: int) -> None:
        self._rest_bot: hikari.RESTBot = hikari.RESTBot(token, hikari.TokenType.BOT)
        self._rest: api.RESTClient = self._rest_bot.rest
        self._guild_id = guild_id

        self._commands: [command.Command] = []

        self._rest_bot.set_listener(hikari.CommandInteraction, self._on_application_command)
        self._rest_bot.add_startup_callback(self._on_start)

    async def _on_start(self, _: hikari.RESTBot) -> None:
        application: hikari.Application = await self._rest.fetch_application()

        for cmd in self._commands:
            await self._rest.create_slash_command(application, cmd.name, cmd.description, guild=self._guild_id)

    async def _handle_response(self, interaction: hikari.CommandInteraction, response: typing.Any) -> special_endpoints.InteractionMessageBuilder:
        return interaction.build_response().set_content(response)

    async def _on_application_command(self, interaction: hikari.CommandInteraction) -> special_endpoints.InteractionMessageBuilder | None:
        if interaction.command_type == hikari.CommandType.SLASH:
            for cmd in self._commands:
                if cmd.name == interaction.command_name:
                    response = await cmd.callback(context.Context(interaction, self._rest))
                    return await self._handle_response(interaction, response)

        return None

    def command(self, name: str, description: str) -> typing.Callable[[], None]:
        def inner(callback: typing.Callable[[context.Context, ...], typing.Awaitable[typing.Any]]) -> None:
            self. _commands.append(command.Command(name, description, callback))

        return inner

    def run(self):
        self._rest_bot.run()
