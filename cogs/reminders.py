import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta

from util import is_discord_member
from timeutil import UserFriendlyTime
from paginator import EmbedPaginatorSession


def timestamp(dt, *, format="R") -> str:
    unix = int(dt.timestamp())
    return f"<t:{unix}:{format}>"


class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()

    @is_discord_member()
    @commands.command(name='remindme', aliases=['reminder', 'remind'])
    async def remind_me(self, ctx, *, time: UserFriendlyTime):
        """Set a reminder."""
        message = time.arg
        await self.bot.database.add_reminder(
            user_id=ctx.author.id,
            channel_id=ctx.channel.id,
            message=message,
            timestamp=time.dt
        )

        msg = f"{ctx.author.mention}: I will remind you at {time.dt.strftime('%Y-%m-%d %H:%M:%S')} UTC ({timestamp(time.dt)}) "
        if message:
            msg += f"with the message: {message}"
        await ctx.reply(msg)

    @is_discord_member()
    @commands.command(name='reminders', aliases=['myreminders'])
    async def my_reminders(self, ctx):
        """List all reminders set by the user."""
        reminders = await self.bot.database.get_reminders(ctx.author.id)
        if not reminders:
            return await ctx.reply(f"{ctx.author.display_name}: You have no reminders set.")

        if len(reminders) > 5:
            embeds = [discord.Embed(title=f"{ctx.author.display_name}'s Reminders", color=discord.Color.blue()) for _ in range((len(reminders) - 1) // 5 + 1)]
            for i, reminder in enumerate(reminders):
                embeds[i // 5].add_field(
                    name=f"Reminder at {reminder[2].strftime('%Y-%m-%d %H:%M:%S')}",
                    value=f"Message: {reminder[0] or '-'}",
                    inline=False
                )
            paginator = EmbedPaginatorSession(ctx, *embeds)
            await paginator.run()
        else:
            embed = discord.Embed(title=f"{ctx.author.display_name}'s Reminders", color=discord.Color.blue())
            for message, _, timestamp in reminders:
                    embed.add_field(
                        name=f"Reminder at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                        value=f"Message: {message or '-'}",
                        inline=False
                    )
            await ctx.reply(embed=embed)

    @tasks.loop(seconds=60)
    async def check_reminders(self):
        """Check for reminders that need to be sent."""
        reminders = await self.bot.database.pop_expired_reminders()
        for reminder in reminders:
            user_id, channel_id, message = reminder
            channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
            try:
                await channel.send(f"<@{user_id}>{f': {message}' if message else ''}")
            except discord.Forbidden:
                # If the bot cannot send messages to the channel, skip it
                continue

async def setup(bot):
    await bot.add_cog(Reminders(bot))
