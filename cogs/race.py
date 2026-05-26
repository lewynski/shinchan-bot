import asyncio
import random
from typing import Literal

import discord
from discord.ext import commands


class RaceCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="race",
        aliases=["betrace"],
        description="Bet on an underground Adventure Time street race.",
    )
    async def race(
        self,
        ctx: commands.Context,
        racer: Literal["finn", "bubble", "bmo"],
        bet: int,
    ):
        cash_emoji = "<a:cash:1506921225484767282>"

        if bet <= 0:
            return await ctx.send("You must bet a valid amount of coins.")
        if bet > 50000:
            return await ctx.send(
                f"The betting pool is capped. Max bet is {cash_emoji} **50,000**."
            )

        collection = self.bot.db["daily_cooldowns"]
        user_id = int(ctx.author.id)

        user_data = await collection.find_one(
            {"$or": [{"_id": user_id}, {"_id": str(user_id)}]}
        ) or {}

        coins = user_data.get("coins", 0)
        document_id = user_data.get("_id", user_id)

        if coins < bet:
            return await ctx.send(
                f"You don't have enough to bet that much. "
                f"You only have {cash_emoji} **{coins:,}**."
            )

        bet_update = await collection.update_one(
            {"_id": document_id, "coins": {"$gte": bet}},
            {"$inc": {"coins": -bet}},
        )

        if bet_update.modified_count == 0:
            return await ctx.send(
                "Your balance changed before the race started. Try again."
            )

        finn_emoji = "<a:fin:1508749987775774861>"
        bubble_emoji = "<a:bubble:1508749980918087790>"
        bmo_emoji = "<a:bmo:1508749925159010344>"

        racers_data = {
            "finn": {"emoji": finn_emoji, "pos": 0},
            "bubble": {"emoji": bubble_emoji, "pos": 0},
            "bmo": {"emoji": bmo_emoji, "pos": 0},
        }

        track_length = 20

        def get_track_display():
            lines = []
            for name, data in racers_data.items():
                position = min(data["pos"], track_length)
                path_behind = "-" * position
                path_ahead = "-" * (track_length - position)
                lines.append(
                    f"**{name.capitalize()}**\n"
                    f"`{path_behind}`{data['emoji']}`{path_ahead}` FINISH"
                )
            return "\n\n".join(lines)

        embed = discord.Embed(
            title="Underground Midnight Race",
            description=(
                f"You bet {cash_emoji} **{bet:,}** on **{racer.capitalize()}**.\n\n"
                f"{get_track_display()}"
            ),
            color=0x2B2D31,
        )
        msg = await ctx.send(embed=embed)

        winner = None

        while not winner:
            await asyncio.sleep(1.5)

            for name in racers_data:
                racers_data[name]["pos"] += random.randint(1, 4)

            finishers = [
                name
                for name, data in racers_data.items()
                if data["pos"] >= track_length
            ]

            if finishers:
                finishers.sort(key=lambda x: racers_data[x]["pos"], reverse=True)
                winner = finishers[0]

            embed.description = (
                f"You bet {cash_emoji} **{bet:,}** on **{racer.capitalize()}**.\n\n"
                f"{get_track_display()}"
            )
            await msg.edit(embed=embed)

        if winner == racer.lower():
            payout = bet * 2
            result_text = (
                f"**{winner.capitalize()}** crossed the finish line first. "
                f"You won {cash_emoji} **{bet:,}** profit."
            )
            color = discord.Color.green()
        else:
            payout = 0
            result_text = (
                f"**{winner.capitalize()}** won the race. "
                f"You lost your {cash_emoji} **{bet:,}** bet on {racer.capitalize()}."
            )
            color = discord.Color.red()

        if payout:
            await collection.update_one(
                {"_id": document_id},
                {"$inc": {"coins": payout}},
                upsert=True,
            )

        embed.color = color
        embed.description = (
            f"**THE RACE IS OVER!**\n\n{get_track_display()}\n\n{result_text}"
        )
        await msg.edit(embed=embed)


async def setup(bot):
    await bot.add_cog(RaceCommand(bot))
