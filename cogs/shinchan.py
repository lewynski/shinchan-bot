import discord
from discord.ext import commands

class Shinchan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="shinchan", description="View all available commands.")
    async def shinchan(self, ctx: commands.Context):
        
        # Creating a white-themed embed for a premium look
        embed = discord.Embed(
            title="Available Commands",
            color=0xFFFFFF # Pure white accent
        )
        
        # Adding commands with small text formatting
        embed.add_field(
            name="**/cash**",
            value="-# Check your current wallet balance.",
            inline=False
        )
        embed.add_field(
            name="**/coinflip <choice> <bet>**",
            value="-# Bet your coins on heads or tails.",
            inline=False
        )
        embed.add_field(
            name="**/rob <user>**",
            value="-# Attempt to steal coins from another citizen.",
            inline=False
        )
        embed.add_field(
            name="**/shop**",
            value="-# Browse the Black Market for exclusive perks.",
            inline=False
        )
        embed.add_field(
            name="**/role <user> <role>**",
            value="-# Grant or revoke roles for server members (Staff only).",
            inline=False
        )
            
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Shinchan(bot))
