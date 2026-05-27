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

        cursor = collection.find({"coins": {"$gt": 0}}).sort("coins", -1).limit(25)
        top_users = await cursor.to_list(length=25)

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
        rank = 1

        for user_data in top_users:
            raw_user_id = user_data.get("_id")
            coins = user_data.get("coins", 0)

            try:
                user_id = int(raw_user_id)
            except (TypeError, ValueError):
                continue

            member = ctx.guild.get_member(user_id)

            if member is None:
                try:
                    member = await ctx.guild.fetch_member(user_id)
                except (discord.NotFound, discord.HTTPException):
                    continue

            crown = crowns.get(rank, crowns[3])
            leaderboard_text += (
                f"{crown} **{rank}. {member.display_name}** - {coins:,} {cash_emoji}\n"
            )

            rank += 1

            if rank > 10:
                break

        if not leaderboard_text:
            return await ctx.send("The leaderboard is currently empty for this server.")

        embed.add_field(name="Current Standings", value=leaderboard_text, inline=False)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
