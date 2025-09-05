import discord
from discord import app_commands
from discord.ext import commands, tasks
import typing

from util import is_staff, app_is_staff, create_deletion_embed, reformat_relay_chat
from timeutil import UserFriendlyTime

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_tempbans.start()
        # Discord.py doesn't support using the @app_commands.context_menu decorator in Cogs.
        # This is the recommended workaround.
        # See: https://github.com/Rapptz/discord.py/issues/7823#issuecomment-1086830458
        ctx_menu = app_commands.ContextMenu(
            name="Delete message",
            callback=self.delete_message,
        )
        self.bot.tree.add_command(ctx_menu)

    @tasks.loop(seconds=60)
    async def check_tempbans(self):
        tempbans = await self.bot.database.pop_expired_tempbans()
        if not tempbans:
            return
        channel = self.bot.get_channel(self.bot.config["channels"]["audit_log"])
        for user_id, in tempbans:
            user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
            if user:
                try:
                    await self.bot.guild.unban(user, reason=f"Temporary ban expired")
                except discord.NotFound:
                    # User is not banned, skip
                    continue
                embed = discord.Embed(
                    title="ORE Moderation Services",
                    description=f"{user.mention} has been unbanned after their temporary ban expired.",
                    color=discord.Color.green(),
                )
                embed.set_thumbnail(url="https://i.imgflip.com/44o9ir.png")
                embed.timestamp = discord.utils.utcnow()
                await channel.send(embed=embed)

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
            message = self.original_message
            if message.author.bot and message.channel.id == self.bot.config["channels"]["gamechat"]:
                message = reformat_relay_chat(self.bot, message)
            embed, attachments = await create_deletion_embed(
                interaction.user,
                reason,
                message,
            )
            await channel.send(embed=embed, files=attachments)
            await self.original_message.delete()

    @app_is_staff()
    async def delete_message(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        await interaction.response.send_modal(self.DeleteModal(message, self.bot))

    @is_staff()
    async def tempban(self, ctx, user: typing.Union[discord.Member, discord.User], *, time: UserFriendlyTime):
        reason = time.arg
        channel = ctx.guild.get_channel(self.bot.config["channels"]["audit_log"])
        await self.bot.database.add_tempban(
            user_id=user.id,
            reason=reason,
            timestamp=time.dt,
        )
        await ctx.guild.ban(user, reason=f"Temporary ban by {ctx.author}: {reason or 'No reason provided'}")
        embed = discord.Embed(
            title="ORE Moderation Services",
            color=discord.Color.red(),
        )
        embed.set_thumbnail(url="https://i.imgflip.com/44o9ir.png")
        embed.add_field(name="Staff Member", value=ctx.author.mention, inline=False)
        embed.add_field(name="User", value=user.mention, inline=True)
        embed.add_field(name="Display Name", value=user.display_name, inline=True)
        embed.add_field(name="Reason", value=reason if reason else "No reason provided", inline=False)
        embed.timestamp = ctx.message.created_at

        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))