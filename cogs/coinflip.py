import random
import asyncio
import discord
from discord.ext import commands

class CoinflipCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="coinflip", 
        aliases=["cf", "flip"], 
        description="Bet your coins on a 50/50 coin flip."
    )
    async def coinflip(self, ctx: commands.Context, bet: int):
        # Define the cash emoji right away so we can use it in our error messages
        cash_emoji = "<a:cash:1506921225484767282>"
        
        # 1. Invalid bet check
        if bet <= 0:
            return await ctx.send("You must bet a valid amount of coins.")
            
        # 2. Maximum bet limit check
        if bet > 100000:
            return await ctx.send(f"The high rollers table is full. The maximum bet is {cash_emoji} **100,000**.")

        collection = self.bot.db["daily_cooldowns"]
        user_data = await collection.find_one({"_id": ctx.author.id}) or {}
        
        coins = user_data.get("coins", 0)
        
        # 3. Insufficient funds check (Removed the X emoji)
        if coins < bet:
            return await ctx.send(f"You don't have enough to bet that much. You only have {cash_emoji} **{coins:,}**.")

        # --- CUSTOM EMOJIS ---
        coinflip_emoji = "<a:coinflip:1506997893972623451>"
        winner_emoji = "<a:winner:1506997895491223592>"
        defeat_emoji = "<a:defeat:1506997897059631114>"

        # Send the suspenseful flipping message
        flip_msg = await ctx.send(f"{coinflip_emoji} Tossing the coin for {cash_emoji} **{bet:,}**...")

        # Wait 2 seconds for dramatic effect
        await asyncio.sleep(2)

        # Calculate 50/50 Outcome
        outcome = random.choice(["win", "lose"])

        if outcome == "win":
            # Add the bet amount to their balance
            await collection.update_one(
                {"_id": ctx.author.id},
                {"$inc": {"coins": bet}}
            )
            
            # Random victory phrases
            phrases = [
                "The coin lands perfectly in your favor.",
                "Beginner's luck, or pure skill?",
                "Don't spend it all in one place.",
                "Easy money. The streets respect a winner."
            ]
            
            text = (
                f"{winner_emoji} **You Won!**\n"
                f"The coin landed in your favor. You doubled your money and won {cash_emoji} **{bet:,}**!\n"
                f"-# {random.choice(phrases)}"
            )
            
        else:
            # Deduct the bet amount from their balance
            await collection.update_one(
                {"_id": ctx.author.id},
                {"$inc": {"coins": -bet}}
            )
            
            # Random defeat phrases
            phrases = [
                "The house always wins... eventually.",
                "Better luck next time, gambler.",
                "Down bad. Want to try again?",
                "Ouch. That one is going to hurt the wallet."
            ]
            
            text = (
                f"{defeat_emoji} **You Lost!**\n"
                f"The coin betrayed you. You lost {cash_emoji} **{bet:,}**...\n"
                f"-# {random.choice(phrases)}"
            )

        # Edit the original message to reveal the result
        await flip_msg.edit(content=text)

async def setup(bot):
    await bot.add_cog(CoinflipCommand(bot))
