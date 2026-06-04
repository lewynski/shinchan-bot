import discord
from discord.ext import commands

# --- MODALS (The pop-up forms for input) ---

class BasicInfoModal(discord.ui.Modal, title="Edit Basic Information"):
    def __init__(self, view):
        super().__init__()
        self.builder_view = view

        self.emb_title = discord.ui.TextInput(
            label="Embed Title", style=discord.TextStyle.short, required=False, 
            default=view.preview_embed.title if view.preview_embed.title else ""
        )
        self.emb_desc = discord.ui.TextInput(
            label="Embed Description", style=discord.TextStyle.paragraph, required=False,
            default=view.preview_embed.description if view.preview_embed.description else ""
        )
        
        # Pull the color from the current draft so the staff can see the Hex code
        current_color = ""
        if view.preview_embed.color:
            current_color = f"#{view.preview_embed.color.value:06x}"

        self.emb_color = discord.ui.TextInput(
            label="Hex Color (e.g. #2b2d31)", style=discord.TextStyle.short, required=False,
            default=current_color
        )

        self.add_item(self.emb_title)
        self.add_item(self.emb_desc)
        self.add_item(self.emb_color)

    async def on_submit(self, interaction: discord.Interaction):
        self.builder_view.preview_embed.title = self.emb_title.value if self.emb_title.value else None
        self.builder_view.preview_embed.description = self.emb_desc.value if self.emb_desc.value else None
        
        if self.emb_color.value:
            try:
                color_value = int(self.emb_color.value.replace("#", ""), 16)
                self.builder_view.preview_embed.color = discord.Color(color_value)
            except ValueError:
                pass 

        await self.builder_view.update_preview(interaction)


class AuthorModal(discord.ui.Modal, title="Edit the Author"):
    def __init__(self, view):
        super().__init__()
        self.builder_view = view
        
        current_name = view.preview_embed.author.name if view.preview_embed.author else ""
        self.author_name = discord.ui.TextInput(label="Author Name", style=discord.TextStyle.short, required=False, default=current_name)
        self.author_icon = discord.ui.TextInput(label="Author Icon URL", style=discord.TextStyle.short, required=False)

        self.add_item(self.author_name)
        self.add_item(self.author_icon)

    async def on_submit(self, interaction: discord.Interaction):
        name = self.author_name.value if self.author_name.value else None
        icon = self.author_icon.value if self.author_icon.value else None
        
        if name:
            self.builder_view.preview_embed.set_author(name=name, icon_url=icon)
        else:
            self.builder_view.preview_embed.remove_author()

        await self.builder_view.update_preview(interaction)


class FooterModal(discord.ui.Modal, title="Edit the Footer"):
    def __init__(self, view):
        super().__init__()
        self.builder_view = view
        
        current_text = view.preview_embed.footer.text if view.preview_embed.footer else ""
        self.footer_text = discord.ui.TextInput(label="Footer Text", style=discord.TextStyle.short, required=False, default=current_text)
        self.footer_icon = discord.ui.TextInput(label="Footer Icon URL", style=discord.TextStyle.short, required=False)

        self.add_item(self.footer_text)
        self.add_item(self.footer_icon)

    async def on_submit(self, interaction: discord.Interaction):
        text = self.footer_text.value if self.footer_text.value else None
        icon = self.footer_icon.value if self.footer_icon.value else None
        
        if text:
            self.builder_view.preview_embed.set_footer(text=text, icon_url=icon)
        else:
            self.builder_view.preview_embed.remove_footer()

        await self.builder_view.update_preview(interaction)


class ImagesModal(discord.ui.Modal, title="Edit the Images"):
    def __init__(self, view):
        super().__init__()
        self.builder_view = view
        
        self.thumbnail_url = discord.ui.TextInput(
            label="Side Right Image (Thumbnail URL)", style=discord.TextStyle.short, required=False
        )
        self.image_url = discord.ui.TextInput(
            label="Bottom Image (Main Image URL)", style=discord.TextStyle.short, required=False
        )

        self.add_item(self.thumbnail_url)
        self.add_item(self.image_url)

    async def on_submit(self, interaction: discord.Interaction):
        if self.thumbnail_url.value:
            self.builder_view.preview_embed.set_thumbnail(url=self.thumbnail_url.value)
        else:
            self.builder_view.preview_embed.set_thumbnail(url=None)
            
        if self.image_url.value:
            self.builder_view.preview_embed.set_image(url=self.image_url.value)
        else:
            self.builder_view.preview_embed.set_image(url=None)

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
        # 1. Load the template data into the draft secretly
        if self.values[0] == "gothic":
            self.parent_view.preview_embed.color = discord.Color(0x2b2d31)
            self.parent_view.preview_embed.title = None
            self.parent_view.preview_embed.description = (
                "♱ ⸸ ✦ ₊ ˚. ✞\n\n"
                "      ⋆      welc... to the underground.   ♱   *Born to die.*\n\n"
                "➦   [intros](https://discord.com)  🪦  [info](https://discord.com) 🧾 \n"
                "✿       [perks](https://discord.com)    *.·:·.✧.·:·.* ♡"
            )
            self.parent_view.preview_embed.set_footer(text="welc !  ,,  we now have a new member !")
            
        elif self.values[0] == "cute":
            self.parent_view.preview_embed.color = discord.Color(0xffb6c1)
            self.parent_view.preview_embed.title = "🎀 Welcome to the server! 🎀"
            self.parent_view.preview_embed.description = (
                "ʚ♡ɞ ⁺˖ ⸝⸝\n\n"
                "╭◜◝ ͡ ◜◝╮\n"
                "( ᯅ̈.  ) grab your roles!\n"
                "╰◟◞ ͜ ◟◞╯\n\n"
                "🌸 ➜ [rules](https://discord.com)  |  🍧 ➜ [chat](https://discord.com)"
            )
            self.parent_view.preview_embed.set_footer(text="enjoy your stay ~ ♡")
            
        elif self.values[0] == "minimal":
            self.parent_view.preview_embed.color = discord.Color(0xffffff)
            self.parent_view.preview_embed.title = "SERVER DIRECTORY"
            self.parent_view.preview_embed.description = (
                "**Welcome to the community.**\n"
                "───────────────\n"
                "Please read the rules before participating.\n\n"
                "▸ [Information](https://discord.com)\n"
                "▸ [Roles](https://discord.com)"
            )
            self.parent_view.preview_embed.set_footer(text="Official Server Welcome")
            
        elif self.values[0] == "blank":
            self.parent_view.preview_embed.color = discord.Color(0x2b2d31)
            self.parent_view.preview_embed.title = "New Embed"
            self.parent_view.preview_embed.description = "Click the buttons below to build your embed."
            self.parent_view.preview_embed.clear_fields()
            self.parent_view.preview_embed.remove_author()
            self.parent_view.preview_embed.remove_footer()
            self.parent_view.preview_embed.set_image(url=None)
            self.parent_view.preview_embed.set_thumbnail(url=None)

        # 2. INSTANTLY open the text editor so the staff can revise the template text!
        await interaction.response.send_modal(BasicInfoModal(self.parent_view))


# --- VIEW (The interactive buttons below the message) ---
class EmbedBuilderView(discord.ui.View):
    def __init__(self, ctx, target_channel):
        super().__init__(timeout=600)
        self.ctx = ctx
        self.target_channel = target_channel
        
        self.preview_embed = discord.Embed(
            title="New Embed", 
            description="Click the buttons below or select a template to build your embed.",
            color=0x2b2d31
        )
        
        # Attach the Dropdown Menu
        self.add_item(TemplateSelect(self))

    async def update_preview(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.preview_embed, view=self)

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

    @discord.ui.button(label="✅ Send to Channel", style=discord.ButtonStyle.success, row=3)
    async def btn_send(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        await interaction.delete_original_response()
        
        try:
            await self.target_channel.send(embed=self.preview_embed)
            if self.target_channel.id != self.ctx.channel.id:
                await interaction.followup.send(f"✅ Embed successfully sent to {self.target_channel.mention}!", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send(f"❌ I don't have permission to send messages in {self.target_channel.mention}.", ephemeral=True)
            
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
        
        content = f"🛠️ **Welcome Builder** | Target: {target.mention}\n*Pick a template below to get started!*"
        await ctx.send(content=content, embed=view.preview_embed, view=view)

    @create_welcome.error
    async def create_welcome_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You do not have permission to use the embed builder.", ephemeral=True)

    # 2. THE REMOVE COMMAND
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
