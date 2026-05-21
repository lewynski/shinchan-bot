import random
import discord
from discord.ext import commands
from discord import app_commands

class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="role", description="Toggle server roles seamlessly.")
    @commands.has_permissions(manage_roles=True)
    @app_commands.describe(member="Target user", role="Target role to toggle")
    async def role(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        
        if ctx.guild.me.top_role <= role:
            return await ctx.send("System Error: The role is positioned above this bot's hierarchy.", ephemeral=True)

        # --- CUSTOM EMOJIS ---
        crown_emoji = "<a:crown:1507002962558455848>"
        kick_emoji = "<a:kick:1507003085761937438>"

        try:
            # Case A: Removing the role
            if role in member.roles:
                await member.remove_roles(role)
                status_text = f"{kick_emoji} {member.mention} | Role Revoked: {role.mention} | Status: `Removed`"
                
                phrases = [
                    "Back to the bottom of the food chain.",
                    "Power revoked. The system remembers.",
                    "A tactical demotion.",
                    "Access restricted. Hierarchy updated."
                ]

            # Case B: Adding the role
            else:
                await member.add_roles(role)
                status_text = f"{crown_emoji} {member.mention} | Role Granted: {role.mention} | Status: `Assigned`"
                
                phrases = [
                    "Don't let the new power go to your head.",
                    "A new rank achieved. Use it wisely.",
                    "Clearance level upgraded.",
                    "The hierarchy welcomes your ascent."
                ]
            
            # Send status text followed by the random small phrase
            await ctx.send(f"{status_text}\n-# {random.choice(phrases)}")

        except discord.Forbidden:
            await ctx.send("System Error: Insufficient permissions to complete operations.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"System Error: {e}", ephemeral=True)

    @role.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Access Denied: You must have the 'Manage Roles' permission.", ephemeral=True)
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Target Error: User could not be resolved.", ephemeral=True)
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("Target Error: Role could not be resolved.", ephemeral=True)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Syntax Error: Format: `/role <user> <role>`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Role(bot))
