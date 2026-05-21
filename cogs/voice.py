import discord
import random
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
        for guild in self.bot.guilds:
            for member in guild.members:
                # Check if member is in a voice channel and isn't a bot
                if member.voice and member.voice.channel and not member.bot:
                    
                    # Fetch user from DB
                    user_data = await self.bot.db.users.find_one({"user_id": member.id})
                    items = user_data.get("items", []) if user_data else []
                    has_necklace = "necklace" in items
                    
                    earnings = 6000 if has_necklace else 3000
                    
                    # Update Balance
                    await self.bot.db.users.update_one(
                        {"user_id": member.id},
                        {"$inc": {"balance": earnings}},
                        upsert=True
                    )

                    phrases = [
                        "The grind never stops.",
                        "System rewards credited successfully.",
                        "Your bank account is growing.",
                        "Consistency pays off, citizen."
                    ]

                    # The mention (ping) is included here as requested
                    await member.voice.channel.send(
                        f"{member.mention} | You earned {self.cash_emoji} **{earnings:,}**\n"
                        f"-# {random.choice(phrases)}"
                    )

    @voice_tracker.before_loop
    async def before_tracker(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Voice(bot))
