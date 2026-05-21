import random
import discord
from discord.ext import commands
from collections import Counter

class Inventory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="inventory",
        aliases=["inv"],
        description="View your or another citizen's lifestyle profile and assets."
    )
    async def inventory(self, ctx: commands.Context, member: discord.Member = None):
        
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

        if not user_data:
            user_data = {"coins": 0, "gems": 0, "level": 1, "items": []}

        coins = user_data.get("coins", 0)
        gems = user_data.get("gems", 0)
        level = user_data.get("level", 1)
        
        # Assume items is a list in DB, e.g., ["Ring", "Chicken", "Chicken"]
        raw_items = user_data.get("items", [])

        # --- ITEM REGISTRY (Match the screenshot layout) ---
        # You can replace these default emojis with your custom Developer Portal emojis
        item_registry = {
            "Anting-anting": {
                "emoji": "🧿", 
                "desc": "Bonus: +500 Coins every 30 minutes in VC, valid for 1 day"
            },
            "Agimat": {
                "emoji": "🏺", 
                "desc": "Grants shield from robbery, valid for 1 day"
            },
            "Chicken": {
                "emoji": "🐓", 
                "desc": "Fighting chicken for `/cockfight`"
            },
            "Ring": {
                "emoji": "💍", 
                "desc": "Required for `/marry`, gives -10% tax reduction on `/give`"
            }
        }

        # --- INVENTORY FORMATTING ---
        inventory_lines = []
        if raw_items:
            # Counter automatically groups duplicates (e.g., counts 2 Chickens)
            item_counts = Counter(raw_items)
            
            for item_name, count in item_counts.items():
                # Pull data from registry, or use a fallback if the item isn't listed
                item_info = item_registry.get(item_name, {"emoji": "📦", "desc": "A mysterious item."})
                
                # The exact layout from your screenshot:
                # Emoji **Name** - __Quantity__
                # Description
                header = f"{item_info['emoji']} **{item_name}** - __x{count} Owned__"
                desc = item_info['desc']
                
                inventory_lines.append(f"{header}\n{desc}")
                
            # Join all formatted items with a double space for breathing room
            inventory_text = "\n\n".join(inventory_lines[:10])
        else:
            inventory_text = "No luxury assets or properties owned."

        # --- DYNAMIC AGE & STATS ---
        discord_age_years = (discord.utils.utcnow() - target_user.created_at).days // 365
        bitlife_age = 18 + discord_age_years

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

        # --- EMBED LAYOUT ---
        embed = discord.Embed(
            title="BitLife • Lifestyle Summary",
            description=(
                f"Profile overview for {target_user.mention}\n\n"
                f"Age\n**{bitlife_age}**\n\n"
                f"Status\n**{status}**\n\n"
                f"Reputation\n**Stable**\n\n"
                f"Career\n**Unemployed**"
            ),
            color=0x1A1A1A
        )

        embed.set_author(name=str(target_user), icon_url=target_user.display_avatar.url)

        embed.add_field(
            name=f"{cash_emoji} Finances",
            value=(
                f"Cash Balance\n**{coins:,} Coins**\n\n"
                f"Premium Currency\n**{gems:,} Gems**\n\n"
                f"Lifestyle Level\n**Level {level}**"
            ),
            inline=False
        )

        # The newly formatted Assets list goes here
        embed.add_field(
            name=f"{rate_emoji} Assets & Properties",
            value=inventory_text,
            inline=False
        )

        embed.add_field(
            name=f"{level_emoji} Life Status",
            value=(
                f"Happiness\n**{happiness}%**\n\n"
                f"Health\n**{health}%**\n\n"
                f"Stress\n**{stress}%**\n\n"
                f"Discipline\n**Strong**"
            ),
            inline=False
        )

        embed.set_thumbnail(url=target_user.display_avatar.url)
        embed.set_footer(text=f"Citizen ID • {target_user.id}")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Inventory(bot))
