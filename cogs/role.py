import discord
from discord.ext import commands
from discord import app_commands

# Authorized Staff and Moderator Role IDs
AUTHORIZED_ROLES = (1506809407588008027, 1506810633637859401)

def is_staff_or_mod():
    """Custom check to verify if the user has any of the authorized role IDs."""
    async def predicate(ctx):
        user_role_ids = [role.id for role in ctx.author.roles]
        if any(role_id in AUTHORIZED_ROLES for role_id in user_role_ids):
            return True
        raise commands.MissingAnyRole(AUTHORIZED_ROLES)
    return commands.check(predicate)

class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="role", description="Toggle server roles seamlessly.")
    @is_staff_or_mod()
    @app_commands.describe(member="Target user", role="Target role to toggle")
    async def role(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        
        if ctx.guild.me.top_role <= role:
            return await ctx.send(f"System Error: The role {role.mention} is positioned above this bot's hierarchy.", ephemeral=True)

        try:
            # Case A: Removing the role (Custom Burgundy Color)
            if role in member.roles:
                await member.remove_roles(role)
                
                embed = discord.Embed(
                    title="H I E R A R C H Y  U P D A T E",
                    color=discord.Color(0x800020) # Custom Burgundy Red Accent
                )
                embed.add_field(name="Target User", value=member.mention, inline=True)
                embed.add_field(name="Role Revoked", value=role.mention, inline=True)
                embed.add_field(name="Status", value="```diff\n- Removed\n```", inline=False)
                embed.set_image(url="https://i.imgur.com/kQn4191.gif")

            # Case B: Adding the role (Pure Black Color)
            else:
                await member.add_roles(role)
                
                embed = discord.Embed(
                    title="H I E R A R C H Y  U P D A T E",
                    color=0x000000 # Pure Black Accent
                )
                embed.add_field(name="Target User", value=member.mention, inline=True)
                embed.add_field(name="Role Granted", value=role.mention, inline=True)
                embed.add_field(name="Status", value="```diff\n+ Assigned\n```", inline=False)
                embed.set_image(url="https://i.imgur.com/GIDHSyY.gif")

            # Server Icon Configuration
            if ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon.url)
            
            # Subtle Footer
            embed.set_footer(
                text=f"Authorized by: {ctx.author.display_name}", 
                icon_url=ctx.author.display_avatar.url
            )

            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("System Error: Insufficient permissions to complete operations.", ephemeral=True)
        except Exception as e:
            await ctx.send(f"System Error: {e}", ephemeral=True)

    # Clean Error Logging
    @role.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send("Access Denied: Command restricted to authorized management roles only.", ephemeral=True)
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Target Error: Specified user could not be resolved.", ephemeral=True)
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("Target Error: Specified role could not be resolved.", ephemeral=True)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Syntax Error: Required parameters missing. Format: `srole <user> <role>`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Role(bot))
