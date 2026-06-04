import discord
import random
from discord.ext import commands


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="leaderboard",
        aliases=["lb", "top"],
        description="View the richest members in the city."
    )
    async def leaderboard(self, ctx: commands.Context):
        try:
            collection = self.bot.db["daily_cooldowns"]

            top_users = await collection.find(
                {"coins": {"$gt": 0}}
            ).sort("coins", -1).limit(25).to_list(length=25)

            if not top_users:
                return await ctx.send(
                    "❌ No users with coins were found in the database."
                )

            trophy_emoji = "🏆"
            cash_emoji = "💰"

            crowns = {
                1: "🥇",
                2: "🥈",
                3: "🥉",
            }

            embed = discord.Embed(
                title=f"{trophy_emoji} Hall of Fame",
                description=random.choice([
                    "Legends in the making.",
                    "The wealthiest in the city.",
                    "Respect the grind.",
                    "The top of the food chain."
                ]),
                color=discord.Color.gold()
            )

            if ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon.url)

            leaderboard_text = ""
            rank = 1

            for user_data in top_users:
                user_id = user_data.get("_id")
                coins = user_data.get("coins", 0)

                try:
                    user_id = int(user_id)
                except Exception:
                    continue

                member = ctx.guild.get_member(user_id)

                if member is None:
                    try:
                        member = await self.bot.fetch_user(user_id)
                        username = member.name
                    except Exception:
                        username = f"Unknown User ({user_id})"
                else:
                    username = member.display_name

                crown = crowns.get(rank, "🔹")

                leaderboard_text += (
                    f"{crown} **{rank}. {username}**\n"
                    f"└ {coins:,} {cash_emoji}\n\n"
                )

                rank += 1

                if rank > 10:
                    break

            embed.add_field(
                name="Current Standings",
                value=leaderboard_text,
                inline=False
            )

            await ctx.send(embed=embed)

        except Exception as e:
            print(f"LEADERBOARD ERROR: {e}")
            await ctx.send(f"❌ Error: `{e}`")


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
