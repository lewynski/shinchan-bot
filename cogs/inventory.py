import discord
from discord.ext import commands
from discord import app_commands

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
            description=f"Personal vault overview for <@{ctx.author.id}>",
            color=0xFFFFFF
        )

        # We isolate the formatting backticks to prevent any editor parser glitches
        format_wrap = "```"
        ledger_text = f"{format_wrap}🏦 Liquid Balance: {total_coins:,} Credits{format_wrap}"
        currency_text = f"{coin_emoji} **Main Currency:** {total_coins:,} coins"

        # Construct grid layout fields
        embed.add_field(
            name="Financial Ledger", 
            value=ledger_text, 
            inline=False
        )
        
        embed.add_field(
            name="Currencies",
            value=currency_text,
            inline=True
        )

        embed.add_field(
            name="Inventory Status",
            value="`Vault Level 1` — No items registered.",
            inline=True
        )

        # Server Icon Positioning (Top Right)
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        # White Banner GIF Layout (Bottom)
        embed.set_image(url="[https://i.imgur.com/9lYEi9w.gif](https://i.imgur.com/9lYEi9w.gif)")

        # Subtle Footer
        embed.set_footer(
            text=f"Secure ID: {ctx.author.id}", 
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Inventory(bot))
