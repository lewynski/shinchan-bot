import discord
import random
from discord.ext import commands


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="leaderboard",
        aliases=["lb", "top"],
        description="View the richest members in the city.",
    )
    async def leaderboard(self, ctx: commands.Context):
        collection = self.bot.db["daily_cooldowns"]

        cursor = collection.find({"coins": {"$gt": 0}}).sort("coins", -1).limit(10)
        top_users = await cursor.to_list(length=10)

        if not top_users:
            return await ctx.send("The leaderboard is currently empty.")

        trophy_emoji = "<a:trophy:1507185290173874176>"
        cash_emoji = "<a:cash:1506921225484767282>"

        crowns = {
            1: "<:1crown:1507184842503098468>",
            2: "<:2crown:1507184840779235521>",
            3: "<a:3crown:1507184839206375565>",
        }

        phrases = [
            "Legends in the making.",
            "The wealthiest in the city.",
            "Respect the grind.",
            "The top of the food chain.",
        ]

        embed = discord.Embed(
            title=f"{trophy_emoji} Hall of Fame",
            description=f"-# {random.choice(phrases)}",
            color=0xFFFFFF,
        )

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        leaderboard_text = ""

        for i, user_data in enumerate(top_users, 1):
            raw_user_id = user_data.get("_id")
            coins = user_data.get("coins", 0)

            try:
                user_id = int(raw_user_id)
            except (TypeError, ValueError):
                user_id = None

            member = ctx.guild.get_member(user_id) if user_id else None

            if member is None and user_id:
                try:
                    member = await ctx.guild.fetch_member(user_id)
                except discord.NotFound:
                    member = None
                except discord.HTTPException:
                    member = None

            name = member.display_name if member else f"User {raw_user_id}"
            crown = crowns.get(i, crowns[3])

            leaderboard_text += (
                f"{crown} **{i}. {name}** - {coins:,} {cash_emoji}\n"
            )

        embed.add_field(name="Current Standings", value=leaderboard_text, inline=False)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
