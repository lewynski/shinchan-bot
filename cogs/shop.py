import time
import discord
from discord.ext import commands

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
        user_data = await collection.find_one({"_id": interaction.user.id}) or {}
        coins = user_data.get("coins", 0)
        if coins < 5000:
            return await interaction.response.send_message(f"❌ You have {coins:,} coins. Need 5,000.", ephemeral=True)
            
        await collection.update_one({"_id": interaction.user.id}, {"$inc": {"coins": -5000}, "$set": {"pendant_until": time.time() + 86400}}, upsert=True)
        button.disabled = True
        button.emoji = "✅" 
        await interaction.response.edit_message(content="✅ **Pendant Equipped!**", embed=None, view=self)

    @discord.ui.button(label="", style=discord.ButtonStyle.secondary, emoji=discord.PartialEmoji.from_str(NECKLACE_EMOJI))
    async def buy_necklace(self, interaction: discord.Interaction, button: discord.ui.Button):
        collection = interaction.client.db["users"]
        user_data = await collection.find_one({"_id": interaction.user.id}) or {}
        coins = user_data.get("coins", 0)
        if user_data.get("necklace_until", 0) > time.time():
            return await interaction.response.send_message("❌ Already active!", ephemeral=True)
        if coins < 3000:
            return await interaction.response.send_message(f"❌ You have {coins:,} coins. Need 3,000.", ephemeral=True)
            
        await collection.update_one({"_id": interaction.user.id}, {"$inc": {"coins": -3000}, "$set": {"necklace_until": time.time() + 43200}}, upsert=True)
        button.disabled = True
        button.emoji = "✅"
        await interaction.response.edit_message(content="✅ **Necklace Purchased!**", embed=None, view=self)

async def setup(bot):
    await bot.add_cog(ShopCommand(bot)) # Add the command class similarly to previous examples
