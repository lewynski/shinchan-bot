import discord
from discord.ext import commands
import json

# --- MODALS (The pop-up forms for input) ---

class BasicInfoModal(discord.ui.Modal, title="Edit Basic Information"):
    def __init__(self, view):
        super().__init__()
        self.builder_view = view

        self.emb_title = discord.ui.TextInput(
            label="Embed Title", style=discord.TextStyle.short, required=False, 
            default=view.raw_dict.get("title", "")
        )
        self.emb_desc = discord.ui.TextInput(
            label="Embed Description", style=discord.TextStyle.paragraph, required=False,
            default=view.raw_dict.get("description", "")
        )
        
        current_color = ""
        if "color" in view.raw_dict:
            current_color = f"#{view.raw_dict['color']:06x}"

        self.emb_color = discord.ui.TextInput(
            label="Hex Color (e.g. #2b2d31)", style=discord.TextStyle.short, required=False,
            default=current_color
        )

        self.add_item(self.emb_title)
        self.add_item(self.emb_desc)
        self.add_item(self.emb_color)

    async def on_submit(self, interaction: discord.Interaction):
        self.builder_view.raw_dict["title"] = self.emb_title.value if self.emb_title.value else None
        self.builder_view.raw_dict["description"] = self.emb_desc.value if self.emb_desc.value else None
        
        if self.emb_color.value:
            try:
                self.builder_view.raw_dict["color"] = int(self.emb_color.value.replace("#", ""), 16)
            except ValueError:
                pass 

        await self.builder_view.update_preview(interaction)


class AuthorModal(discord.ui.Modal, title="Edit the Author"):
    def __init__(self, view):
        super().__init__()
        self.builder_view = view
        
        current_author = view.raw_dict.get("author", {})
        self.author_name = discord.ui.TextInput(label="Author Name", style=discord.TextStyle.short, required=False, default=current_author.get("name", ""))
        self.author_icon = discord.ui.TextInput(label="Author Icon URL", style=discord.TextStyle.short, required=False, default=current_author.get("icon_url", ""))

        self.add_item(self.author_name)
        self.add_item(self.author_icon)

    async def on_submit(self, interaction: discord.Interaction):
        if self.author_name.value:
            self.builder_view.raw_dict["author"] = {
                "name": self.author_name.value,
                "icon_url": self.author_icon.value if self.author_icon.value else None
            }
        else:
            self.builder_view.raw_dict.pop("author", None)

        await self.builder_view.update_preview(interaction)


class FooterModal(discord.ui.Modal, title="Edit the Footer"):
    def __init__(self, view):
        super().__init__()
        self.builder_view = view
        
        current_footer = view.raw_dict.get("footer", {})
        self.footer_text = discord.ui.TextInput(label="Footer Text", style=discord.TextStyle.short, required=False, default=current_footer.get("text", ""))
        self.footer_icon = discord.ui.TextInput(label="Footer Icon URL", style=discord.TextStyle.short, required=False, default=current_footer.get("icon_url", ""))

        self.add_item(self.footer_text)
        self.add_item(self.footer_icon)

    async def on_submit(self, interaction: discord.Interaction):
        if self.footer_text.value:
            self.builder_view.raw_dict["footer"] = {
                "text": self.footer_text.value,
                "icon_url": self.footer_icon.value if self.footer_icon.value else None
            }
        else:
            self.builder_view.raw_dict.pop("footer", None)

        await self.builder_view.update_preview(interaction)


class ImagesModal(discord.ui.Modal, title="Edit the Images"):
    def __init__(self, view):
        super().__init__()
        self.builder_view = view
        
        current_thumb = view.raw_dict.get("thumbnail", {}).get("url", "")
        current_image = view.raw_dict.get("image", {}).get("url", "")

        self.thumbnail_url = discord.ui.TextInput(
            label="Side Right Image (Thumbnail URL)", style=discord.TextStyle.short, required=False, default=current_thumb
        )
        self.image_url = discord.ui.TextInput(
            label="Bottom Image (Main Image URL)", style=discord.TextStyle.short, required=False, default=current_image
        )

        self.add_item(self.thumbnail_url)
        self.add_item(self.image_url)

    async def on_submit(self, interaction: discord.Interaction):
        if self.thumbnail_url.value:
            self.builder_view.raw_dict["thumbnail"] = {"url": self.thumbnail_url.value}
        else:
            self.builder_view.raw_dict.pop("thumbnail", None)
            
        if self.image_url.value:
            self.builder_view.raw_dict["image"] = {"url": self.image_url.value}
        else:
            self.builder_view.raw_dict.pop("image", None)

        await self.builder_view.update_preview(interaction)


# --- TEMPLATE DROPDOWN ---
class TemplateSelect(discord.ui.Select):
    def __init__(self, parent_view):
        self.parent_view = parent_view
        options = [
            discord.SelectOption(label="Blank Canvas", description="Start from scratch.", emoji="📄", value="blank"),
            discord.SelectOption(label="Gothic / Dark", description="Invisible background, crosses, dark aesthetic.", emoji="🦇", value="gothic"),
            discord.SelectOption(label="Cute / Soft", description="Pastel theme, sparkles, and kaomoji.", emoji="🌸", value="cute"),
            discord.SelectOption(label="Minimalist", description="Clean, professional, and simple.", emoji="🔲", value="minimal")
        ]
        super().__init__(placeholder="Select a pre-made template...", min_values=1, max_values=1, options=options, row=4)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "gothic":
            self.parent_view.raw_dict = {
                "color": 0x2b2d31,
                "description": "♱ ⸸ ✦ ₊ ˚. ✞\n\n      ⋆      welc... {user} to the underground.   ♱   *Born to die.*\n\n➦   [intros](https://discord.com)  🪦  [info](https://discord.com) 🧾 \n✿       [perks](https://discord.com)    *.·:·.✧.·:·.* ♡",
                "footer": {"text": "welc !  ,,  you are member #{member_count} !"}
            }
        elif self.values[0] == "cute":
            self.parent_view.raw_dict = {
                "color": 0xffb6c1,
                "title": "🎀 Welcome to the server! 🎀",
                "description": "ʚ♡ɞ ⁺˖ ⸝⸝\n\n╭◜◝ ͡ ◜◝╮\n( ᯅ̈.  ) grab your roles, {username}!\n╰◟◞ ͜ ◟◞╯\n\n🌸 ➜ [rules](https://discord.com)  |  🍧 ➜ [chat](https://discord.com)",
                "footer": {"text": "enjoy your stay ~ ♡ | member #{member_count}"},
                "thumbnail": {"url": "{avatar}"}
            }
        elif self.values[0] == "minimal":
            self.parent_view.raw_dict = {
                "color": 0xffffff,
                "title": "SERVER DIRECTORY",
                "description": "**Welcome to the community, {user}.**\n───────────────\nPlease read the rules before participating.\n\n▸ [Information](https://discord.com)\n▸ [Roles](https://discord.com)",
                "footer": {"text": "Total Members: {member_count}"}
            }
        elif self.values[0] == "blank":
            self.parent_view.raw_dict = {
                "color": 0x2b2d31,
                "title": "New Embed",
                "description": "Click the buttons below to build your embed."
            }

        await interaction.response.send_modal(BasicInfoModal(self.parent_view))


# --- VIEW (The interactive buttons below the message) ---
class EmbedBuilderView(discord.ui.View):
    def __init__(self, ctx, target_channel):
        super().__init__(timeout=600)
        self.ctx = ctx
        self.target_channel = target_channel
        
        self.raw_dict = {
            "title": "New Embed", 
            "description": "Click the buttons below or select a template to build your embed.",
            "color": 0x2b2d31
        }
        
        self.add_item(TemplateSelect(self))

    async def update_preview(self, interaction: discord.Interaction):
        raw_str = json.dumps(self.raw_dict)
        
        user = self.ctx.author
        server = self.ctx.guild
        avatar_url = user.display_avatar.url if user.display_avatar else user.default_avatar.url
        
        preview_str = raw_str.replace("{user}", user.mention) \
                             .replace("{username}", user.display_name) \
                             .replace("{server}", server.name) \
                             .replace("{member_count}", str(server.member_count)) \
                             .replace("{avatar}", avatar_url)
                             
        preview_dict = json.loads(preview_str)
        preview_embed = discord.Embed.from_dict(preview_dict)
        
        await interaction.response.edit_message(embed=preview_embed, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message("❌ You didn't run this command.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Edit the basic information", style=discord.ButtonStyle.secondary, row=0)
    async def btn_basic(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BasicInfoModal(self))

    @discord.ui.button(label="Edit the author", style=discord.ButtonStyle.secondary, row=1)
    async def btn_author(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AuthorModal(self))

    @discord.ui.button(label="Edit the footer", style=discord.ButtonStyle.secondary, row=1)
    async def btn_footer(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FooterModal(self))

    @discord.ui.button(label="Edit the images", style=discord.ButtonStyle.secondary, row=2)
    async def btn_images(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ImagesModal(self))

    @discord.ui.button(label="✅ Save Welcome Setup", style=discord.ButtonStyle.success, row=3)
    async def btn_send(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await interaction.delete_original_response()
        
        collection = self.ctx.bot.db["servers"] 
        await collection.update_one(
            {"_id": self.ctx.guild.id},
            {"$set": {
                "welcome_channel": self.target_channel.id,
                "welcome_embed": self.raw_dict 
            }},
            upsert=True
        )
        
        await interaction.followup.send(f"✅ **Welcome Setup Saved!** Whenever a new user joins, the bot will now automatically send this message to {self.target_channel.mention}.", ephemeral=True)
        self.stop()

    @discord.ui.button(label="🗑️ Cancel", style=discord.ButtonStyle.danger, row=3)
    async def btn_cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await interaction.delete_original_response()
        self.stop()


# --- MAIN COG ---
class CreateWelcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. THE CREATE WELCOME COMMAND
    @commands.hybrid_command(name="create_welcome", description="Open the interactive Welcome Embed Builder (Staff Only).")
    @commands.has_permissions(manage_messages=True)
    async def create_welcome(self, ctx: commands.Context, channel: discord.TextChannel = None):
        target = channel or ctx.channel 
        
        view = EmbedBuilderView(ctx, target)
        
        content = (
            f"🛠️ **Welcome Builder** | Target: {target.mention}\n"
            f"*Pick a template below or use the buttons to get started!*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"**✨ Available Variables (Type these anywhere!):**\n"
            f"`{{user}}` ➔ Pings the new user (e.g. {ctx.author.mention})\n"
            f"`{{username}}` ➔ The user's name (e.g. {ctx.author.display_name})\n"
            f"`{{server}}` ➔ The server's name\n"
            f"`{{member_count}}` ➔ Total number of members (e.g. {ctx.guild.member_count})\n"
            f"`{{avatar}}` ➔ The user's Profile Picture URL *(Put this in the image/thumbnail box!)*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        preview_embed = discord.Embed.from_dict(view.raw_dict)
        
        # This is the line that makes the menu INVISIBLE to everyone else!
        await ctx.send(content=content, embed=preview_embed, view=view, ephemeral=True)


    # 2. AUTOMATIC WELCOME LISTENER
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        collection = self.bot.db["servers"]
        server_data = await collection.find_one({"_id": member.guild.id})
        
        if not server_data or "welcome_embed" not in server_data:
            return 
            
        channel_id = server_data.get("welcome_channel")
        channel = member.guild.get_channel(channel_id)
        if not channel:
            return 
            
        raw_str = json.dumps(server_data["welcome_embed"])
        avatar_url = member.display_avatar.url if member.display_avatar else member.default_avatar.url
        
        final_str = raw_str.replace("{user}", member.mention) \
                           .replace("{username}", member.display_name) \
                           .replace("{server}", member.guild.name) \
                           .replace("{member_count}", str(member.guild.member_count)) \
                           .replace("{avatar}", avatar_url)
                           
        final_dict = json.loads(final_str)
        final_embed = discord.Embed.from_dict(final_dict)
        
        try:
            await channel.send(content=f"Welcome to the underground, {member.mention}...", embed=final_embed)
        except discord.Forbidden:
            pass


    # 3. THE REMOVE COMMAND (Kept completely untouched!)
    @commands.hybrid_command(name="remove_embed", aliases=["delete_embed", "delwelcome"], description="Delete an existing bot message using its ID (Staff Only).")
    @commands.has_permissions(manage_messages=True)
    async def remove_embed(self, ctx: commands.Context, message_id: str, channel: discord.TextChannel = None):
        target_channel = channel or ctx.channel
        
        try:
            msg = await target_channel.fetch_message(int(message_id))
            
            if msg.author.id != self.bot.user.id:
                return await ctx.send("❌ I can only delete messages that were sent by me.", ephemeral=True)
                
            await msg.delete()
            await ctx.send(f"✅ Successfully deleted the embed in {target_channel.mention}.", ephemeral=True)
            
        except discord.NotFound:
            await ctx.send("❌ Could not find that message. Make sure you copied the correct ID and selected the right channel.", ephemeral=True)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to delete that message.", ephemeral=True)
        except ValueError:
            await ctx.send("❌ Invalid ID format. Please provide a valid numeric Message ID.", ephemeral=True)

    @remove_embed.error
    async def remove_embed_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You do not have permission to use this command.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(CreateWelcome(bot))
