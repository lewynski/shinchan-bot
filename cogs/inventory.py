import discord
from discord.ext import commands
from discord import app_commands

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="inventory", aliases=["inv"], description="View your current balance and collected assets.")
    async def inventory(self, ctx: commands.Context):
        user_id = ctx.author.id
        
        # Access the collection storing daily data
        cooldown_collection = self.bot.db['daily_cooldowns']
        user_data = await cooldown_collection.find_one({"_id": user_id})
        
        # Check if the user has a balance history, otherwise default to 0
        # (Assuming each daily claim gives 1 coin for tracking)
        total_coins = 0
        if user_data:
            # If you haven't set up a dedicated coin field yet, we look for history 
            # or default to 1 for their active profile initialization
            total_coins = user_data.get("coins", 1)

        # Custom developer portal emoji string
        coin_emoji = "<:coin:1506921225484767282>"

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

### How to install:
1. Create a new file named `inventory.py` inside your `cogs/` folder.
2. Paste the script above into it and push it to GitHub. 

Railway will pick up the changes, compile the extension automatically, and sync both the `sinv` prefix shorthand and the `/inventory` slash menu globally.
