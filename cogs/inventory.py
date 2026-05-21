import discord
from discord.ext import commands
from discord import app_commands

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Added aliases=["inv"] so typing 'sinv' works perfectly alongside 'sinventory'
    @commands.hybrid_command(name="inventory", aliases=["inv"], description="View your current balance and collected assets.")
    async def inventory(self, ctx: commands.Context):
        user_id = ctx.author.id
        coin_emoji = "<:coin:1506921225484767282>"
        
        cooldown_collection = self.bot.db['daily_cooldowns']
        user_data = await cooldown_collection.find_one({"_id": user_id})
        
        # Pull the absolute coin value from the database, default to 0 if new user
        total_coins = user_data.get("coins", 0) if user_data else 0

        # Formal Minimalist Design (Pure White Accent)
        embed = discord.Embed(
            title="A S S E T  M A N A G E M E N T",
            description=f"Personal vault overview for {ctx.author.mention}",
            color=0xFFFFFF
        )

        # Structured Ledger Fields
        embed.add_field(
            name="Financial Ledger", 
            value=f"
http://googleusercontent.com/immersive_entry_chip/0
