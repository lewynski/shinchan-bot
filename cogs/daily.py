import time
import random

from discord.ext import commands

from cogs.announcement import send_pending_announcement


class Daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="daily", description="Claim your daily rewards.")
    async def daily(self, ctx: commands.Context):
        coin_emoji = "<:coin:1506921225484767282>"
        user_id = int(ctx.author.id)
        current_time = int(time.time())
        cooldown_seconds = 86400

        cooldown_collection = self.bot.db["daily_cooldowns"]

        user_data = await cooldown_collection.find_one(
            {"$or": [{"_id": user_id}, {"_id": str(user_id)}]}
        ) or {}

        await send_pending_announcement(self.bot, ctx, user_id)

        if user_data:
            last_claim = user_data.get("last_claim", 0)
            time_passed = current_time - last_claim

            if time_passed < cooldown_seconds:
                next_claim_timestamp = last_claim + cooldown_seconds
                await ctx.send(
                    f"You have already claimed your daily reward!\n"
                    f"-# You can daily again <t:{next_claim_timestamp}:R>",
                    ephemeral=True,
                )
                return

        random_reward = random.randint(500, 10000)

        await cooldown_collection.update_one(
            {"_id": user_data.get("_id", user_id)},
            {
                "$set": {"last_claim": current_time},
                "$inc": {"coins": random_reward},
            },
            upsert=True,
        )

        await ctx.send(
            f"Here's your daily coin {coin_emoji} **+{random_reward:,}**\n"
            f"-# You can daily again <t:{current_time + cooldown_seconds}:R>"
        )


async def setup(bot):
    await bot.add_cog(Daily(bot))
