import discord
from discord.ext import commands
from discord import app_commands

# Store your authorized Role IDs in a secure tuple
AUTHORIZED_ROLES = (1506809407588008027, 1506810633637859401)

def is_staff_or_mod():
    """Custom check to verify if the user has any of the authorized role IDs."""
    async def predicate(ctx):
        # Extract all role IDs the user currently has
        user_role_ids = [role.id for role in ctx.author.roles]
        
        # Check if there is any overlap between user roles and authorized roles
        if any(role_id in AUTHORIZED_ROLES for role_id in user_role_ids):
            return True
            
        # Raise a specific error if they don't match, so our error handler can grab it
        raise commands.MissingAnyRole(AUTHORIZED_ROLES)
    return commands.check(predicate)

class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.hybrid_command makes this work as BOTH "srole" and "/role"
    @commands.hybrid_command(name="role", description="Toggle a role: Adds it if missing, removes it if owned.")
    @is_staff_or_mod() # Applies our secure ID check here
    @app_commands.describe(member="The user to modify", role="The role to add or remove")
    async def role(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        
        # 1. Security Check: Ensure Shinchan's role is higher than the role being assigned
        if ctx.guild.me.top_role <= role:
            return await ctx.send(f"❌ I cannot manage {role.mention} because it is higher than or equal to my own top role!", ephemeral=True)

        try:
            # 2. Logic: REMOVE the role if they already have it
            if role in member.roles:
                await member.remove_roles(role)
                
                embed = discord.Embed(
                    title="Role Removed",
                    description=f"➖ Successfully removed {role.mention} from {member.mention}",
                    color=discord.Color.red() # Red color
                )
                embed.set_image(url="https://i.imgur.com/kQn4191.gif")

            # 3. Logic: ADD the role if they don't have it
            else:
                await member.add_roles(role)
                
                embed = discord.Embed(
                    title="Role Added",
                    description=f"➕ Successfully added {role.mention} to {member.mention}",
                    color=0x000000 # Black color
                )
                embed.set_image(url="https://i.imgur.com/GIDHSyY.gif")

            # 4. Set the Server Icon in the top right (Thumbnail)
            if ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon.url)
            
            # Show who ran the command at the bottom
            embed.set_footer(text=f"Action by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

            # Send the embed
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to manage roles. Check my role settings!", ephemeral=True)
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}", ephemeral=True)

    # Error handling for incorrect usage or missing permissions
    @role.error
    async def role_error(self, ctx, error):
        if isinstance(error, commands.MissingAnyRole):
            await ctx.send("❌ Only authorized Staff and Moderators are allowed to use this command.", ephemeral=True)
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Could not find that user. Try mentioning them, replying to their message, or using their user ID.", ephemeral=True)
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("❌ Could not find that role. Try tagging the role or using its role ID.", ephemeral=True)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Missing arguments! Usage: `srole <user> <role>`", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Role(bot))
