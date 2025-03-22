import traceback

import discord
from discord.ext import commands


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # This is the bot instance, it lets us interact with most things

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if hasattr(ctx.command, "on_error"):
            return

        error = getattr(error, "original", error)

        if isinstance(error, commands.NotOwner) or isinstance(
            error, commands.MissingPermissions
        ):
            await ctx.send("Unauthorized :'(")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Member not found.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("The argument you gave is invalid/cannot be processed.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"Command usage: `,{ctx.command.name} {ctx.command.signature}`"
            )
        elif isinstance(error, commands.CommandNotFound):
            self.bot.logger.info(
                f"User '{ctx.author}' attempted to run an unrecognized command: '{ctx.message.content[1:]}'"
            )
            await ctx.send("Unrecognized command :'(")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Bot does not have permissions for this command.")
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send("This command is disabled.")
        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.send("This command can only be used in DMs.")
        else:
            await ctx.send("An unknown error occurred while processing the command.")
            traceback.print_tb(error.__traceback__)
            self.bot.logger.error(error)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
