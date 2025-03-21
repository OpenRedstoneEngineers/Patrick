import discord
from discord.ext import commands

from time import perf_counter
from random import randint, choice

class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        start = perf_counter()
        message = await ctx.send("Testing...")
        latency = (perf_counter() - start) * 1000
        await message.edit(content=f"Pong!\nLatency: {latency:.2f}ms\nAPI Latency: {self.bot.latency * 1000:.2f}ms")

    @commands.command()
    async def quote(self, ctx):
        async with self.bot.aiosession.get("https://zenquotes.io/api/random/") as response:
            if response.status == 200:
                data = await response.json()
                await ctx.send(f"\"{data[0]['q']}\" - {data[0]['a']}")

    async def get_xkcd_data(self, number: int):
        async with self.bot.aiosession.get(f"https://xkcd.com/{number}/info.0.json") as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return None

    def xkcd_embed(self, data):
        embed = discord.Embed(
            title=data["title"],
            description=data["alt"],
            url=f"https://xkcd.com/{data['num']}",
            image=data["img"],
        )
        embed.set_footer(text=f"{data['num']} ({data['month']}/{data['day']}/{data['year']})")
        return embed

    @commands.command()
    async def xkcd(self, ctx, number: int = None):
        if number is None:
            async with self.bot.aiosession.get("https://xkcd.com/info.0.json") as response:
                if response.status == 200:
                    data = await response.json()
                    randnum = randint(1, data["num"])
                    data = await self.get_xkcd_data(randnum)
                    if data is None:
                        return await ctx.send("An error occurred while fetching the comic.")
                    await ctx.send(embed=self.xkcd_embed(data))

        else:
            data = await self.get_xkcd_data(number)
            if data is None:
                return await ctx.send("An error occurred while fetching the comic.")
            await ctx.send(embed=self.xkcd_embed(data))

    @commands.command()
    async def protip(self, ctx):
        random_tip = choice(self.bot.config.get("protips"))
        await ctx.send(f"{ctx.author.display_name}: Pro Tip: {random_tip}")

def setup(bot):
    bot.add_cog(FunCommands(bot))
