import discord
from discord.ext import commands

class CashCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="cash", aliases=["bal", "balance", "scash"], description="Check your cash balance.")
    async def cash(self, ctx: commands.Context):
        collection = self.bot.db["users"]
        # Use _id to match your MongoDB structure
        user_data = await collection.find_one({"_id": ctx.author.id}) or {}
        
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
