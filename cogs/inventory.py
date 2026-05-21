import discord
from discord.ext import commands


class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="inventory",
        aliases=["inv"],
        description="View your inventory and account assets."
    )
    async def inventory(self, ctx: commands.Context):

        user_id = ctx.author.id

        # Custom Currency Emoji
        coin_emoji = "<:coin:1506921225484767282>"

        # Database Collection
        collection = self.bot.db["daily_cooldowns"]

        # Fetch User Data
        user_data = await collection.find_one({"_id": user_id})

        # Default Values
        if not user_data:
            user_data = {
                "coins": 0,
                "gems": 0,
                "level": 1,
                "items": []
            }

        coins = user_data.get("coins", 0)
        gems = user_data.get("gems", 0)
        level = user_data.get("level", 1)
        items = user_data.get("items", [])

        # Inventory List
        if items:
            inventory_text = "\n".join(
                f"• {item}" for item in items[:15]
            )
        else:
            inventory_text = "No registered assets."

        # Main Embed
        embed = discord.Embed(
            title="Asset Management System",
            description=(
                f"Official inventory overview for "
                f"{ctx.author.mention}"
            ),
            color=0xFFFFFF
        )

        # User Avatar
        embed.set_author(
            name=str(ctx.author),
            icon_url=ctx.author.display_avatar.url
        )

        # Financial Overview
        embed.add_field(
            name="Financial Overview",
            value=(
                f"{coin_emoji} Currency Balance: "
                f"**{coins:,} Coins**\n"
                f"💎 Premium Assets: "
                f"**{gems:,} Gems**"
            ),
            inline=False
        )

        # Account Information
        embed.add_field(
            name="Account Information",
            value=(
                f"Account Level: **{level}**\n"
                f"Registered Assets: **{len(items)}**"
            ),
            inline=False
        )

        # Inventory Assets
        embed.add_field(
            name="Registered Inventory",
            value=inventory_text,
            inline=False
        )

        # Server Icon
        if ctx.guild and ctx.guild.icon:
            embed.set_thumbnail(
                url=ctx.guild.icon.url
            )

        # Banner Image
        embed.set_image(
            url="https://i.imgur.com/sHIxFaQ.gif"
        )

        # Footer
        embed.set_footer(
            text=f"Secure Account ID: {ctx.author.id}"
        )

        # Send
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Inventory(bot))
