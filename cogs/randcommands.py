import asyncio
import random
from asyncio import to_thread
from io import BytesIO
from random import choice, getrandbits, randint
from time import perf_counter

import discord
from discord.ext import commands

from fractal import fractal
from brainfuck import process_brainfuck
from util import is_staff, baseconvert, reply


class RandCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        bases = {
        "b": 2,
        "o": 8,
        "d": 10,
        "h": 16,
        "64": 64,
    }
        async def convert_func(ctx, number: str):
            from_base = ctx.command.extras["from_base"]
            to_base = ctx.command.extras["to_base"]
            try:
                converted = baseconvert(number, bases[from_base], bases[to_base])
                await reply(ctx, converted)
            except ValueError as e:
                await reply(ctx, f"Invalid input number for base {from_base}")

        for from_base, from_value in bases.items():
            for to_base, to_value in bases.items():
                if from_base == to_base:
                    continue
                self.bot.add_command(commands.Command(
                        convert_func,
                        help=f"Convert a number from base {from_value} to base {to_value}.",
                        name=f"{from_base}2{to_base}",
                        extras={"from_base": from_base, "to_base": to_base},
                    )
                )

    @commands.command(help="Performs a ping test and shows results.", aliases=["pingtest"])
    async def ping(self, ctx):
        start = perf_counter()
        message = await reply(ctx, "Testing...")
        latency = (perf_counter() - start) * 1000
        await message.edit(
            content=f"{ctx.author.display_name}: Pong!\nLatency: {latency:.2f}ms\n"
                    f"API Latency: {self.bot.latency * 1000:.2f}ms"
        )

    @commands.command(help="Gets a random quote from zenquotes.", aliases=["zenquote"])
    async def quote(self, ctx):
        async with self.bot.aiosession.get(
            "https://zenquotes.io/api/random/"
        ) as response:
            if response.status == 200:
                data = await response.json()
                await reply(ctx, f"\"{data[0]['q']}\" - {data[0]['a']}")

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
        )
        embed.set_image(url=data["img"])
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
                        return await reply(ctx, "An error occurred while fetching the comic.")
                    await reply(ctx, embed=self.xkcd_embed(data))

        else:
            data = await self.get_xkcd_data(number)
            if data is None:
                return await reply(ctx, "An error occurred while fetching the comic.")
            await reply(ctx, embed=self.xkcd_embed(data))

    @commands.command(
        help="Generates a random binary number with the given amount of bits.", aliases=["random"]
    )
    async def rng(self, ctx, num: int):
        if num < 1:
            return await reply(ctx, "Number must be greater than 0.")
        if num > 128:
            return await reply(ctx, "Number must not be greater than 128.")
        generated = getrandbits(num)
        await reply(ctx, f"`{generated:0{num}b}`")

    @commands.command(help="Roll some dice.", aliases=["dice"])
    async def roll(self, ctx, options: str = None):
        d6 = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
        if not options:
            await reply(ctx, random.choice(d6))
        elif options == "rick":
            await reply(ctx, "<https://youtu.be/dQw4w9WgXcQ>")
        else:
            to_return = []
            for dice in options.split("+"):
                try:
                    count, sides = dice.split("d")
                    if int(count) < 1 or int(count) > 10:
                        return await reply(ctx, "Invalid roll count!")
                    if int(sides) < 2 or int(sides) > 20:
                        return await reply(ctx, "Invalid number of sides!")
                    values = [random.randint(1, int(sides)) for _ in range(int(count))]
                    values_ = ", ".join([str(_) for _ in values])
                    to_return.append(f"**d{sides}** rolled **{count}** time(s): `{values_}` (**{sum(values)}**)")
                except ValueError:
                    return await reply(ctx, "Invalid dice format! I'm expecting XdT where X is "
                                   f"the number of rolls and T is the number of sides.")
            to_return = "\n".join(to_return)
            await reply(ctx, to_return)

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
                await reply(ctx, f"`{uuid}`")
            else:
                await reply(ctx, "Invalid username provided")

    @commands.command(help="Slap someone.")
    @commands.guild_only()
    async def slap(self, ctx, user: discord.Member):
        slap_role = discord.utils.get(ctx.guild.roles, name="Slapped")
        if slap_role is None:
            return await reply(ctx, "No slapped rank :(")
        if slap_role in user.roles:
            return await reply(ctx, "User is already slapped.")
        await user.add_roles(slap_role)
        await reply(ctx, f"slapped {user.mention}", False, True)
        await asyncio.sleep(3_600)  # 1 hour
        await user.remove_roles(slap_role)

    @commands.command(help="pikl someone.")
    @commands.guild_only()
    @is_staff()
    async def pikl(self, ctx, user: discord.Member):
        pikl_role = discord.utils.get(ctx.guild.roles, name="pikl")
        if pikl_role is None:
            return await reply(ctx, "No pikl rank :(")
        await user.add_roles(pikl_role)
        await reply(ctx, f"{user.mention} got pikl'd.", False, True)
        await asyncio.sleep(120)
        await user.remove_roles(pikl_role)

    @commands.command(help="Googles something.", aliases=["lmgtfy"])
    async def google(self, ctx, *, query):
        await reply(ctx, f"<https://www.google.com/search?q={query.replace(' ', '+')}>")

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
            return await reply(ctx, "Number must be greater than 0.")
        pow_map = {"2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
        try:
            factors = await asyncio.wait_for(
                asyncio.to_thread(self.prime_factors, number),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            return await reply(ctx, "Calculation took too long, terminating.")
        powered_factors = []
        for factor in set(factors):
            count = factors.count(factor)
            if count > 1:
                powered_factors.append(
                    f"{factor}^{str(count).translate(pow_map)}"
                )
            else:
                powered_factors.append(f"{factor}")
        await reply(ctx, f"{number} = {' * '.join(powered_factors)}")

    @commands.command(help="Get the aeiou version of your text.", aliases=["tts"])
    @commands.cooldown(15, 60, commands.BucketType.default)
    async def aeiou(self, ctx, *, text):
        if len(text) > 1024:
            return await reply(ctx, "Text is too long. Maximum length is 1024 characters.")
        if len(text) < 1:
            return await reply(ctx, "Text is too short. Minimum length is 1 character.")
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
                await reply(ctx, text, file=file)
            else:
                await reply(ctx, "An error occurred while fetching the aeiou text.")

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
            await reply(ctx, seed, file=file, embed=embed)

        end = perf_counter()
        self.bot.logger.info(
            f"Fractal generation took {end - start:.2f} seconds for seed '{seed}'"
        )

    @commands.command(help="Be mean to someone. >:D")
    async def insult(self, ctx, target: str = None):
        if target is None:
            target = ctx.author.display_name
        message = choice(self.bot.config["insults"])
        await reply(ctx, message.format(user=target))

    @commands.command(help="Process brainfuck code.", aliases=["bf"])
    async def brainfuck(self, ctx, code: str, input: str = ""):
        if len(code) > 1000:
            return await reply(ctx, "Code is too long. Maximum length is 1000 characters.")
        if len(input) > 1000:
            return await reply(ctx, "Input is too long. Maximum length is 1000 characters.")
        try:
            output = await asyncio.wait_for(
                asyncio.to_thread(process_brainfuck, code, input),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            return await reply(ctx, "Processing took too long, terminating.")
        await reply(ctx, output)

async def setup(bot):
    await bot.add_cog(RandCommands(bot))
