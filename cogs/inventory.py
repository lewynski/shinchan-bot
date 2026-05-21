import discord
from discord.ext import commands
from discord.ui import View, Button


class InventoryView(View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id

    @discord.ui.button(
        label="Refresh",
        style=discord.ButtonStyle.secondary,
        emoji="🔄"
    )
    async def refresh_inventory(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(
                "This inventory panel is not yours.",
                ephemeral=True
            )

        await interaction.response.defer()


class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="inventory",
        aliases=["inv"],
        description="View your inventory and balance."
    )
    async def inventory(self, ctx: commands.Context):

        user_id = ctx.author.id
        coin_emoji = "<:coin:1506921225484767282>"

        # DATABASE
        collection = self.bot.db["daily_cooldowns"]

        user_data = await collection.find_one({"_id": user_id})

        if not user_data:
            user_data = {
                "coins": 0,
                "gems": 0,
                "level": 1,
                "items": []
            }

        # USER DATA
        coins = user_data.get("coins", 0)
        gems = user_data.get("gems", 0)
        level = user_data.get("level", 1)
        items = user_data.get("items", [])

        # ITEM DISPLAY
        if items:
            item_text = "\n".join(
                [f"• {item}" for item in items[:10]]
            )
        else:
            item_text = "`No registered items.`"

        # EMBED
        embed = discord.Embed(
            title="✦ VAULT INVENTORY",
            description=(
                f"Asset registry for {ctx.author.mention}\n"
                f"> Secure digital storage initialized."
            ),
            color=0x0F0F0F
        )

        # USER PROFILE
        embed.set_author(
            name=str(ctx.author),
            icon_url=ctx.author.display_avatar.url
        )

        # BALANCE FIELD
        embed.add_field(
            name="💰 Financial Assets",
            value=(
                f"```yaml\n"
                f"Credits : {coins:,}\n"
                f"Gems    : {gems:,}\n"
                f"Level   : {level}\n"
                f"```"
            ),
            inline=False
        )

        # CURRENCY
        embed.add_field(
            name="Currency",
            value=(
                f"{coin_emoji} **Coins:** `{coins:,}`\n"
                f"💎 **Gems:** `{gems:,}`"
            ),
            inline=True
        )

        # STATUS
        embed.add_field(
            name="Vault Status",
            value=(
                "```diff\n"
                "+ Operational\n"
                "+ Secured\n"
                "- No anomalies detected\n"
                "```"
            ),
            inline=True
        )

        # INVENTORY ITEMS
        embed.add_field(
            name="📦 Registered Assets",
            value=item_text,
            inline=False
        )

        # THUMBNAIL
        if ctx.guild and ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        # BANNER GIF
        embed.set_image(
            url="https://i.imgur.com/sHIxFaQ.gif"
        )

        # FOOTER
        embed.set_footer(
            text=f"Secure ID: {ctx.author.id}"
        )

        # SEND
        await ctx.send(
            embed=embed,
            view=InventoryView(user_id)
        )


async def setup(bot):
    await bot.add_cog(Inventory(bot))
