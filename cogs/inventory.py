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
    # Added 'member' parameter to allow tagging other users
    async def inventory(self, ctx: commands.Context, member: discord.Member = None):
        
        # Determine the target user (either the tagged member, or the command author)
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
        # Calculates age based on the target user's Discord account creation date
        discord_age_years = (discord.utils.utcnow() - target_user.created_at).days // 365
        bitlife_age = 18 + discord_age_years

        # --- NET WORTH RANK & DYNAMIC STATS ---
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
            inventory_text = "\n\n".join(
                f"• {item}" for item in items[:10]
            )
        else:
            inventory_text = (
                "No luxury assets or properties owned."
            )

        # --- EMBED LAYOUT ---
        embed = discord.Embed(
            title="BitLife • Lifestyle Summary",
            description=(
                f"Profile overview for {target_user.mention}\n\n"
                f"Age • `{bitlife_age}`\n\n"
                f"Status • `{status}`\n\n"
                f"Reputation • `Stable`\n\n"
                f"Career • `Unemployed`"
            ),
            color=0x1A1A1A
        )

        # --- PROFILE ---
        embed.set_author(
            name=str(target_user),
            icon_url=target_user.display_avatar.url
        )

        # --- FINANCIALS ---
        embed.add_field(
            name=f"{cash_emoji} Finances",
            value=(
                f"{cash_emoji} Cash Balance - **{coins:,} Coins**\n\n"
                f"{diamonds_emoji} Premium Currency - **{gems:,} Gems**\n\n"
                f"{life_emoji} Lifestyle Level - **Level {level}**"
            ),
            inline=False
        )

        # --- ASSETS ---
        embed.add_field(
            name=f"{rate_emoji} Assets & Properties",
            value=inventory_text,
            inline=False
        )

        # --- LIFE STATUS ---
        embed.add_field(
            name=f"{level_emoji} Life Status",
            value=(
                f"Happiness • `{happiness}%`\n\n"
                f"Health • `{health}%`\n\n"
                f"Stress • `{stress}%`\n\n"
                f"Discipline • `Strong`"
            ),
            inline=False
        )

        # --- VISUALS ---
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        embed.set_footer(text=f"Citizen ID • {target_user.id}")

        # --- SEND ---
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Inventory(bot))
