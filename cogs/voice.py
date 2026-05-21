import discord
import random
import time
from discord.ext import commands, tasks


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_tracker.start()
        self.cash_emoji = "<a:cash:1506921225484767282>"

    def cog_unload(self):
        self.voice_tracker.cancel()

    @tasks.loop(minutes=15)
    async def voice_tracker(self):
        collection = self.bot.db["daily_cooldowns"]

        for guild in self.bot.guilds:
            for member in guild.members:
                if not member.voice or not member.voice.channel or member.bot:
                    continue

                user_id = int(member.id)

                user_data = await collection.find_one(
                    {"$or": [{"_id": user_id}, {"_id": str(user_id)}]}
                ) or {}

                has_necklace = user_data.get("necklace_until", 0) > time.time()
                earnings = 6000 if has_necklace else 3000

                await collection.update_one(
                    {"_id": user_data.get("_id", user_id)},
                    {"$inc": {"coins": earnings}},
                    upsert=True,
                )

                phrases = [
                    "The grind never stops.",
                    "System rewards credited successfully.",
                    "Your bank account is growing.",
                    "Consistency pays off, citizen.",
                ]

                await member.voice.channel.send(
                    f"{member.mention} | You earned {self.cash_emoji} **{earnings:,}**\n"
                    f"-# {random.choice(phrases)}"
                )

    @voice_tracker.before_loop
    async def before_tracker(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Voice(bot))
