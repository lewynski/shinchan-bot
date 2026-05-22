import discord
import random
from discord.ext import commands


class ScratchCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="scratch",
        aliases=["scratcher", "ticket"],
        description="Buy a Black Market scratch ticket for 5,000 coins.",
    )
    async def scratch(self, ctx: commands.Context):
        cash_emoji = "<a:cash:1506921225484767282>"
        ticket_price = 5000

        collection = self.bot.db["daily_cooldowns"]
        user_id = int(ctx.author.id)

        user_data = await collection.find_one(
            {"$or": [{"_id": user_id}, {"_id": str(user_id)}]}
        ) or {}

        coins = user_data.get("coins", 0)

        if coins < ticket_price:
            return await ctx.send(
                f"You need {cash_emoji} **{ticket_price:,}** to buy a scratcher. "
                f"You only have {cash_emoji} **{coins:,}**."
            )

        MONEY = "<a:money:1507188967563591710>"
        PISTOL = "<a:pistol:1507188973427232789>"
        CIGARETTE = "<a:cigarette:1507188969618804848>"
        SKULL = "<a:skull:1507193069575995504>"

        symbols = [SKULL, CIGARETTE, PISTOL, MONEY]
        weights = [60, 22, 12, 6]

        grid = random.choices(symbols, weights=weights, k=9)

        winnings = 0
        result_msg = f"**Bust.** You lost {cash_emoji} **{ticket_price:,}**."

        if grid.count(MONEY) >= 3:
            winnings = 50000
            result_msg = (
                f"**JACKPOT!** You found 3 money stacks and won "
                f"{cash_emoji} **{winnings:,}**."
            )
        elif grid.count(PISTOL) >= 3:
            winnings = 15000
            result_msg = (
                f"**Great pull.** You found 3 pistols and won "
                f"{cash_emoji} **{winnings:,}**."
            )
        elif grid.count(CIGARETTE) >= 3:
            winnings = 5000
            result_msg = (
                f"**Break even.** You found 3 cigarettes and got back "
                f"{cash_emoji} **{winnings:,}**."
            )

        net_change = winnings - ticket_price

        await collection.update_one(
            {"_id": user_data.get("_id", user_id)},
            {"$inc": {"coins": net_change}},
            upsert=True,
        )

        row1 = f"|| {grid[0]} ||  || {grid[1]} ||  || {grid[2]} ||"
        row2 = f"|| {grid[3]} ||  || {grid[4]} ||  || {grid[5]} ||"
        row3 = f"|| {grid[6]} ||  || {grid[7]} ||  || {grid[8]} ||"

        phrases = [
            "The ticket smells like smoke and bad decisions.",
            "Three symbols can change the whole night.",
            "The black market does not print refunds.",
            "Scratch slow. Hope fast.",
            "The city watches every reveal.",
        ]

        await ctx.send(
            f"**Black Market Scratcher**\n"
            f"Ticket: {cash_emoji} **{ticket_price:,}**\n\n"
            f"{row1}\n{row2}\n{row3}\n\n"
            f"{result_msg}\n"
            f"-# {random.choice(phrases)}"
        )


async def setup(bot):
    await bot.add_cog(ScratchCommand(bot))
