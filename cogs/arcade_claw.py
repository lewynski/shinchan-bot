import asyncio
import random

import discord
from discord.ext import commands


class ClawMachineView(discord.ui.View):
    def __init__(self, ctx, collection, document_id, cost, cash_emoji):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.collection = collection
        self.document_id = document_id
        self.cost = cost
        self.cash_emoji = cash_emoji
        self.finished = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "This is not your machine. Run `/arcade_claw` to spawn your own.",
                ephemeral=True,
            )
            return False
        return True

    def disable_buttons(self):
        for child in self.children:
            child.disabled = True

    @discord.ui.button(
        label="Drop Claw",
        style=discord.ButtonStyle.blurple,
        emoji="🕹️",
    )
    async def btn_drop(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.finished:
            return await interaction.response.send_message(
                "This machine already finished its run.", ephemeral=True
            )

        self.finished = True
        self.disable_buttons()

        await interaction.response.edit_message(
            content=(
                f"**Retro Arcade Claw**\n"
                f"Cost: {self.cash_emoji} **{self.cost:,}**\n\n"
                f"The claw slides over the glass...\n"
                f"-# The machine hums like it knows your balance."
            ),
            view=self,
        )
        await asyncio.sleep(1.3)

        await interaction.message.edit(
            content=(
                f"**Retro Arcade Claw**\n"
                f"Cost: {self.cash_emoji} **{self.cost:,}**\n\n"
                f"**The claw is descending...**\n"
                f"-# Whirrrrr..."
            ),
            view=self,
        )
        await asyncio.sleep(1.3)

        await interaction.message.edit(
            content=(
                f"**Retro Arcade Claw**\n"
                f"Cost: {self.cash_emoji} **{self.cost:,}**\n\n"
                f"**It grabbed something. Pulling up...**\n"
                f"-# Clank. Clank. The arcade holds its breath."
            ),
            view=self,
        )
        await asyncio.sleep(1.3)

        outcomes = ["loss", "common", "jackpot"]
        weights = [60, 35, 5]
        result = random.choices(outcomes, weights=weights, k=1)[0]

        phrases = [
            "The cabinet lights flicker like tiny witnesses.",
            "Somewhere behind the glass, luck changes lanes.",
            "The arcade eats coins and whispers promises.",
            "One clean grab can fix the whole night.",
            "The machine pretends it is fair. Charming little liar.",
        ]

        if result == "loss":
            prize = random.choice(
                ["Smelly Sock", "Empty Tin Can", "Literal Rock", "Old Bone"]
            )
            result_text = (
                f"**The claw slipped.** You pulled up a **{prize}**.\n"
                f"You lost your {self.cash_emoji} **{self.cost:,}**."
            )

        elif result == "common":
            payout = 500
            prize = random.choice(
                [
                    "Cute Plushie",
                    "Retro Space Invader",
                    "Power-up Mushroom",
                    "Fancy Ribbon",
                ]
            )
            await self.collection.update_one(
                {"_id": self.document_id},
                {"$inc": {"coins": payout}},
                upsert=True,
            )
            result_text = (
                f"**Nice grab.** The chute drops a **{prize}**.\n"
                f"You won {self.cash_emoji} **{payout:,}**."
            )

        else:
            payout = 5000
            prize = random.choice(
                ["Shining Diamond", "Royal Crown", "Legendary Golden Ticket"]
            )
            await self.collection.update_one(
                {"_id": self.document_id},
                {"$inc": {"coins": payout}},
                upsert=True,
            )
            result_text = (
                f"**JACKPOT.** The claw locks onto a **{prize}**.\n"
                f"You won {self.cash_emoji} **{payout:,}**."
            )

        await interaction.message.edit(
            content=(
                f"**Retro Arcade Claw**\n\n"
                f"{result_text}\n"
                f"-# {random.choice(phrases)}"
            ),
            view=None,
        )
        self.stop()

    async def on_timeout(self):
        if self.finished:
            return

        self.finished = True
        self.disable_buttons()

        try:
            await self.message.edit(
                content=(
                    f"**Retro Arcade Claw**\n\n"
                    f"**Timed out.** The machine swallowed your "
                    f"{self.cash_emoji} **{self.cost:,}** and went quiet.\n"
                    f"-# The arcade does not offer refunds."
                ),
                view=self,
            )
        except (AttributeError, discord.HTTPException):
            pass


class ArcadeGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="arcade_claw",
        description="Play the retro pixel claw machine.",
    )
    async def arcade_claw(self, ctx: commands.Context):
        cash_emoji = "<a:cash:1506921225484767282>"
        cost = 100

        collection = self.bot.db["daily_cooldowns"]
        user_id = int(ctx.author.id)

        user_data = await collection.find_one(
            {"$or": [{"_id": user_id}, {"_id": str(user_id)}]}
        ) or {}

        coins = user_data.get("coins", 0)
        document_id = user_data.get("_id", user_id)

        if coins < cost:
            return await ctx.send(
                f"You need {cash_emoji} **{cost:,}** to play. "
                f"You only have {cash_emoji} **{coins:,}**."
            )

        pay_to_play = await collection.update_one(
            {"_id": document_id, "coins": {"$gte": cost}},
            {"$inc": {"coins": -cost}},
        )

        if pay_to_play.modified_count == 0:
            return await ctx.send(
                "Your balance changed before the machine could start. Try again."
            )

        view = ClawMachineView(ctx, collection, document_id, cost, cash_emoji)

        view.message = await ctx.send(
            f"**Retro Arcade Claw**\n"
            f"Cost: {cash_emoji} **{cost:,}**\n\n"
            f"The glass is scratched. The claw is crooked. The prize pit is glowing.\n\n"
            f"-# Press the button and trust the machine exactly as much as it deserves.",
            view=view,
        )


async def setup(bot):
    await bot.add_cog(ArcadeGame(bot))
