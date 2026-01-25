import re
import typing
from random import choice
from copy import copy
from io import StringIO

import discord
from discord import app_commands
from discord.ext import commands


class NoRelayException(Exception):
    pass


class RelayMember(discord.Member):
    __slots__ = tuple()
    """A subclass of discord.Member to signify that the member is a relay member.
    The class holds no functionality, but is used to signify that the member is a relay member for permission checks.
    """


def return_or_truncate(text, max_length):
    """Takes a string and truncates it to a maximum length, adding ellipsis if truncated.
    If the string is shorter than the maximum length, it returns the original string.

    Args:
        text (str): The string to be truncated.
        max_length (int): The maximum length of the string before truncation.

    Returns:
        str: The original string if it's shorter than max_length, otherwise the truncated string with ellipsis.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def reformat_relay_chat(bot, message) -> typing.Optional[discord.Message]:
    """Takes a discord message and checks if it's a server relay message.
    If it is, it reformats the message to be processed as a command by the bot.
    It also changes the author of the message to a RelayMember object.
    This is done to prevent the bot from trying to process commands as itself.
    The message is then returned or None if it is not a relay message to signify that it's a regular chat message.

    Args:
        bot (commands.Bot): The bot instance.
        message (discord.Message): The message to be reformatted.

    Returns:
        discord.Message: The reformatted message if it is a relay message, otherwise None.
    """
    match = bot.relay_regex.match(message.content)
    if match:
        author_name, content = match.groups()
        message.author = copy(message.author)
        message.author.__class__ = RelayMember
        message.author.nick = author_name
        message.content = content
        return message
    return None


async def process_custom_command(bot, message) -> bool:
    """Take a message and check if it is a custom command. If it is, send a random response from the list of responses.
    If the command is not found, return False.

    Args:
        bot (commands.Bot): The bot instance.
        message (discord.Message): The message to check for a custom command.

    Returns:
        bool: True if the command was found and processed, False otherwise.
    """
    commands = bot.database.commands_cache
    for prefix in bot.command_prefix:
        if message.content.removeprefix(prefix) in commands:
            bot.logger.info(
                f"User '{message.author.display_name}' ran custom command '{message.content[1:]}'"
            )
            await message.channel.send(
                f"{message.author.display_name}: {choice(commands[message.content.removeprefix(prefix)])}"
            )
            await bot.database.add_command_history(
                message.author.display_name, message.content.removeprefix(prefix)
            )
            return True
    return False


def load_automod_regexes(bot):
    """A setup function that loads the automod regexes from the config file.
    This runs a re.compile on each regex to create a compiled regex object for performance.

    Args:
        bot (commands.Bot): The bot instance.
    """
    bot.automod_regexes = [re.compile(regex, flags=re.IGNORECASE) for regex in bot.config["automod_regexes"]]


def find_automod_matches(bot, message: discord.Message) -> list[str]:
    """Checks a message against the automod regexes to see if it matches any of them.

    Args:
        bot (commands.Bot): The bot instance.
        message (discord.Message): A discord message to check.

    Returns:
        list[str]: List of any matching regexes
    """
    return [regex.pattern for regex in bot.automod_regexes if regex.search(message.content)]


def is_staff():
    """A decorator that adds a commands.Check to a command to check if the user is a staff member.
    It checks if the user has the staff role in the config file. If they do, it returns True.
    If the user is a RelayMember, it returns False as well.
    If they don't, it raises a MissingPermissions error.
    """

    def predicate(ctx):
        if (
            not isinstance(ctx.author, discord.User)
            and not isinstance(ctx.author, RelayMember)
            and discord.utils.get(ctx.author.roles, id=ctx.bot.config["roles"]["staff"])
            is not None
        ):
            return True
        else:
            raise commands.MissingPermissions("You are not staff.")

    return commands.check(predicate)


def app_is_staff():
    """A decorator that adds a app_commands.Check to a command to check if the user is a staff member.
    It checks if the user has the staff role in the config file. If they do, it returns True.
    If they don't, it sends a message to the user saying they are not staff and returns False.
    """

    async def predicate(interaction: discord.Interaction):
        if (
            not isinstance(interaction.user, discord.User)
            and discord.utils.get(
                interaction.user.roles, id=interaction.client.config["roles"]["staff"]
            )
            is not None
        ):
            return True
        else:
            await interaction.response.send_message(
                "You are not staff.", ephemeral=True
            )
            return False

    return app_commands.check(predicate)


def is_admin():
    """A decorator that adds a commands.Check to a command to check if the user is an admin.
    It checks if the user has the admin role in the config file. If they do, it returns True.
    If the user is a RelayMember, it returns False as well.
    If they don't, it raises a MissingPermissions error.
    """

    def predicate(ctx):
        if (
            not isinstance(ctx.author, discord.User)
            and not isinstance(ctx.author, RelayMember)
            and discord.utils.get(ctx.author.roles, id=ctx.bot.config["roles"]["admin"])
            is not None
        ):
            return True
        else:
            raise commands.MissingPermissions("You are not an admin.")

    return commands.check(predicate)


def app_is_admin():
    """A decorator that adds a app_commands.Check to a command to check if the user is an admin.
    It checks if the user has the admin role in the config file. If they do, it returns True.
    If they don't, it sends a message to the user saying they are not staff and returns False.
    """

    async def predicate(interaction: discord.Interaction):
        if (
            discord.utils.get(
                interaction.user.roles, id=interaction.client.config["roles"]["admin"]
            )
            is not None
        ):
            return True
        else:
            await interaction.response.send_message(
                "You are not an admin.", ephemeral=True
            )
            return False

    return app_commands.check(predicate)


def is_discord_member():
    """A decorator that adds a commands.Check to a command to check if the user is a discord member.
    This allows you to stop certain commands from being run by relay members.
    """

    def predicate(ctx):
        if not isinstance(ctx.author, RelayMember):
            return True
        else:
            raise commands.MissingPermissions("You are not a discord member.")

    return commands.check(predicate)


def split_list(a, n):
    """Split a list in n parts. The last part may be shorter than the others.

    Args:
        a (list): The list to split
        n (int): The amount of parts to split the list into

    Returns:
        list[list]: A list of n lists with the elements of the original list
    """
    k, m = divmod(len(a), n)
    return list(a[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(n))

def baseconvert(number: str, base_from: int, base_to: int) -> str:
    """Convert a number from one base to another.

    Args:
        number (int): The number to convert.
        base_from (int): The base of the input number.
        base_to (int): The base to convert the number to.

    Returns:
        str: The converted number as a string.
    """
    characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/"
    if base_from > len(characters) or base_to > len(characters):
        raise ValueError(f"Base must be between 2 and {len(characters)}.")
    if base_from < 2 or base_to < 2:
        raise ValueError("Base must be at least 2.")
    
    # Convert from base_from to decimal
    decimal_number = int(str(number), base_from)
    
    # Convert from decimal to base_to
    if decimal_number == 0:
        return "0"
    
    digits = []
    while decimal_number > 0:
        digits.append(characters[int(decimal_number % base_to)])
        decimal_number //= base_to
    
    return ''.join(str(x) for x in digits[::-1])  # Reverse the list and join as string

async def create_deletion_embed(
        staff: typing.Union[discord.Member, discord.User],
        reason: str,
        message: discord.Message,
) -> typing.Tuple[discord.Embed, typing.List[discord.File]]:
    """Creates an embed for a deletion action.

    Args:
        staff (discord.Member): The staff member who performed the deletion.
        reason (str): The reason for the deletion.
        message (discord.Message): The message that was deleted.

    Returns:
        discord.Embed: An embed containing the deletion information.
    """
    embed = discord.Embed(
        title="ORE Moderation Services",
        color=discord.Color.red(),
    )
    embed.set_thumbnail(url="https://i.imgflip.com/44o9ir.png")
    embed.add_field(name="Staff Member", value=staff.mention, inline=False)
    embed.add_field(name="User", value=message.author.mention, inline=True)
    embed.add_field(name="Display Name", value=message.author.display_name, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)
    if len(message.message_snapshots) > 0:
        embed.add_field(
            name="Forwarded Message Content",
            value=f"||{return_or_truncate(message.message_snapshots[0].content, 500)}||" or "No content",
            inline=False,
        )
        attachments = [await attachment.to_file() for attachment in message.message_snapshots[0].attachments]
        # On long message, provide a .txt file with full content
        if len(message.message_snapshots[0].content) > 500:
            full_content_file = discord.File(
                fp=StringIO(message.message_snapshots[0].content),
                filename=f"message_{message.id}_full_content.txt",
                spoiler=True,
            )
            attachments.append(full_content_file)
    else:
        embed.add_field(name="Message Content", value=f"||{return_or_truncate(message.content, 500)}||" or "No content", inline=False)
        attachments = [await attachment.to_file() for attachment in message.attachments]
        # On long message, provide a .txt file with full content
        if len(message.content) > 500:
            full_content_file = discord.File(
                fp=StringIO(message.content),
                filename=f"message_{message.id}_full_content.txt",
                spoiler=True,
            )
            attachments.append(full_content_file)
    embed.add_field(name="Channel", value=message.channel.jump_url, inline=True)
    embed.add_field(name="Context", value=message.jump_url, inline=True)
    embed.set_footer(text=f"Message ID: {message.id}")
    embed.timestamp = discord.utils.utcnow()
    return embed, attachments

async def create_automod_embed(
        message: str,
        matches: list[str]
) -> discord.Embed:
    """Creates an embed for a deletion action.

    Args:
        message (str): The message that was flagged.
        matches (list[str]): The list of regex matches.

    Returns:
        discord.Embed: An embed containing the deletion information.
    """
    embed = discord.Embed(description=message, color=discord.Color.red())
    for match in matches:
        embed.add_field(name="Matches", value=f"`{match}`", inline=False)
    return embed

def get_all_command_names(bot: commands.Bot) -> typing.List[str]:
    """Get all commands registered in the bot.

    Args:
        bot (commands.Bot): The bot instance.

    Returns:
        typing.List[str]: A list of all commands.
    """
    command_names = []
    for command in bot.commands:
        if isinstance(command, commands.Group):
            command_names.extend([f"{command.name} {subcommand.name}" for subcommand in command.walk_commands()])
        else:
            command_names.append(command.name)
        # Add aliases if they exist
        if command.aliases:
            command_names.extend([alias for alias in command.aliases])
    return command_names

async def reply(ctx, message=None, is_reply=False, is_silent=False, **kwargs):
    if message is None:
        message = ""
    target = ctx.reply if is_reply else ctx.send
    return await target(f"{ctx.author.display_name}: {message}", silent=is_silent, **kwargs)
