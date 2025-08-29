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

    class DeleteModal(discord.ui.Modal, title="Reason for deleting"):
        reason = discord.ui.TextInput(
            label="Reason",
            placeholder="Why are you deleting this message?",
            style=discord.TextStyle.long,
            required=True,
        )

        def __init__(self, message: discord.Message, bot):
            super().__init__()
            self.original_message = message
            self.bot = bot

        async def on_submit(self, interaction: discord.Interaction):
            reason = str(self.reason).strip()
            if reason == "":
                reason = "No reason provided"
            await interaction.response.send_message(
                f'Message deleted by {interaction.user.mention}: "{reason}"'
            )
            channel = interaction.guild.get_channel(self.bot.config["channels"]["audit_log"])
            embed, attachments = await create_deletion_embed(
                interaction.user,
                reason,
                self.original_message,
            )
            await channel.send(embed=embed, files=attachments)
            await self.original_message.delete()

    @app_is_staff()
    async def delete_message(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        await interaction.response.send_modal(self.DeleteModal(message, self.bot))


async def setup(bot):
    await bot.add_cog(COREmands(bot))
