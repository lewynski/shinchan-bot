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
            return await ctx.send(f"System Error: The role {role.mention} is positioned above this bot's hierarchy.", ephemeral=True)

        # --- CUSTOM EMOJIS ---
        crown_emoji = "<a:crown:1507002962558455848>"
        kick_emoji = "<a:kick:1507003085761937438>"

        try:
            # Case A: Removing the role (Custom Burgundy Color & Kick Emoji)
            if role in member.roles:
                await member.remove_roles(role)
                
                embed = discord.Embed(
                    title=f"{kick_emoji} HIERARCHY UPDATE",
                    color=discord.Color(0x800020) 
                )
                embed.add_field(name="Target User", value=member.mention, inline=True)
                embed.add_field(name="Role Revoked", value=role.mention, inline=True)
                embed.add_field(name="Status", value="```diff\n- Removed\n```", inline=False)

                phrases = [
                    "Back to the bottom of the food chain.",
                    "Power revoked. The system remembers.",
                    "A tactical demotion.",
                    "Access restricted. Hierarchy updated."
                ]

            # Case B: Adding the role (Pure Black Color & Crown Emoji)
            else:
                await member.add_roles(role)
                
                embed = discord.Embed(
                    title=f"{crown_emoji} HIERARCHY UPDATE",
                    color=0x000000 
                )
                embed.add_field(name="Target User", value=member.mention, inline=True)
                embed.add_field(name="Role Granted", value=role.mention, inline=True)
                embed.add_field(name="Status", value="```diff\n+ Assigned\n```", inline=False)

                phrases = [
                    "Don't let the new power go to your head.",
                    "A new rank achieved. Use it wisely.",
                    "Clearance level upgraded.",
                    "The hierarchy welcomes your ascent."
                ]
            
            # Subtle Footer
            embed.set_footer(
                text=f"Authorized by: {ctx.author.display_name}", 
                icon_url=ctx.author.display_avatar.url
            )

            phrase = random.choice(phrases)
            await ctx.send(content=f"-# {phrase}", embed=embed)

        except discord.Forbidden:
            await ctx.send("System Error: Insufficient permissions to complete operations.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"System Error: {e}", ephemeral=True)

    # Clean Error Logging
    @role.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Access Denied: You must have the 'Manage Roles' permission to use this command.", ephemeral=True)
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Target Error: Specified user could not be resolved.", ephemeral=True)
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("Target Error: Specified role could not be resolved.", ephemeral=True)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Syntax Error: Required parameters missing. Format: `/role <user> <role>`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Role(bot))
