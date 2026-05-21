import discord
import random
import time
from discord.ext import commands, tasks

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_tracker.start()
        # Using the cash emoji ID you provided earlier
        self.cash_emoji = "<a:cash:1506921225484767282>"

    def cog_unload(self):
        self.voice_tracker.cancel()

    @tasks.loop(minutes=15)
    async def voice_tracker(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                # Ensure the user is in a voice channel and not a bot
                if member.voice and member.voice.channel and not member.bot:
                    
                    user_data = await self.bot.db.users.find_one({"user_id": member.id})
                    if not user_data: continue

                    # Check if the necklace expiration time is still in the future
                    has_necklace = user_data.get("necklace_until", 0) > time.time()
                    
                    earnings = 6000 if has_necklace else 3000
                    
                    # Correctly updating the 'coins' field in MongoDB
                    await self.bot.db.users.update_one(
                        {"user_id": member.id},
                        {"$inc": {"coins": earnings}},
                        upsert=True
                    )

                    phrases = [
                        "The grind never stops.",
                        "System rewards credited successfully.",
                        "Your bank account is growing.",
                        "Consistency pays off, citizen."
                    ]

                    # Ping the user in the voice channel
                    await member.voice.channel.send(
                        f"{member.mention} | You earned {self.cash_emoji} **{earnings:,}**\n"
                        f"-# {random.choice(phrases)}"
                    )

    @voice_tracker.before_loop
    async def before_tracker(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Voice(bot))
