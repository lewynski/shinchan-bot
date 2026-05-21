import time
import discord
from discord.ext import commands

# --- CUSTOM EMOJI ---
PENDANT_EMOJI = "<:pendant:1506988725794771026>"

class ShopView(discord.ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=120)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Please run your own `/shop` command.", ephemeral=True)
            return False
        return True

    # The button sits outside the embed, has NO text/price, ONLY the pendant icon
    @discord.ui.button(label="", style=discord.ButtonStyle.secondary, emoji=discord.PartialEmoji.from_str(PENDANT_EMOJI))
    async def buy_pendant(self, interaction: discord.Interaction, button: discord.ui.Button):
        collection = interaction.client.db["daily_cooldowns"]
        user_data = await collection.find_one({"_id": interaction.user.id}) or {}
        
        coins = user_data.get("coins", 0)
        if coins < 5000:
            return await interaction.response.send_message("❌ You do not have enough coins for this item.", ephemeral=True)
            
        pendant_until = time.time() + 86400 # 24 hours
        
        await collection.update_one(
            {"_id": interaction.user.id},
            {"$inc": {"coins": -5000}, "$set": {"pendant_until": pendant_until}},
            upsert=True
        )
        
        # Disable the button and change the icon to a checkmark
        button.disabled = True
        button.emoji = "✅" 
        
        # Remove the embed and replace it with a clean success message
        text = (
            f"✅ **Pendant Equipped!**\n"
            f"-# You are completely immune to robberies for 24 hours."
        )
        await interaction.response.edit_message(content=text, embed=None, view=self)

class ShopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="shop", aliases=["sshop"], description="Browse the Black Market to buy exclusive items.")
    async def shop(self, ctx: commands.Context):
        
        # --- WHITE EMBED ---
        embed = discord.Embed(
            title="🛒 City Black Market",
            description="Buy exclusive perks to protect your wealth.",
            color=0xFFFFFF # This hex code makes the embed line pure white
        )
        
        # Item description inside the embed
        embed.add_field(
            name=f"{PENDANT_EMOJI} Magic Pendant - __5,000 Coins__",
            value="Grants total immunity from `/rob` attempts for **24 Hours**.",
            inline=False
        )

        view = ShopView(ctx.author.id)
        
        # Sends the white embed, and attaches the button (view) directly below it
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ShopCommand(bot))
