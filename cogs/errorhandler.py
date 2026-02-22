import traceback

from discord.ext import commands

from util import NoRelayException, reply


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  # This is the bot instance, it lets us interact with most things

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        async def respond(message):
            await reply(ctx, f"{message}")

        if hasattr(ctx.command, "on_error"):
            return

        error = getattr(error, "original", error)

        if isinstance(error, commands.NotOwner) or isinstance(
            error, commands.MissingPermissions
        ):
            await respond("Unauthorized :'(")
        elif isinstance(error, commands.MemberNotFound):
            await respond("Member not found.")
        elif isinstance(error, commands.BadArgument):
            await respond("The argument you gave is invalid/cannot be processed.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await respond(
                f"Command usage: `,{ctx.command.name} {ctx.command.signature}`"
            )
        elif isinstance(error, commands.CommandNotFound):
            self.bot.logger.info(
                f"User '{ctx.author.display_name}' attempted to run an unrecognized command: '{ctx.message.content[1:]}'"
            )
            await respond("Unrecognized command :'(")
        elif isinstance(error, commands.CommandOnCooldown):
            await respond(
                f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds."
            )
        elif isinstance(error, commands.BotMissingPermissions):
            await respond("Bot does not have permissions for this command.")
        elif isinstance(error, commands.DisabledCommand):
            await respond("This command is disabled.")
        elif isinstance(error, commands.PrivateMessageOnly):
            await respond("This command can only be used in DMs.")
        elif isinstance(error, commands.NoPrivateMessage):
            await respond("This command cannot be used in DMs.")
        elif isinstance(error, NoRelayException):
            await respond("This command does not work in the relay chat :'(")
        else:
            await respond("An unknown error occurred while processing the command.")
            traceback.print_tb(error.__traceback__)
            self.bot.logger.error(error)


async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
