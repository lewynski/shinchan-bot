import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="purge", description="Purge a specific number of messages.")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, limit: int):
        if limit < 1:
            return await ctx.send("Please provide a number greater than 0.", ephemeral=True)
        
        # We add 1 to the limit to include the command message itself
        deleted = await ctx.channel.purge(limit=limit + 1)
        
        msg = await ctx.send(f"Successfully deleted {len(deleted) - 1} messages.", ephemeral=True)
        
        # Auto-delete the confirmation message after 5 seconds
        await msg.delete(delay=5)

    @purge.error
    async def purge_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
