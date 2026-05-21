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
        description="Bet your coins on heads or tails."
    )
    # Added 'choice' parameter so users must pick heads or tails
    async def coinflip(self, ctx: commands.Context, choice: str, bet: int):
        cash_emoji = "<a:cash:1506921225484767282>"
        
        # 1. Choice validation
        choice = choice.lower()
        if choice not in ["heads", "tails", "h", "t"]:
            return await ctx.send("You must choose either `heads` or `tails`. Example: `/cf heads 500`")
            
        # Normalize h/t to heads/tails
        if choice == "h": choice = "heads"
        if choice == "t": choice = "tails"
        
        # 2. Invalid bet check
        if bet <= 0:
            return await ctx.send("You must bet a valid amount of coins.")
            
        # 3. Maximum bet limit check
        if bet > 100000:
            return await ctx.send(f"The high rollers table is full. The maximum bet is {cash_emoji} **100,000**.")

        collection = self.bot.db["daily_cooldowns"]
        user_data = await collection.find_one({"_id": ctx.author.id}) or {}
        
        coins = user_data.get("coins", 0)
        
        # 4. Insufficient funds check
        if coins < bet:
            return await ctx.send(f"You don't have enough to bet that much. You only have {cash_emoji} **{coins:,}**.")

        # --- CUSTOM EMOJIS ---
        coinflip_emoji = "<a:coinflip:1506997893972623451>"
        winner_emoji = "<a:winner:1506997895491223592>"
        defeat_emoji = "<a:defeat:1506997897059631114>"

        # Send the suspenseful flipping message with their choice included
        flip_msg = await ctx.send(f"{coinflip_emoji} Tossing the coin... You bet {cash_emoji} **{bet:,}** on **{choice.capitalize()}**.")

        # Wait 2 seconds for dramatic effect
        await asyncio.sleep(2)

        # Calculate Outcome (The actual coin flip)
        landed = random.choice(["heads", "tails"])

        if choice == landed:
            # Add the bet amount to their balance
            await collection.update_one(
                {"_id": ctx.author.id},
                {"$inc": {"coins": bet}}
            )
            
            phrases = [
                "The coin lands perfectly in your favor.",
                "Beginner's luck, or pure skill?",
                "Don't spend it all in one place.",
                "Easy money. The streets respect a winner."
            ]
            
            text = (
                f"{winner_emoji} **You Won!**\n"
                f"It landed on **{landed.capitalize()}**! You doubled your money and won {cash_emoji} **{bet:,}**!\n"
                f"-# {random.choice(phrases)}"
            )
            
        else:
            # Deduct the bet amount from their balance
            await collection.update_one(
                {"_id": ctx.author.id},
                {"$inc": {"coins": -bet}}
            )
            
            phrases = [
                "The house always wins... eventually.",
                "Better luck next time, gambler.",
                "Down bad. Want to try again?",
                "Ouch. That one is going to hurt the wallet."
            ]
            
            text = (
                f"{defeat_emoji} **You Lost!**\n"
                f"It landed on **{landed.capitalize()}**... You lost {cash_emoji} **{bet:,}**.\n"
                f"-# {random.choice(phrases)}"
            )

        # Edit the original message to reveal the result
        await flip_msg.edit(content=text)

async def setup(bot):
    await bot.add_cog(CoinflipCommand(bot))
