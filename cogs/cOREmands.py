from random import choice

import discord
from discord import app_commands
from discord.ext import commands

from util import is_staff, app_is_staff


class COREmands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Discord.py doesn't support using the @app_commands.context_menu decorator in Cogs.
        # This is the recommended workaround.
        # See: https://github.com/Rapptz/discord.py/issues/7823#issuecomment-1086830458
        ctx_menu = app_commands.ContextMenu(
            name="Delete message",
            callback=self.delete_message,
        )
        self.bot.tree.add_command(ctx_menu)

    @commands.command(
        help="Shows instructions how to apply for student, builder, or engineer."
    )
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

    @commands.command(help="Give the trusted role to someone.")
    @is_staff()
    async def trust(self, ctx, member: discord.Member):
        await member.add_roles(ctx.guild.get_role(self.bot.config["roles"]["trusted"]))
        await ctx.send(
            f"{ctx.author.display_name}: {member.display_name} is now Trusted."
        )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        greeting = choice(self.bot.config["greetings"])
        channel = member.guild.get_channel(self.bot.config["channels"]["welcome"])
        await channel.send(greeting.format(user=member.mention))

    class DeleteModal(discord.ui.Modal, title="Reason for deleting"):
        reason = discord.ui.TextInput(
            label="Reason",
            placeholder="Why are you deleting this message?",
            style=discord.TextStyle.long,
            required=True,
        )

        def __init__(self, message: discord.Message):
            super().__init__()
            self.original_mesasge = message

        async def on_submit(self, interaction: discord.Interaction):
            await self.original_mesasge.delete()
            await interaction.response.send_message(
                f"Message deleted by {interaction.user.mention}: \"{self.reason}\""
            )

    @app_is_staff()
    async def delete_message(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.send_modal(
            self.DeleteModal(message)
        )

async def setup(bot):
    await bot.add_cog(COREmands(bot))
