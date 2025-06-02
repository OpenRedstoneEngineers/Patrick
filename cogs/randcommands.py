import asyncio
from asyncio import to_thread
from io import BytesIO
from os import getenv
from random import choice, getrandbits, randint
from time import perf_counter

import discord
from discord.ext import commands

from fractal import fractal
from util import is_admin, is_staff

import openai
openai.api_key = getenv("OPENAI_API_KEY")


class RandCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Performs a ping test and shows results.")
    async def ping(self, ctx):
        start = perf_counter()
        message = await ctx.send("Testing...")
        latency = (perf_counter() - start) * 1000
        await message.edit(
            content=f"Pong!\nLatency: {latency:.2f}ms\nAPI Latency: {self.bot.latency * 1000:.2f}ms"
        )

    @commands.command(help="Consult the ancient wisdom of a cranky AI-powered Iron Golem about your redstone woes.")
    async def golem(self, ctx, *, question: str):
        if len(question) > 256:
            return await ctx.send("Question is too long. Maximum length is 256 characters.")
        if len(question) < 1:
            return await ctx.send("Question is too short.")
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cranky AI-powered Iron Golem who is an expert in redstone. You answer questions about redstone with sarcasm and wit.",
                    },
                    {"role": "user", "content": question},
                ],
            )
            answer = response.choices[0].message.content
            return await ctx.send(answer)

        except Exception as e:
            return await ctx.send("An error occurred while processing your request. Likely fan forgot to pay his bill.")

    @commands.command(help="Gets a random quote from zenquotes.")
    async def quote(self, ctx):
        async with self.bot.aiosession.get(
            "https://zenquotes.io/api/random/"
        ) as response:
            if response.status == 200:
                data = await response.json()
                await ctx.send(f"\"{data[0]['q']}\" - {data[0]['a']}")

    async def get_xkcd_data(self, number: int):
        async with self.bot.aiosession.get(
            f"https://xkcd.com/{number}/info.0.json"
        ) as response:
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
        embed.set_footer(
            text=f"{data['num']} ({data['month']}/{data['day']}/{data['year']})"
        )
        return embed

    @commands.command(help="Gets a random or specific xkcd comic.")
    async def xkcd(self, ctx, number: int = None):
        if number is None:
            async with self.bot.aiosession.get(
                "https://xkcd.com/info.0.json"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    randnum = randint(1, data["num"])
                    data = await self.get_xkcd_data(randnum)
                    if data is None:
                        return await ctx.send(
                            "An error occurred while fetching the comic."
                        )
                    await ctx.send(embed=self.xkcd_embed(data))

        else:
            data = await self.get_xkcd_data(number)
            if data is None:
                return await ctx.send("An error occurred while fetching the comic.")
            await ctx.send(embed=self.xkcd_embed(data))

    @commands.command(
        help="Generates a random binary number with the given amount of bits."
    )
    async def rng(self, ctx, num: int):
        if num < 1:
            return await ctx.send("Number must be greater than 0.")
        generated = getrandbits(num)
        await ctx.send(f"{ctx.author.display_name}: {generated:0{num}b}")

    @commands.command(help="Get someone's minecraft UUID.")
    async def uuid(self, ctx, username: str):
        async with self.bot.aiosession.get(
            f"https://api.mojang.com/users/profiles/minecraft/{username}"
        ) as response:
            if response.status == 200:
                data = await response.json()
                raw_uuid = data["id"]
                uuid = str(
                    raw_uuid[:8]
                    + "-"
                    + raw_uuid[8:12]
                    + "-"
                    + raw_uuid[12:16]
                    + "-"
                    + raw_uuid[16:20]
                    + "-"
                    + raw_uuid[20:]
                )
                await ctx.send(f"{ctx.author.display_name}: `{uuid}`")
            else:
                await ctx.send("Invalid username provided")

    @commands.command(help="Slap someone.")
    @commands.guild_only()
    async def slap(self, ctx, user: discord.Member):
        slap_role = discord.utils.get(ctx.guild.roles, name="slapped")
        if slap_role is None:
            return await ctx.send("No slapped rank :(")
        if slap_role in user.roles:
            return await ctx.send("User is already slapped.")
        await user.add_roles(slap_role)
        await ctx.send(f"{user.mention} got slapped by {ctx.author.mention}.")
        await asyncio.sleep(3_600)  # 1 hour
        await user.remove_roles(slap_role)

    @commands.command(help="pikl someone.")
    @commands.guild_only()
    @is_staff()
    async def pikl(self, ctx, user: discord.Member):
        pikl_role = discord.utils.get(ctx.guild.roles, name="pikl")
        if pikl_role is None:
            return await ctx.send("No pikl rank :(")
        await user.add_roles(pikl_role)
        await ctx.send(f"{user.mention} got pikl'd.")
        await asyncio.sleep(120_000)
        await user.remove_roles(pikl_role)

    @commands.command(help="Googles something.")
    async def google(self, ctx, *, query):
        await ctx.send(f"<https://www.google.com/search?q={query.replace(' ', '+')}>")

    def prime_factors(self, n: int) -> list:
        i = 2
        factors = []
        while i * i <= n:
            if n % i:
                i += 1
            else:
                n //= i
                factors.append(i)
        if n > 1:
            factors.append(n)
        return factors

    @commands.command(help="Get the prime factors of a number.")
    async def factorize(self, ctx, number: int):
        if number < 1:
            return await ctx.send("Number must be greater than 0.")
        factors = self.prime_factors(number)
        powered_factors = []
        for factor in set(factors):
            count = factors.count(factor)
            if count > 1:
                powered_factors.append(
                    f"{factor}^{str(count).translate({"2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"})}"
                )
            else:
                powered_factors.append(f"{factor}")
        await ctx.send(
            f"{ctx.author.display_name}: {number} = {' * '.join(powered_factors)}"
        )

    @commands.command(help="Get the aeiou version of your text.", aliases=["tts"])
    @commands.cooldown(15, 60, commands.BucketType.default)
    async def aeiou(self, ctx, *, text):
        if len(text) > 1024:
            return await ctx.send(
                "Text is too long. Maximum length is 1024 characters."
            )
        if len(text) < 1:
            return await ctx.send("Text is too short. Minimum length is 1 character.")
        user_agent = "Patrick discord bot | Python 3 | sebkuip | https://github.com/OpenRedstoneEngineers/Patrick/"
        headers = {
            "User-Agent": user_agent,
        }
        async with self.bot.aiosession.get(
            "https://tts.cyzon.us/tts", headers=headers, params={"text": text}
        ) as response:
            if response.status == 200:
                audio = BytesIO(await response.read())
                file = discord.File(audio, filename="aeiou.mp3")
                await ctx.send(f"{ctx.author.display_name}: {text}", file=file)
            else:
                await ctx.send("An error occurred while fetching the aeiou text.")

    @commands.command(help="Generate a fractal image using a given seed.")
    @is_staff()
    async def fractal(self, ctx, seed: str):
        start = perf_counter()
        size = self.bot.config["fractalDeets"]["size"]
        max_iter = self.bot.config["fractalDeets"]["maxIterations"]
        messiness = self.bot.config["fractalDeets"]["messiness"]
        zoom = self.bot.config["fractalDeets"]["zoom"]

        frac = await to_thread(fractal, seed, size, size, max_iter, messiness, zoom)

        with BytesIO() as image_binary:
            frac.save(image_binary, "PNG")
            image_binary.seek(0)
            file = discord.File(fp=image_binary, filename="image.png")
            embed = discord.Embed()
            embed.set_image(url="attachment://image.png")
            await ctx.send(file=file, embed=embed)

        end = perf_counter()
        self.bot.logger.info(
            f"Fractal generation took {end - start:.2f} seconds for seed '{seed}'"
        )

    @commands.command(help="Be mean to someone. >:D")
    async def insult(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        message = choice(self.bot.config["insults"])
        await ctx.send(message.format(user=user.display_name))


async def setup(bot):
    await bot.add_cog(RandCommands(bot))
