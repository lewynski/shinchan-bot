import time
import random
import discord
from discord.ext import commands
from discord import app_commands

class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="daily", description="Claim your daily rewards.")
    async def daily(self, ctx: commands.Context):
        coin_emoji = "<:coin:1506921225484767282>"
        user_id = ctx.author.id
        current_time = int(time.time())
        cooldown_seconds = 86400  # 24 hours
        
        cooldown_collection = self.bot.db['daily_cooldowns']
        user_data = await cooldown_collection.find_one({"_id": user_id})
        
        if user_data:
            last_claim = user_data.get("last_claim", 0)
            time_passed = current_time - last_claim
            
            if time_passed < cooldown_seconds:
                next_claim_timestamp = last_claim + cooldown_seconds
                await ctx.send(
                    f"You have already claimed your daily reward!\n"
                    f"-# You can daily again <t:{next_claim_timestamp}:R>",
                    ephemeral=True
                )
                return

        # Roll a random reward value between 500 and 10,000
        random_reward = random.randint(500, 10000)

        # Update time and increment the coins field by the randomized reward amount
        await cooldown_collection.update_one(
            {"_id": user_id},
            {
                "$set": {"last_claim": current_time},
                "$inc": {"coins": random_reward}
            },
            upsert=True
        )
        
        # Formatted using commas for large numbers (e.g., 5,230 instead of 5230)
        await ctx.send(
            f"Here's your daily coin {coin_emoji} **+{random_reward:,}**\n"
            f"-# You can daily again <t:{current_time + cooldown_seconds}:R>"
        )

async def setup(bot):
    await bot.add_cog(Daily(bot))
