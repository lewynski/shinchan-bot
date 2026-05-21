import discord
from discord.ext import commands


class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="inventory",
        aliases=["inv"],
        description="View your lifestyle profile and assets."
    )
    async def inventory(self, ctx: commands.Context):

        user_id = ctx.author.id
        coin_emoji = "<:coin:1506921225484767282>"

        # DATABASE
        collection = self.bot.db["daily_cooldowns"]
        user_data = await collection.find_one({"_id": user_id})

        # DEFAULT VALUES
        if not user_data:
            user_data = {
                "coins": 0,
                "gems": 0,
                "level": 1,
                "items": []
            }

        # DATA
        coins = user_data.get("coins", 0)
        gems = user_data.get("gems", 0)
        level = user_data.get("level", 1)
        items = user_data.get("items", [])

        # NET WORTH RANK
        if coins >= 1_000_000:
            status = "Elite Millionaire"
        elif coins >= 100_000:
            status = "Luxury Citizen"
        elif coins >= 10_000:
            status = "Wealthy Resident"
        else:
            status = "Average Citizen"

        # INVENTORY FORMAT
        if items:
            inventory_text = "\n".join(
                f"• {item}" for item in items[:10]
            )
        else:
            inventory_text = (
                "No luxury assets or properties owned."
            )

        # EMBED
        embed = discord.Embed(
            title="BitLife • Lifestyle Summary",
            description=(
                f"Profile overview for {ctx.author.mention}\n\n"
                f"Age • `21`\n"
                f"Status • `{status}`\n"
                f"Reputation • `Stable`\n"
                f"Career • `Unemployed`"
            ),
            color=0x1A1A1A
        )

        # PROFILE
        embed.set_author(
            name=str(ctx.author),
            icon_url=ctx.author.display_avatar.url
        )

        # FINANCIALS
        embed.add_field(
            name="💰 Finances",
            value=(
                f"{coin_emoji} Cash Balance\n"
                f"┗ **{coins:,} Coins**\n\n"

                f"💎 Premium Currency\n"
                f"┗ **{gems:,} Gems**\n\n"

                f"📈 Lifestyle Level\n"
                f"┗ **Level {level}**"
            ),
            inline=False
        )

        # ASSETS
        embed.add_field(
            name="🏡 Assets & Properties",
            value=inventory_text,
            inline=False
        )

        # LIFE STATUS
        embed.add_field(
            name="📊 Life Status",
            value=(
                "Happiness • `76%`\n"
                "Health • `89%`\n"
                "Stress • `12%`\n"
                "Discipline • `Strong`"
            ),
            inline=False
        )

        # THUMBNAIL
        embed.set_thumbnail(
            url=ctx.author.display_avatar.url
        )

        # IMAGE
        embed.set_image(
            url="https://i.imgur.com/sHIxFaQ.gif"
        )

        # FOOTER
        embed.set_footer(
            text=(
                f"Citizen ID • {ctx.author.id}"
            )
        )

        # SEND
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Inventory(bot))
