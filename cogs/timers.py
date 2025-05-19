from datetime import datetime, timezone

import discord
from discord.ext import commands

from util import is_discord_member


def pretty_timedelta(delta):
    """Convert a timedelta to a human-readable string."""
    days, seconds = delta.days, delta.seconds
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return (
        f"{days}d {hours}h {minutes}m {seconds}s"
        if days
        else f"{hours}h {minutes}m {seconds}s"
    )


class Timers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="timer", invoke_without_command=True)
    @is_discord_member()
    async def timer(self, ctx):
        """Timer commands"""
        raise commands.CommandNotFound(
            "Invalid subcommand. Use `,timer start`, `,timer stop`, or `,timer list`."
        )

    @timer.command(name="start")
    @is_discord_member()
    async def start_timer(self, ctx, *, name: str):
        await self.bot.database.start_timer(ctx.author.id, name)
        await ctx.send(f"{ctx.author.display_name}: Timer '{name}' started.")

    @timer.command(name="stop")
    @is_discord_member()
    async def stop_timer(self, ctx, *, name: str):
        rows = await self.bot.database.stop_timer(ctx.author.id, name)
        if rows:
            row = rows[0]
            await ctx.send(
                f"{ctx.author.display_name}: Timer '{name}' stopped. Took {pretty_timedelta(datetime.now(timezone.utc) - row[0])}"
            )
        else:
            await ctx.send(
                f"{ctx.author.display_name}: No timer found with the name '{name}'."
            )

    @timer.command(name="list")
    @is_discord_member()
    async def list_timers(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
        rows = await self.bot.database.get_timers(member.id)
        if rows:
            timers = "\n".join(
                [f"{row[0]}: <t:{int(row[1].timestamp())}:f>" for row in rows]
            )
            if member == ctx.author:
                await ctx.send(f"{ctx.author.display_name}: Your timers:\n{timers}")
            else:
                await ctx.send(
                    f"{ctx.author.display_name}: {member.display_name}'s timers:\n{timers}"
                )
        else:
            await ctx.send(f"{ctx.author.display_name}: No timers found.")


async def setup(bot):
    await bot.add_cog(Timers(bot))
