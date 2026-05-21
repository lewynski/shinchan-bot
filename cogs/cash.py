import discord
from discord.ext import commands

class CashCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="cash", 
        aliases=["bal", "balance", "scash"], 
        description="Check your cash balance."
    )
    async def cash(self, ctx: commands.Context):
        # 1. Look in the 'users' collection instead of 'daily_cooldowns'
        collection = self.bot.db["users"]
        
        # 2. Look for the document using 'user_id'
        user_data = await collection.find_one({"user_id": ctx.author.id}) or {}
        
        # 3. Retrieve 'coins' from the user document
        coins = user_data.get("coins", 0)
        
        cash_emoji = "<a:cash:1506921225484767282>"
        demoncat_emoji = "<a:demoncat:1506995624879329490>"
        
        text = (
            f"{demoncat_emoji} You currently have {cash_emoji} **{coins:,}** cash.\n"
            f"-# Watch your pockets. The streets aren't always safe."
        )
            
        await ctx.send(content=text)

async def setup(bot):
    await bot.add_cog(CashCommand(bot))
