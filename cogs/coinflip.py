import random
import asyncio
import discord
from discord.ext import commands

# --- COINFLIP VIEW (BUTTONS) ---
class CoinflipView(discord.ui.View):
    def __init__(self, author_id, bet):
        super().__init__(timeout=60)
        self.author_id = author_id
        self.bet = bet

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("This is not your bet! Run your own `/cf` command.", ephemeral=True)
            return False
        return True

    async def process_flip(self, interaction: discord.Interaction, choice: str):
        collection = interaction.client.db["daily_cooldowns"]
        
        # Emojis
        cash_emoji = "<a:cash:1506921225484767282>"
        coinflip_emoji = "<a:coinflip:1506997893972623451>"
        winner_emoji = "<a:winner:1506997895491223592>"
        defeat_emoji = "<a:defeat:1506997897059631114>"

        # 1. Instantly edit the message to show the toss animation and remove buttons
        await interaction.response.edit_message(
            content=f"{coinflip_emoji} Tossing the coin... You bet {cash_emoji} **{self.bet:,}** on **{choice.capitalize()}**.",
            view=None
        )

        # 2. Wait for dramatic effect
        await asyncio.sleep(2)

        # 3. Calculate Outcome
        landed = random.choice(["heads", "tails"])

        if choice == landed:
            # Win Logic
            await collection.update_one(
                {"_id": interaction.user.id},
                {"$inc": {"coins": self.bet}}
            )
            
            phrases = [
                "The coin lands perfectly in your favor.",
                "Beginner's luck, or pure skill?",
                "Don't spend it all in one place.",
                "Easy money. The streets respect a winner."
            ]
            
            text = (
                f"{winner_emoji} **You Won!**\n"
                f"It landed on **{landed.capitalize()}**! You doubled your money and won {cash_emoji} **{self.bet:,}**!\n"
                f"-# {random.choice(phrases)}"
            )
        else:
            # Lose Logic
            await collection.update_one(
                {"_id": interaction.user.id},
                {"$inc": {"coins": -self.bet}}
            )
            
            phrases = [
                "The house always wins... eventually.",
                "Better luck next time, gambler.",
                "Down bad. Want to try again?",
                "Ouch. That one is going to hurt the wallet."
            ]
            
            text = (
                f"{defeat_emoji} **You Lost!**\n"
                f"It landed on **{landed.capitalize()}**... You lost {cash_emoji} **{self.bet:,}**.\n"
                f"-# {random.choice(phrases)}"
            )

        # 4. Final reveal
        await interaction.message.edit(content=text)

    @discord.ui.button(label="Heads", style=discord.ButtonStyle.primary, emoji="🪙")
    async def btn_heads(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_flip(interaction, "heads")

    @discord.ui.button(label="Tails", style=discord.ButtonStyle.secondary, emoji="🪙")
    async def btn_tails(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.process_flip(interaction, "tails")


# --- MAIN COMMAND ---
class CoinflipCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="coinflip", 
        aliases=["cf", "flip"], 
        description="Bet your coins on heads or tails."
    )
    async def coinflip(self, ctx: commands.Context, bet: int):
        cash_emoji = "<a:cash:1506921225484767282>"
        
        # 1. Invalid bet check
        if bet <= 0:
            return await ctx.send("You must bet a valid amount of coins.")
            
        # 2. Maximum bet limit check
        if bet > 100000:
            return await ctx.send(f"The high rollers table is full. The maximum bet is {cash_emoji} **100,000**.")

        collection = self.bot.db["daily_cooldowns"]
        user_data = await collection.find_one({"_id": ctx.author.id}) or {}
        coins = user_data.get("coins", 0)
        
        # 3. Insufficient funds check
        if coins < bet:
            return await ctx.send(f"You don't have enough to bet that much. You only have {cash_emoji} **{coins:,}**.")

        # 4. Spawn the interactive button menu
        view = CoinflipView(ctx.author.id, bet)
        text = f"You are betting {cash_emoji} **{bet:,}**. Choose **Heads** or **Tails** below:"
        
        await ctx.send(content=text, view=view)

async def setup(bot):
    await bot.add_cog(CoinflipCommand(bot))
