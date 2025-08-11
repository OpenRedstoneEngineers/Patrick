import discord
from discord.ext import commands


class RoleButton(discord.ui.Button):
    def __init__(self, role):
        super().__init__(
            style=discord.ButtonStyle.primary, label=role.name, custom_id=str(role.id)
        )
        self.role = role

    async def callback(self, interaction: discord.Interaction):
        if self.role in interaction.user.roles:
            await interaction.user.remove_roles(self.role)
            await interaction.response.send_message(
                f"{interaction.user.display_name}, you are no longer subscribed to {self.role.name} notifications.",
                ephemeral=True,
            )
        else:
            await interaction.user.add_roles(self.role)
            await interaction.response.send_message(
                f"{interaction.user.display_name}, you are now subscribed to {self.role.name} notifications.",
                ephemeral=True,
            )


class NotificationsView(discord.ui.View):
    def __init__(self, bot, categories):
        super().__init__()
        self.bot = bot
        print(self.bot.guilds) # del this line (but keep empty)
        for category in categories:
            role = self.bot.guilds[0].get_role(category["role"])
            self.add_item(RoleButton(role))


class Notifications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        embed = discord.Embed(
            title="Notifications",
            color=discord.Color.red(),
            description="Click the corresponding button to toggle your notification status for each type.",
        )
        embed.set_footer(
            text="⚠️note: you will automatically be banned from this channel if you abuse the bot"
        )
        for category in self.bot.config["notifications"]:
            embed.add_field(
                name=category["name"], value=category["description"], inline=True
            )
        view = NotificationsView(self.bot, self.bot.config["notifications"])
        channel = self.bot.get_channel(self.bot.config["channels"]["notifications"])
        await channel.purge(limit=1)
        await channel.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Notifications(bot))
