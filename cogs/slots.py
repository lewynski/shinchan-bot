import random
import asyncio
import discord
from discord.ext import commands

class SlotsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="slots", aliases=["slot", "gamble"], description="Spin the underground slots to win big.")
    async def slots(self, ctx: commands.Context, bet: int):
        cash_emoji = "<a:cash:1506921225484767282>"
        demoncat_emoji = "<a:demoncat:1506995624879329490>"
        
        # --- Bet Validation ---
        if bet <= 0:
            return await ctx.send("❌ You must bet a valid amount of coins.")
            
        # UPDATE: Changed max bet to 50,000
        if bet > 50000:
            return await ctx.send(f"❌ The high rollers table is full. Max bet is {cash_emoji} **50,000**.")

        # --- Database Check ---
        collection = self.bot.db["users"]
        u_id = int(ctx.author.id)
        user_data = await collection.find_one({"_id": u_id}) or {}
        coins = user_data.get("coins", 0)

        if coins < bet:
            return await ctx.send(f"❌ You don't have enough to bet that much. You only have {cash_emoji} **{coins:,}**.")

        # --- Emojis ---
        MONEY = "<a:money:1507188967563591710>"
        CIGARETTE = "<a:cigarette:1507188969618804848>"
        PILL = "<a:pill:1507188971300589608>"
        PISTOL = "<a:pistol:1507188973427232789>"
        BLACKHEART = "<a:blackheart:1507188976065188001>"
        
        symbols = [MONEY, CIGARETTE, PILL, PISTOL, BLACKHEART]

        # --- Initial Spinning Message ---
        embed = discord.Embed(
            title="🎰 Underground Slots",
            description=f"**Bet:** {cash_emoji} {bet:,}\n\n[ ⬛ | ⬛ | ⬛ ]\n\n*Spinning the reels...*",
            color=0x2b2d31
        )
        msg = await ctx.send(embed=embed)

        await asyncio.sleep(2) 

        # --- The Roll ---
        s1 = random.choice(symbols)
        s2 = random.choice(symbols)
        s3 = random.choice(symbols)

        # --- Calculate Outcome ---
        if s1 == s2 == s3:
            multiplier = 10
            result_text = f"{demoncat_emoji} **JACKPOT!** You won {cash_emoji} **{bet * multiplier:,}**!"
            color = discord.Color.gold()
        elif s1 == s2 or s2 == s3 or s1 == s3:
            multiplier = 1
            result_text = f"**Close one.** You got your {cash_emoji} **{bet:,}** back."
            color = discord.Color.light_grey()
        else:
            multiplier = 0
            result_text = f"**Bust.** You lost {cash_emoji} **{bet:,}**."
            color = discord.Color.dark_red()

        # --- Database Update ---
        winnings = (bet * multiplier) - bet
        
        await collection.update_one(
            {"_id": u_id},
            {"$inc": {"coins": winnings}}
        )

        # --- Final Message Edit ---
        final_embed = discord.Embed(
            title="🎰 Underground Slots",
            description=f"**Bet:** {cash_emoji} {bet:,}\n\n**[ {s1} | {s2} | {s3} ]**\n\n{result_text}",
            color=color
        )
        final_embed.set_footer(text="The house always gets its cut.")
        
        await msg.edit(embed=final_embed)

async def setup(bot):
    await bot.add_cog(SlotsCommand(bot))
