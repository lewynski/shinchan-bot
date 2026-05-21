import time
import discord
from discord.ext import commands

# --- CUSTOM EMOJIS ---
PENDANT_EMOJI = "<:pendant:1506988725794771026>"
NECKLACE_EMOJI = "<:necklace:1507010305149108224>"

class ShopView(discord.ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=120)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Please run your own `/shop` command.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="", style=discord.ButtonStyle.secondary, emoji=discord.PartialEmoji.from_str(PENDANT_EMOJI))
    async def buy_pendant(self, interaction: discord.Interaction, button: discord.ui.Button):
        collection = interaction.client.db["users"]
        user_data = await collection.find_one({"user_id": interaction.user.id}) or {}
        
        # Check 'coins' field
        coins = user_data.get("coins", 0)
        if coins < 5000:
            return await interaction.response.send_message(f"❌ You do not have enough coins. You have {coins:,}.", ephemeral=True)
            
        pendant_until = time.time() + 86400 # 24 hours
        await collection.update_one(
            {"user_id": interaction.user.id},
            {"$inc": {"coins": -5000}, "$set": {"pendant_until": pendant_until}},
            upsert=True
        )
        
        button.disabled = True
        button.emoji = "✅" 
        await interaction.response.edit_message(content="✅ **Pendant Equipped!** -# Immune to robberies for 24 hours.", embed=None, view=self)

    @discord.ui.button(label="", style=discord.ButtonStyle.secondary, emoji=discord.PartialEmoji.from_str(NECKLACE_EMOJI))
    async def buy_necklace(self, interaction: discord.Interaction, button: discord.ui.Button):
        collection = interaction.client.db["users"]
        user_data = await collection.find_one({"user_id": interaction.user.id}) or {}
        
        # Check 'coins' field
        coins = user_data.get("coins", 0)
        necklace_until = user_data.get("necklace_until", 0)
        
        if necklace_until > time.time():
            return await interaction.response.send_message("❌ You already have an active necklace!", ephemeral=True)
        if coins < 3000:
            return await interaction.response.send_message(f"❌ You do not have enough coins. You have {coins:,}.", ephemeral=True)
            
        new_expiry = time.time() + 43200 # 12 hours
        await collection.update_one(
            {"user_id": interaction.user.id},
            {"$inc": {"coins": -3000}, "$set": {"necklace_until": new_expiry}},
            upsert=True
        )
        
        button.disabled = True
        button.emoji = "✅"
        await interaction.response.edit_message(content="✅ **Necklace Purchased!** -# Enjoy double voice earnings for 12 hours.", embed=None, view=self)

class ShopCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="shop", description="Browse the Black Market to buy exclusive items.")
    async def shop(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🛒 City Black Market",
            description="Buy exclusive perks to enhance your wealth.",
            color=0xFFFFFF
        )
        embed.add_field(
            name=f"{PENDANT_EMOJI} Magic Pendant - __5,000 Coins__",
            value="Grants total immunity from `/rob` attempts for **24 Hours**.",
            inline=False
        )
        embed.add_field(
            name=f"{NECKLACE_EMOJI} Voice Necklace - __3,000 Coins__",
            value="Boosts earnings in voice channels to **6,000 per 15 mins** for **12 Hours**.",
            inline=False
        )
        view = ShopView(ctx.author.id)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ShopCommand(bot))
