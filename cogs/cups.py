import random

import discord
from discord.ext import commands


class CupsGameView(discord.ui.View):
    def __init__(
        self,
        ctx,
        bet,
        collection,
        document_id,
        cash_emoji,
        money_emoji,
        skull_emoji,
        cup_emoji,
    ):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.bet = bet
        self.collection = collection
        self.document_id = document_id
        self.cash_emoji = cash_emoji
        self.money_emoji = money_emoji
        self.skull_emoji = skull_emoji
        self.cup_emoji = cup_emoji
        self.message = None
        self.finished = False

        self.cup_one.emoji = self.cup_emoji
        self.cup_two.emoji = self.cup_emoji
        self.cup_three.emoji = self.cup_emoji

        self.winning_cup = random.randint(0, 2)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "This isn't your street hustle.", ephemeral=True
            )
            return False
        return True

    def disable_buttons(self):
        for child in self.children:
            child.disabled = True

    def get_revealed_board(self):
        revealed = [self.skull_emoji, self.skull_emoji, self.skull_emoji]
        revealed[self.winning_cup] = self.money_emoji

        return (
            f"|  {revealed[0]}  |  {revealed[1]}  |  {revealed[2]}  |\n"
            f"   Cup 1      Cup 2      Cup 3"
        )

    async def process_choice(self, interaction: discord.Interaction, chosen_cup: int):
        if self.finished:
            return await interaction.response.send_message(
                "This hustle is already over.", ephemeral=True
            )

        self.finished = True
        self.disable_buttons()

        phrases = [
            "The dealer smiles like he knew the ending.",
            "The table goes quiet for half a second.",
            "Fast hands, faster money.",
            "The corner crowd pretends they were not watching.",
            "The shells stop moving. The city does not.",
        ]

        if chosen_cup == self.winning_cup:
            payout = self.bet * 3
            await self.collection.update_one(
                {"_id": self.document_id},
                {"$inc": {"coins": payout}},
                upsert=True,
            )

            result_text = (
                f"**You found it.** The dealer pays you "
                f"{self.cash_emoji} **{self.bet * 2:,}** profit."
            )
        else:
            result_text = (
                f"**Bust.** It was under Cup {self.winning_cup + 1}. "
                f"You lost your {self.cash_emoji} **{self.bet:,}** bet."
            )

        await interaction.response.edit_message(
            content=(
                f"**The Shell Hustle**\n\n"
                f"The dealer lifts the cups...\n\n"
                f"{self.get_revealed_board()}\n\n"
                f"{result_text}\n"
                f"-# {random.choice(phrases)}"
            ),
            view=self,
        )

    @discord.ui.button(label="Cup 1", style=discord.ButtonStyle.secondary)
    async def cup_one(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.process_choice(interaction, 0)

    @discord.ui.button(label="Cup 2", style=discord.ButtonStyle.secondary)
    async def cup_two(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.process_choice(interaction, 1)

    @discord.ui.button(label="Cup 3", style=discord.ButtonStyle.secondary)
    async def cup_three(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.process_choice(interaction, 2)

    async def on_timeout(self):
        if self.finished:
            return

        self.finished = True
        self.disable_buttons()

        if self.message:
            try:
                await self.message.edit(
                    content=(
                        f"**The Shell Hustle**\n\n"
                        f"**Timed out.** You hesitated too long and the dealer "
                        f"cleared the table.\n"
                        f"You lost your {self.cash_emoji} **{self.bet:,}** bet.\n"
                        f"-# The street keeps moving without you."
                    ),
                    view=self,
                )
            except discord.HTTPException:
                pass


class CupsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="cups",
        aliases=["shell", "monte"],
        description="Play Three-Card Monte against a street dealer.",
    )
    async def cups(self, ctx: commands.Context, bet: int):
        cash_emoji = "<a:cash:1506921225484767282>"

        if bet <= 0:
            return await ctx.send("You must bet a valid amount of coins.")
        if bet > 50000:
            return await ctx.send(
                f"The dealer refuses to handle that much cash. "
                f"Max bet is {cash_emoji} **50,000**."
            )

        collection = self.bot.db["daily_cooldowns"]
        user_id = int(ctx.author.id)

        user_data = await collection.find_one(
            {"$or": [{"_id": user_id}, {"_id": str(user_id)}]}
        ) or {}

        coins = user_data.get("coins", 0)
        document_id = user_data.get("_id", user_id)

        if coins < bet:
            return await ctx.send(
                f"You don't have enough capital. "
                f"You only have {cash_emoji} **{coins:,}**."
            )

        bet_update = await collection.update_one(
            {"_id": document_id, "coins": {"$gte": bet}},
            {"$inc": {"coins": -bet}},
        )

        if bet_update.modified_count == 0:
            return await ctx.send(
                "Your balance changed before the dealer could take the bet. Try again."
            )

        money_emoji = "<a:money:1507188967563591710>"
        skull_emoji = "<a:skull:1507193069575995504>"
        cup_emoji = "<a:cup:1509076339087376514>"

        initial_board = (
            f"|  {cup_emoji}  |  {cup_emoji}  |  {cup_emoji}  |\n"
            f"   Cup 1      Cup 2      Cup 3"
        )

        view = CupsGameView(
            ctx,
            bet,
            collection,
            document_id,
            cash_emoji,
            money_emoji,
            skull_emoji,
            cup_emoji,
        )

        view.message = await ctx.send(
            f"**The Shell Hustle**\n"
            f"Bet: {cash_emoji} **{bet:,}**\n\n"
            f"The dealer drops your cash and shuffles fast.\n\n"
            f"{initial_board}\n\n"
            f"-# Choose a cup before the table clears.",
            view=view,
        )


async def setup(bot):
    await bot.add_cog(CupsCommand(bot))
