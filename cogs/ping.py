import discord
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # In Cogs, we use @commands.command() instead of @bot.command()
    # And we must pass 'self' as the first parameter
    @commands.command()
    async def ping(self, ctx):
        """A simple test command."""
        await ctx.send('Pong! 🏓')

# This setup function is required for every Cog
async def setup(bot):
    await bot.add_cog(Ping(bot))
