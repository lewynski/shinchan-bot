import time
import discord
from discord.ext import commands
from discord import app_commands

class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="daily", description="Claim your daily rewards.")
    async def daily(self, ctx: commands.Context):
        # Your custom developer portal emoji string
        coin_emoji = "<:coin:1506921225484767282>"
        
        user_id = ctx.author.id
        current_time = int(time.time())
        cooldown_seconds = 86400  # 24 hours in seconds
        
        # Access your MongoDB 'daily_cooldowns' collection
        cooldown_collection = self.bot.db['daily_cooldowns']
        
        # Look up the user's last claim time
        user_data = await cooldown_collection.find_one({"_id": user_id})
        
        if user_data:
            last_claim = user_data.get("last_claim", 0)
            time_passed = current_time - last_claim
            
            if time_passed < cooldown_seconds:
                # Calculate the exact timestamp when they can claim again
                next_claim_timestamp = last_claim + cooldown_seconds
                
                # Using Discord's <t:timestamp:R> creates a dynamic live countdown string
                await ctx.send(
                    f"You have already claimed your daily reward!\n"
                    f"-# You can daily again <t:{next_claim_timestamp}:R>"
                )
                return

        # If they haven't claimed yet or the 24 hours passed, update the database
        await cooldown_collection.update_one(
            {"_id": user_id},
            {"$set": {"last_claim": current_time}},
            upsert=True
        )
        
        # Elegant text response using your custom emoji and small subtext layout
        await ctx.send(
            f"Here's your daily coin {coin_emoji}\n"
            f"-# You can daily again <t:{current_time + cooldown_seconds}:R>"
        )

async def setup(bot):
    await bot.add_cog(Daily(bot))
