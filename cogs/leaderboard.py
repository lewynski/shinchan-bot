import discord
import random
import math
from discord.ext import commands

class LeaderboardPagination(discord.ui.View):
    def __init__(self, ctx, top_users, bot, phrases):
        super().__init__(timeout=120)
        self.ctx = ctx
        self.top_users = top_users
        self.bot = bot
        self.phrases = phrases
        self.current_page = 0
        self.per_page = 10
        self.total_pages = math.ceil(len(top_users) / self.per_page) or 1
        self.update_buttons()

    def update_buttons(self):
        # Updates the middle button (index 1) to show the current page number
        self.children[1].label = f"{self.current_page + 1}/{self.total_pages}"

    async def generate_embed(self):
        guild_name = self.ctx.guild.name if self.ctx.guild else "City"
        
        # 1. Dark red embed setup & Tking emoji with Server Name
        embed = discord.Embed(
            title=f"<a:tking:1514950042291802143> {guild_name} Leaderboard",
            color=discord.Color.dark_red()
        )
        
        # 2. Server icon at the top right
        if self.ctx.guild and self.ctx.guild.icon:
            embed.set_thumbnail(url=self.ctx.guild.icon.url)
            
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_users = self.top_users[start:end]

        # 3. Animated crown mappings
        crowns = {
            1: "<a:crown1:1514950214539153518>",
            2: "<a:crown2:1514950212521558026>",
            3: "<a:crown3:1514950035253760000>"
        }
        crown4 = "<a:crown4:1514950032665870378>" # Applies to ranks 4+
        
        description = ""
        
        # 4. Building the inline user format
        for i, user_data in enumerate(page_users):
            rank = start + i + 1
            user_id = user_data.get("_id")
            coins = user_data.get("coins", 0)
            
            try:
                user_id = int(user_id)
            except Exception:
                continue
            
            member = self.ctx.guild.get_member(user_id) if self.ctx.guild else None
            
            if member is None:
                try:
                    member = await self.bot.fetch_user(user_id)
                    username = member.name
                except Exception:
                    username = f"Unknown User ({user_id})"
            else:
                username = member.display_name
            
            crown = crowns.get(rank, crown4)
            
            # Format: 🏆 1. **Username** — 💰 `1,000,000`
            description += f"{crown} {rank}. **{username}** — 💰 `{coins:,}`\n"
            
        # 5. Bottom line separator and pagination/phrase text
        description += f"\n---\n\nPage {self.current_page + 1}/{self.total_pages} • {random.choice(self.phrases)}"
        
        embed.description = description
        
        return embed

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("You cannot use these buttons.", ephemeral=True)
        self.current_page = (self.current_page - 1) % self.total_pages
        self.update_buttons()
        await interaction.response.edit_message(embed=await self.generate_embed(), view=self)

    @discord.ui.button(label="1/1", style=discord.ButtonStyle.secondary, disabled=True)
    async def page_indicator(self, interaction: discord.Interaction, button: discord.ui.Button):
        # This button is disabled and just used to display the current page (e.g. 1/2)
        pass

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("You cannot use these buttons.", ephemeral=True)
        self.current_page = (self.current_page + 1) % self.total_pages
        self.update_buttons()
        await interaction.response.edit_message(embed=await self.generate_embed(), view=self)


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="leaderboard",
        aliases=["lb", "top"],
        description="View the richest members in the city."
    )
    async def leaderboard(self, ctx: commands.Context):
        try:
            collection = self.bot.db["daily_cooldowns"]

            # Fetching top 100 users
            top_users = await collection.find(
                {"coins": {"$gt": 0}}
            ).sort("coins", -1).limit(100).to_list(length=100)

            if not top_users:
                return await ctx.send(
                    "❌ No users with coins were found in the database."
                )

            phrases = [
                "Keep grinding to reach #1.",
                "Legends in the making.",
                "The wealthiest in the city.",
                "Respect the grind.",
                "The top of the food chain."
            ]

            view = LeaderboardPagination(ctx, top_users, self.bot, phrases)
            
            # Remove buttons if there is only one page
            if view.total_pages <= 1:
                view.clear_items()

            embed = await view.generate_embed()
            await ctx.send(embed=embed, view=view)

        except Exception as e:
            print(f"LEADERBOARD ERROR: {e}")
            await ctx.send(f"❌ Error: `{e}`")


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
