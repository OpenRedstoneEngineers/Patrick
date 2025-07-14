from random import choice
import discord
from discord.ext import commands

from util import app_is_staff, is_staff, create_deletion_embed, reply
from timeutil import UserFriendlyTime


class COREmands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help="Shows instructions how to apply for student, builder, or engineer."
    )
    async def apply(self, ctx, *, name: str = None):
        if name is None:
            return await reply(ctx, 'Specify "student", "builder", or "engineer".')
        match name:
            case "student":
                await reply(ctx, "To apply for student, hop onto `mc.openredstone.org` and run `/apply`")
            case "builder":
                await reply(ctx,
                    "To apply for builder, follow the steps outlined here: <https://discourse.openredstone.org/builder>"
                )
            case "engineer":
                await reply(ctx,
                    "To apply for engineer, follow the steps outlined here: <https://discourse.openredstone.org/engineer>"
                )
            case _:
                await reply(ctx, 'Specify "student", "builder", or "engineer".')

    @commands.command(help="Give the trusted role to someone.")
    @is_staff()
    async def trust(self, ctx, member: discord.Member):
        role = ctx.guild.get_role(self.bot.config["roles"]["trusted"])
        if role in member.roles:
            await member.remove_roles(role)
            await reply(ctx, f"{member.display_name} is no longer Trusted.")
        else:
            await member.add_roles(role)
            await reply(ctx, f"{member.display_name} is now Trusted.")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        greeting = choice(self.bot.config["greetings"])
        channel = member.guild.get_channel(self.bot.config["channels"]["welcome"])
        await channel.send(greeting.format(user=member.mention))

async def setup(bot):
    await bot.add_cog(COREmands(bot))
