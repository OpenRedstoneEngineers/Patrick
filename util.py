import typing

import discord
from discord.ext import commands


def process_relay_chat(bot, message) -> typing.Tuple[discord.Message, bool]:
    if message.channel.id == bot.config["channels"]["gamechat"]:
        match = bot.relay_regex.match(message.content)
        if match:
            author, content = match.groups()
            message.author = author
            message.content = content
            return message, True
    return message, False


async def get_custom_commands(bot) -> dict:
    return {row[0]: row[1] for row in await bot.database.get_commands()}


async def process_custom_command(bot, message) -> bool:
    commands = await get_custom_commands(bot)
    if message.content[1:] in commands:
        bot.logger.info(
            f"User '{message.author}' ran custom command '{message.content[1:]}'"
        )
        await message.channel.send(commands[message.content[1:]])
        return True
    return False

def is_staff():
    def predicate(ctx):
        return discord.utils.get(ctx.author.roles, id=ctx.bot.config["roles"]["staff"]) is not None
    return commands.check(predicate)

def is_admin():
    def predicate(ctx):
        return discord.utils.get(ctx.author.roles, id=ctx.bot.config["staff"]["admin"]) is not None
    return commands.check(predicate)
