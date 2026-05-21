import discord
from discord.ext import commands

class GiveCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Your specific Discord ID hardcoded for ultimate security
        self.admin_id = 879936602414133288 

    @commands.hybrid_command(
        name="give",
        aliases=["sgive"],
        description="[ADMIN] Give coins to a specific citizen."
    )
    async def give(self, ctx: commands.Context, member: discord.Member, amount: int):
        
        # 1. Strict Security Check
        if ctx.author.id != self.admin_id:
            # ephemeral=True hides the rejection message from the public chat
            return await ctx.send("❌ Access Denied. This is an admin-only command.", ephemeral=True)

        # 2. Database Connection
        collection = self.bot.db["daily_cooldowns"]
        
        # 3. Process the Transfer
        # $inc safely adds the amount to their current balance
        await collection.update_one(
            {"_id": member.id},
            {"$inc": {"coins": amount}},
            upsert=True
        )

        # 4. Success Message (Using your clean text style and animated emoji)
        cash_emoji = "<a:cash:1506921225484767282>"
        
        text = (
            f"🏦 **Central Bank Transfer**\n"
            f"Successfully transferred {cash_emoji} **{amount:,}** to {member.mention}."
        )
        
        await ctx.send(content=text)

async def setup(bot):
    await bot.add_cog(GiveCommand(bot))
