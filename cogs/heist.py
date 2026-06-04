import asyncio
import random

import discord
from discord.ext import commands


class HeistView(discord.ui.View):
    def __init__(self, ctx, collection, document_id, bet, cash_emoji, target_freq):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.collection = collection
        self.document_id = document_id
        self.bet = bet
        self.cash_emoji = cash_emoji
        self.target_freq = target_freq
        self.current_freq = None
        self.locked = False
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "This is not your heist. Run `/heist` to start your own.",
                ephemeral=True,
            )
            return False
        return True

    def disable_buttons(self):
        for child in self.children:
            child.disabled = True

    @discord.ui.button(
        label="Lock Signal",
        style=discord.ButtonStyle.danger,
        emoji="🔒",
    )
    async def btn_lock(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.locked:
            return await interaction.response.send_message(
                "This heist is already over.", ephemeral=True
            )

        self.locked = True
        self.disable_buttons()

        phrases = [
            "The signal vanishes into the city grid.",
            "Somewhere, a firewall starts sweating.",
            "The terminal blinks like it saw too much.",
            "Fast hands, clean signal, no witnesses.",
            "The bank alarm thinks about screaming.",
            "The transfer disappears before anyone can blink.",
        ]

        if self.current_freq == self.target_freq:
            payout = self.bet * 3
            await self.collection.update_one(
                {"_id": self.document_id},
                {"$inc": {"coins": payout}},
                upsert=True,
            )
            result_text = (
                f"**Heist successful.** You matched the signal perfectly.\n"
                f"You won {self.cash_emoji} **{self.bet * 2:,}** profit."
            )
        else:
            result_text = (
                f"**Heist failed.** The trace hit before the transfer cleared.\n"
                f"You lost your {self.cash_emoji} **{self.bet:,}** wager."
            )

        await interaction.response.edit_message(
            content=(
                f"**Signal Heist**\n"
                f"Bet: {self.cash_emoji} **{self.bet:,}**\n\n"
                f"Target: `{self.target_freq}` MHz\n"
                f"Locked: `{self.current_freq}` MHz\n\n"
                f"{result_text}\n"
                f"-# {random.choice(phrases)}"
            ),
            view=self,
        )
        self.stop()

    async def on_timeout(self):
        if self.locked:
            return

        self.locked = True
        self.disable_buttons()

        timeout_phrases = [
            "The wire goes cold. The city keeps humming.",
            "The bank transfer slips through your fingers.",
            "The signal dies before the money moves.",
            "Too slow. The system already forgot your name.",
        ]

        if not self.message:
            return

        try:
            await self.message.edit(
                content=(
                    f"**Signal Heist**\n"
                    f"Bet: {self.cash_emoji} **{self.bet:,}**\n\n"
                    f"**Connection timed out.** The bank transfer completed before "
                    f"you locked the signal.\n"
                    f"You lost your {self.cash_emoji} **{self.bet:,}** wager.\n"
                    f"-# {random.choice(timeout_phrases)}"
                ),
                view=self,
            )
        except discord.HTTPException:
            pass


class HeistGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="heist",
        description="Hack the bank frequency to intercept funds.",
    )
    async def heist(self, ctx: commands.Context, bet: int):
        cash_emoji = "<a:cash:1506921225484767282>"

        if bet <= 0:
            return await ctx.send("You must wager a valid amount of cash.")
        if bet > 50000:
            return await ctx.send(
                f"The heist crew refuses that heat. Max wager is {cash_emoji} **50,000**."
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
                f"You need {cash_emoji} **{bet:,}** for this heist. "
                f"You only have {cash_emoji} **{coins:,}**."
            )

        wager_update = await collection.update_one(
            {"_id": document_id, "coins": {"$gte": bet}},
            {"$inc": {"coins": -bet}},
        )

        if wager_update.modified_count == 0:
            return await ctx.send(
                "Your balance changed before the heist started. Try again."
            )

        target_freq = round(random.uniform(95.0, 105.0), 1)
        view = HeistView(ctx, collection, document_id, bet, cash_emoji, target_freq)

        view.message = await ctx.send(
            f"**Signal Heist**\n"
            f"Bet: {cash_emoji} **{bet:,}**\n\n"
            f"Target: `{target_freq}` MHz\n"
            f"Current: `--.-` MHz\n\n"
            f"-# Lock the signal when the current frequency matches the target.",
            view=view,
        )

        frequencies = [
            round(target_freq + random.uniform(-3.0, 3.0), 1) for _ in range(8)
        ]
        frequencies.insert(random.randint(2, 6), target_freq)

        for freq in frequencies:
            if view.locked:
                break

            view.current_freq = freq

            try:
                await view.message.edit(
                    content=(
                        f"**Signal Heist**\n"
                        f"Bet: {cash_emoji} **{bet:,}**\n\n"
                        f"Target: `{target_freq}` MHz\n"
                        f"Current: `{freq}` MHz\n\n"
                        f"-# Wait for the match. Then lock it."
                    ),
                    view=view,
                )
            except discord.NotFound:
                break

            await asyncio.sleep(1.5)

        if not view.locked:
            view.locked = True
            view.disable_buttons()

            timeout_phrases = [
                "The wire goes cold. The city keeps humming.",
                "The bank transfer slips through your fingers.",
                "The signal dies before the money moves.",
                "Too slow. The system already forgot your name.",
            ]

            await view.message.edit(
                content=(
                    f"**Signal Heist**\n"
                    f"Bet: {cash_emoji} **{bet:,}**\n\n"
                    f"**Connection timed out.** The bank transfer completed before "
                    f"you locked the signal.\n"
                    f"You lost your {cash_emoji} **{bet:,}** wager.\n"
                    f"-# {random.choice(timeout_phrases)}"
                ),
                view=view,
            )


async def setup(bot):
    await bot.add_cog(HeistGame(bot))
