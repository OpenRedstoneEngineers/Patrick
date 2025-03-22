import discord
from discord.ext import commands

class COREmands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def apply(self, ctx, *, name: str = None):
        if name is None:
            return await ctx.send('Specify "student", "builder", or "engineer".')
        match name:
            case "student":
                await ctx.send(
                    "To apply for student, hop onto `mc.openredstone.org` and run `/apply`"
                )
            case "builder":
                await ctx.send(
                    "To apply for builder, follow the steps outlined here: <https://discourse.openredstone.org/builder>"
                )
            case "engineer":
                await ctx.send(
                    "To apply for engineer, follow the steps outlined here: <https://discourse.openredstone.org/engineer>"
                )
            case _:
                await ctx.send('Specify "student", "builder", or "engineer".')


def setup(bot):
    bot.add_cog(COREmands(bot))
