import discord
import random
from discord.ext import commands

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="leaderboard", aliases=["lb", "top"], description="View the richest members in the city.")
    async def leaderboard(self, ctx: commands.Context):
        collection = self.bot.db["users"]
        
        # Fetch top 10 users, sorted by coins descending
        cursor = collection.find({"coins": {"$gt": 0}}).sort("coins", -1).limit(10)
        top_users = await cursor.to_list(length=10)
        
        if not top_users:
            return await ctx.send("The leaderboard is currently empty.")

        # Emojis
        trophy_emoji = "<a:trophy:1507185290173874176>"
        crowns = {
            1: "<:1crown:1507184842503098468>",
            2: "<:2crown:1507184840779235521>",
            3: "<a:3crown:1507184839206375565>" # Animated
        }
        
        phrases = [
            "Legends in the making.",
            "The wealthiest in the city.",
            "Respect the grind.",
            "The top of the food chain."
        ]

        embed = discord.Embed(
            title=f"{trophy_emoji} Hall of Fame",
            description=f"-# {random.choice(phrases)}",
            color=0xFFFFFF # White
        )

        leaderboard_text = ""
        for i, user_data in enumerate(top_users, 1):
            user_id = user_data.get("_id")
            coins = user_data.get("coins", 0)
            
            # Get user name
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else f"User {user_id}"
            
            # Select crown
            crown = crowns.get(i, crowns[3]) # Use 3rd crown for 3-10
            
            leaderboard_text += f"{crown} **{i}. {name}** — {coins:,} coins\n"

        embed.add_field(name="Current Standings", value=leaderboard_text, inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
