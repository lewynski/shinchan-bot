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
        self.children[1].label = f"{self.current_page + 1}/{self.total_pages}"

    async def get_rank_of_invoker(self):
        """Returns the rank and coins of the command invoker, or None if not found."""
        invoker_id = str(self.ctx.author.id)
        for i, user_data in enumerate(self.top_users):
            if str(user_data.get("_id")) == invoker_id:
                return i + 1, user_data.get("coins", 0)
        return None, None

    async def generate_embed(self):
        guild_name = self.ctx.guild.name if self.ctx.guild else "City"

        # Dark red embed with animated tking emoji + server name
        embed = discord.Embed(
            title=f"<a:tking:1514950042291802143> {guild_name} Leaderboard",
            color=discord.Color.dark_red()
        )

        # Server icon thumbnail (top right)
        if self.ctx.guild and self.ctx.guild.icon:
            embed.set_thumbnail(url=self.ctx.guild.icon.url)

        start = self.current_page * self.per_page
        end = start + self.per_page
        page_users = self.top_users[start:end]

        # Animated crown mappings — keeping your exact emojis
        crowns = {
            1: "<a:crown1:1514950214539153518>",
            2: "<a:crown2:1514950212521558026>",
            3: "<a:crown3:1514950035253760000>"
        }
        crown4 = "<a:crown4:1514950032665870378>"  # Ranks 4+

        description_lines = []

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
                    username = f"Unknown ({user_id})"
            else:
                username = member.display_name

            crown = crowns.get(rank, crown4)

            # Highlight the invoker's own row with a subtle marker
            is_self = (user_id == self.ctx.author.id)
            name_display = f"**{username}**" if not is_self else f"**__{username}__**"

            description_lines.append(
                f"{crown} {rank}. {name_display} — 💰 `{coins:,}`"
            )

        description = "\n".join(description_lines)

        # Separator + pagination phrase (matching image layout)
        description += f"\n\n─────────────────────\nPage {self.current_page + 1}/{self.total_pages} • *{random.choice(self.phrases)}*"

        # Show invoker's rank below separator if they're not on the current page
        invoker_rank, invoker_coins = await self.get_rank_of_invoker()
        if invoker_rank is not None:
            page_start = start + 1
            page_end = min(end, len(self.top_users))
            if not (page_start <= invoker_rank <= page_end):
                description += (
                    f"\n\n> Your rank: **#{invoker_rank}** — 💰 `{invoker_coins:,}`"
                )

        embed.description = description

        # Footer: total players tracked + bot avatar
        total = len(self.top_users)
        embed.set_footer(
            text=f"{total} players on the leaderboard",
            icon_url=self.bot.user.display_avatar.url if self.bot.user else None
        )

        return embed

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(
                "You cannot use these buttons.", ephemeral=True
            )
        self.current_page = (self.current_page - 1) % self.total_pages
        self.update_buttons()
        await interaction.response.edit_message(embed=await self.generate_embed(), view=self)

    @discord.ui.button(label="1/1", style=discord.ButtonStyle.secondary, disabled=True)
    async def page_indicator(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message(
                "You cannot use these buttons.", ephemeral=True
            )
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

            # Fetch top 100 users sorted by coins descending
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
                "The top of the food chain.",
                "Fortune favors the bold.",
                "Stack up or get left behind."
            ]

            view = LeaderboardPagination(ctx, top_users, self.bot, phrases)

            # Remove buttons if only one page
            if view.total_pages <= 1:
                view.clear_items()

            embed = await view.generate_embed()
            await ctx.send(embed=embed, view=view)

        except Exception as e:
            print(f"LEADERBOARD ERROR: {e}")
            await ctx.send(f"❌ Error: `{e}`")


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
