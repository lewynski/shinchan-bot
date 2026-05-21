import discord
from discord.ext import commands

class Menu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="menu", description="View all available commands.")
    async def menu(self, ctx: commands.Context):
        
        # Here we list your commands with the small text formatting below each one
        text = (
            "**Available Commands**\n\n"
            
            "**/cash**\n"
            "-# Check your current wallet balance.\n\n"
            
            "**/coinflip <choice> <bet>**\n"
            "-# Bet your coins on heads or tails.\n\n"
            
            "**/rob <user>**\n"
            "-# Attempt to steal coins from another citizen.\n\n"
            
            "**/shop**\n"
            "-# Browse the Black Market for exclusive perks.\n\n"
            
            "**/role <user> <role>**\n"
            "-# Grant or revoke roles for server members (Staff only)."
        )
            
        await ctx.send(content=text)

async def setup(bot):
    await bot.add_cog(Menu(bot))
