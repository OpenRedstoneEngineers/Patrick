import discord
from discord.ext import commands

from util import get_custom_commands, is_staff


class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @is_staff()
    async def addcommand(self, ctx, key: str, *, message: str):
        commands = await get_custom_commands(self.bot)
        if key in commands:
            await ctx.send(f"Command `{key}` already exists.")
            return
        await self.bot.database.add_command(key, message)
        await ctx.send(f"Command `{key}` added.")

    @commands.command()
    @is_staff()
    async def delcommand(self, ctx, key: str):
        await self.bot.database.remove_command(key)
        await ctx.send(f"Command `{key}` removed.")


def setup(bot):
    bot.add_cog(CustomCommands(bot))
