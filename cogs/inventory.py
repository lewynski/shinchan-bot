import random
import discord
from discord.ext import commands
from collections import Counter

# --- INTERACTIVE PAGINATOR CLASS ---
class InventoryPaginator(discord.ui.View):
    def __init__(self, pages, author_id):
        super().__init__(timeout=180) # Buttons will disable after 3 minutes to save memory
        self.pages = pages
        self.author_id = author_id
        self.current_page = 0

    # Ensures only the person who ran the command can click the buttons
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("This isn't your menu!", ephemeral=True)
            return False
        return True

    def update_buttons(self):
        # Disable "Prev" if on the first page, disable "Next" if on the last page
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.pages) - 1

    @discord.ui.button(label="◀ Prev", style=discord.ButtonStyle.blurple, disabled=True)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.blurple)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current_page], view=self)

# --- INVENTORY COG ---
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
        raw_items = user_data.get("items", [])

        # --- ITEM REGISTRY ---
        item_registry = {}

        # --- INVENTORY FORMATTING ---
        inventory_lines = []
        if raw_items:
            item_counts = Counter(raw_items)
            for item_name, count in item_counts.items():
                item_info = item_registry.get(item_name, {"emoji": "📦", "desc": "A mysterious item."})
                header = f"{item_info['emoji']} **{item_name}** - __x{count} Owned__"
                desc = item_info['desc']
                inventory_lines.append(f"{header}\n{desc}")
                
            inventory_text = "\n".join(inventory_lines[:10])
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

        # --- BUILD PAGES ---
        pages = []
        
        # Helper function to generate a base embed template to avoid repetitive code
        def create_base_embed(title_suffix, page_num):
            embed = discord.Embed(
                title=f"BitLife • {title_suffix}",
                color=0x1A1A1A
            )
            embed.set_author(name=str(target_user), icon_url=target_user.display_avatar.url)
            embed.set_thumbnail(url=target_user.display_avatar.url)
            embed.set_footer(text=f"Citizen ID • {target_user.id}  |  Page {page_num}/4")
            return embed

        # PAGE 1: Profile
        embed1 = create_base_embed("Personal Profile", 1)
        embed1.description = (
            f"Profile overview for {target_user.mention}\n\n"
            f"Age\n**{bitlife_age}**\n"
            f"Status\n**{status}**\n"
            f"Reputation\n**Stable**\n"
            f"Career\n**Unemployed**"
        )
        pages.append(embed1)

        # PAGE 2: Finances
        embed2 = create_base_embed("Financial Ledger", 2)
        embed2.add_field(
            name=f"{cash_emoji} Finances",
            value=(
                f"Cash Balance\n**{coins:,} Coins**\n"
                f"Premium Currency\n**{gems:,} Gems**\n"
                f"Lifestyle Level\n**Level {level}**"
            ),
            inline=False
        )
        pages.append(embed2)

        # PAGE 3: Assets
        embed3 = create_base_embed("Assets & Properties", 3)
        embed3.add_field(
            name=f"{rate_emoji} Inventory",
            value=inventory_text,
            inline=False
        )
        pages.append(embed3)

        # PAGE 4: Life Status
        embed4 = create_base_embed("Life Status", 4)
        embed4.add_field(
            name=f"{level_emoji} Vitals",
            value=(
                f"Happiness\n**{happiness}%**\n"
                f"Health\n**{health}%**\n"
                f"Stress\n**{stress}%**\n"
                f"Discipline\n**Strong**"
            ),
            inline=False
        )
        pages.append(embed4)

        # --- SEND FIRST PAGE WITH BUTTONS ---
        view = InventoryPaginator(pages, ctx.author.id)
        await ctx.send(embed=pages[0], view=view)

async def setup(bot):
    await bot.add_cog(Inventory(bot))
