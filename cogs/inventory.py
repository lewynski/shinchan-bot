import random
import discord
from discord.ext import commands


class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="inventory",
        aliases=["inv"],
        description="View your or another citizen's lifestyle profile and assets."
    )
    async def inventory(self, ctx: commands.Context, member: discord.Member = None):

        # Target user
        target_user = member or ctx.author
        user_id = target_user.id

        # --- CUSTOM ANIMATED EMOJIS ---
        cash_emoji = "<a:cash:1506921225484767282>"
        diamonds_emoji = "<a:diamonds:1506953045722927114>"
        life_emoji = "<a:life:1506953524272168970>"
        rate_emoji = "<a:rate:1506950189800357948>"
        level_emoji = "<a:level:1506953310807130152>"

        # --- DATABASE ---
        collection = self.bot.db["daily_cooldowns"]
        user_data = await collection.find_one({"_id": user_id})

        # --- DEFAULT VALUES ---
        if not user_data:
            user_data = {
                "coins": 0,
                "gems": 0,
                "level": 1,
                "items": []
            }

        # --- DATA ---
        coins = user_data.get("coins", 0)
        gems = user_data.get("gems", 0)
        level = user_data.get("level", 1)
        items = user_data.get("items", [])

        # --- DYNAMIC AGE ---
        discord_age_years = (discord.utils.utcnow() - target_user.created_at).days // 365
        bitlife_age = 18 + discord_age_years

        # --- STATUS SYSTEM ---
        if coins >= 1_000_000:
            status = "Elite Millionaire"
            happiness = random.randint(85, 100)
            health = random.randint(80, 100)
            stress = random.randint(5, 25)

        elif coins >= 100_000:
            status = "Luxury Citizen"
            happiness = random.randint(70, 90)
            health = random.randint(70, 95)
            stress = random.randint(15, 40)

        elif coins >= 10_000:
            status = "Wealthy Resident"
            happiness = random.randint(50, 80)
            health = random.randint(60, 90)
            stress = random.randint(30, 60)

        else:
            status = "Average Citizen"
            happiness = random.randint(20, 60)
            health = random.randint(40, 80)
            stress = random.randint(50, 90)

        # --- INVENTORY FORMAT ---
        if items:
            inventory_text = "\n".join(f"• {item}" for item in items[:10])
        else:
            inventory_text = "No luxury assets or properties owned."

        # --- EMBED ---
        embed = discord.Embed(
            title="BitLife • Lifestyle Summary",
            description=(
                f"Profile overview for {target_user.mention}\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                f"Age • `{bitlife_age}`\n"
                f"Status • `{status}`\n"
                "━━━━━━━━━━━━━━━━━━"
            ),
            color=0x1A1A1A
        )

        embed.set_author(
            name=str(target_user),
            icon_url=target_user.display_avatar.url
        )

        embed.set_thumbnail(url=target_user.display_avatar.url)

        # --- FINANCES (REDESIGNED) ---
        embed.add_field(
            name=f"{cash_emoji} Finances",
            value=(
                f"{cash_emoji} Cash Balance\n"
                f"    **{coins:,} Coins**\n\n"

                f"{diamonds_emoji} Premium Currency\n"
                f"    **{gems:,} Gems**\n\n"

                f"{life_emoji} Lifestyle Level\n"
                f"    **Level {level}**\n"
            ),
            inline=False
        )

        # --- ASSETS (REDESIGNED) ---
        embed.add_field(
            name=f"{rate_emoji} Assets & Properties",
            value=(
                f"{rate_emoji} Ownership Overview\n\n"
                f"{inventory_text}\n\n"
                "────────────────────"
            ),
            inline=False
        )

        # --- LIFE STATUS (REDESIGNED) ---
        embed.add_field(
            name=f"{level_emoji} Life Status",
            value=(
                f"{level_emoji} Emotional State\n"
                f"    Happiness: `{happiness}%`\n\n"

                f"{life_emoji} Physical Condition\n"
                f"    Health: `{health}%`\n\n"

                f"{cash_emoji} Mental Pressure\n"
                f"    Stress: `{stress}%`\n\n"

                "Discipline: `Strong`\n"
            ),
            inline=False
        )

        embed.set_footer(text=f"Citizen ID • {target_user.id}")

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Inventory(bot))
