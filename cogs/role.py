import discord
from discord.ext import commands

class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_roles=True) # Security: Only admins/mods can use this
    async def addrole(self, ctx, member: discord.Member, role: discord.Role):
        """Assigns a role to a user. Example: !addrole @user @role"""
        try:
            await member.add_roles(role)
            await ctx.send(f"✅ Successfully added the **{role.name}** role to {member.mention}.")
        
        # This catches errors where Shinchan's own role is lower than the role he is trying to assign
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to add that role. My bot role must be higher than the role you are assigning!")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    # This handles errors if a normal user tries to run the command
    @addrole.error
    async def addrole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing arguments! Please use: `!addrole @user @role`")

async def setup(bot):
    await bot.add_cog(Role(bot))
