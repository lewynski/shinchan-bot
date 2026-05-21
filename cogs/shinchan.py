import discord
from discord.ext import commands

class MenuPaginator(discord.ui.View):
    def __init__(self, commands_list, author_id):
        super().__init__(timeout=60)
        self.commands_list = commands_list
        self.author_id = author_id
        self.page = 0
        self.items_per_page = 5
        self.update_buttons()

    def update_buttons(self):
        # Disable Previous if on page 0
        self.prev_button.disabled = (self.page == 0)
        # Disable Next if on the last page
        max_pages = ((len(self.commands_list) - 1) // self.items_per_page)
        self.next_button.disabled = (self.page >= max_pages)

    def get_embed(self):
        commands_emoji = "<a:commands:1507006568657453096>"
        start = self.page * self.items_per_page
        end = start + self.items_per_page
        page_items = self.commands_list[start:end]

        embed = discord.Embed(
            title=f"{commands_emoji} Available Commands",
            color=0xFFFFFF
        )
        for name, desc in page_items:
            embed.add_field(name=name, value=f"-# {desc}", inline=False)
        
        embed.set_footer(text=f"Page {self.page + 1} / {((len(self.commands_list)-1)//self.items_per_page)+1}")
        return embed

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary, custom_id="prev")
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.author_id:
            self.page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary, custom_id="next")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.author_id:
            self.page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

class Shinchan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_data = [
            ("/cash", "Check your current wallet balance."),
            ("/coinflip <choice> <bet>", "Bet your coins on heads or tails."),
            ("/rob <user>", "Attempt to steal coins from another citizen."),
            ("/shop", "Browse the Black Market for exclusive perks."),
            ("/role <user> <role>", "Grant or revoke roles (Staff only).")
        ]

    @commands.hybrid_command(name="shinchan", description="View all available commands.")
    async def shinchan(self, ctx: commands.Context):
        view = MenuPaginator(self.command_data, ctx.author.id)
        await ctx.send(embed=view.get_embed(), view=view)

async def setup(bot):
    await bot.add_cog(Shinchan(bot))
