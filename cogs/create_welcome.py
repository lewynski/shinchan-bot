import json

import discord
from discord.ext import commands


async def send_ctx(ctx: commands.Context, *args, **kwargs):
    if ctx.interaction:
        kwargs.setdefault("ephemeral", True)
    else:
        kwargs.pop("ephemeral", None)

    return await ctx.send(*args, **kwargs)


def set_optional_value(data: dict, key: str, value: str):
    if value:
        data[key] = value
    else:
        data.pop(key, None)


class BasicInfoModal(discord.ui.Modal, title="Edit Basic Information"):
    def __init__(self, view):
        super().__init__()
        self.builder_view = view

        self.emb_title = discord.ui.TextInput(
            label="Embed Title",
            style=discord.TextStyle.short,
            required=False,
            default=view.raw_dict.get("title", ""),
        )
        self.emb_desc = discord.ui.TextInput(
            label="Embed Description",
            style=discord.TextStyle.paragraph,
            required=False,
            default=view.raw_dict.get("description", ""),
        )

        current_color = ""
        if "color" in view.raw_dict:
            current_color = f"#{view.raw_dict['color']:06x}"

        self.emb_color = discord.ui.TextInput(
            label="Hex Color, example #2b2d31",
            style=discord.TextStyle.short,
            required=False,
            default=current_color,
        )

        self.add_item(self.emb_title)
        self.add_item(self.emb_desc)
        self.add_item(self.emb_color)

    async def on_submit(self, interaction: discord.Interaction):
        set_optional_value(
            self.builder_view.raw_dict, "title", self.emb_title.value.strip()
        )
        set_optional_value(
            self.builder_view.raw_dict, "description", self.emb_desc.value.strip()
        )

        color_value = self.emb_color.value.strip().replace("#", "")
        if color_value:
            try:
                self.builder_view.raw_dict["color"] = int(color_value, 16)
            except ValueError:
                await interaction.response.send_message(
                    "Invalid hex color. Use something like `#2b2d31`.",
                    ephemeral=True,
                )
                return

        await self.builder_view.update_preview(interaction)


class AuthorModal(discord.ui.Modal, title="Edit Author"):
    def __init__(self, view):
        super().__init__()
        self.builder_view = view

        current_author = view.raw_dict.get("author", {})
        self.author_name = discord.ui.TextInput(
            label="Author Name",
            style=discord.TextStyle.short,
            required=False,
            default=current_author.get("name", ""),
        )
        self.author_icon = discord.ui.TextInput(
            label="Author Icon URL",
            style=discord.TextStyle.short,
            required=False,
            default=current_author.get("icon_url", ""),
        )

        self.add_item(self.author_name)
        self.add_item(self.author_icon)

    async def on_submit(self, interaction: discord.Interaction):
        author_name = self.author_name.value.strip()
        author_icon = self.author_icon.value.strip()

        if author_name:
            self.builder_view.raw_dict["author"] = {"name": author_name}
            if author_icon:
                self.builder_view.raw_dict["author"]["icon_url"] = author_icon
        else:
            self.builder_view.raw_dict.pop("author", None)

        await self.builder_view.update_preview(interaction)


class FooterModal(discord.ui.Modal, title="Edit Footer"):
    def __init__(self, view):
        super().__init__()
        self.builder_view = view

        current_footer = view.raw_dict.get("footer", {})
        self.footer_text = discord.ui.TextInput(
            label="Footer Text",
            style=discord.TextStyle.short,
            required=False,
            default=current_footer.get("text", ""),
        )
        self.footer_icon = discord.ui.TextInput(
            label="Footer Icon URL",
            style=discord.TextStyle.short,
            required=False,
            default=current_footer.get("icon_url", ""),
        )

        self.add_item(self.footer_text)
        self.add_item(self.footer_icon)

    async def on_submit(self, interaction: discord.Interaction):
        footer_text = self.footer_text.value.strip()
        footer_icon = self.footer_icon.value.strip()

        if footer_text:
            self.builder_view.raw_dict["footer"] = {"text": footer_text}
            if footer_icon:
                self.builder_view.raw_dict["footer"]["icon_url"] = footer_icon
        else:
            self.builder_view.raw_dict.pop("footer", None)

        await self.builder_view.update_preview(interaction)


class ImagesModal(discord.ui.Modal, title="Edit Images"):
    def __init__(self, view):
        super().__init__()
        self.builder_view = view

        current_thumb = view.raw_dict.get("thumbnail", {}).get("url", "")
        current_image = view.raw_dict.get("image", {}).get("url", "")

        self.thumbnail_url = discord.ui.TextInput(
            label="Right Side Image URL",
            style=discord.TextStyle.short,
            required=False,
            default=current_thumb,
        )
        self.image_url = discord.ui.TextInput(
            label="Bottom Image URL",
            style=discord.TextStyle.short,
            required=False,
            default=current_image,
        )

        self.add_item(self.thumbnail_url)
        self.add_item(self.image_url)

    async def on_submit(self, interaction: discord.Interaction):
        thumbnail_url = self.thumbnail_url.value.strip()
        image_url = self.image_url.value.strip()

        if thumbnail_url:
            self.builder_view.raw_dict["thumbnail"] = {"url": thumbnail_url}
        else:
            self.builder_view.raw_dict.pop("thumbnail", None)

        if image_url:
            self.builder_view.raw_dict["image"] = {"url": image_url}
        else:
            self.builder_view.raw_dict.pop("image", None)

        await self.builder_view.update_preview(interaction)


class TemplateSelect(discord.ui.Select):
    def __init__(self, parent_view):
        self.parent_view = parent_view
        options = [
            discord.SelectOption(
                label="Blank Canvas",
                description="Start from scratch.",
                value="blank",
            ),
            discord.SelectOption(
                label="Gothic / Dark",
                description="Dark welcome layout.",
                value="gothic",
            ),
            discord.SelectOption(
                label="Cute / Soft",
                description="Pastel welcome layout.",
                value="cute",
            ),
            discord.SelectOption(
                label="Minimalist",
                description="Clean and simple layout.",
                value="minimal",
            ),
        ]
        super().__init__(
            placeholder="Select a pre-made template...",
            min_values=1,
            max_values=1,
            options=options,
            row=4,
        )

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "gothic":
            self.parent_view.raw_dict = {
                "color": 0x2B2D31,
                "description": (
                    "**Welcome to the underground, {user}.**\n\n"
                    "Read the info, pick your roles, and keep your eyes open.\n\n"
                    "[Intros](https://discord.com) | "
                    "[Info](https://discord.com) | "
                    "[Perks](https://discord.com)"
                ),
                "footer": {"text": "Member #{member_count}"},
            }
        elif self.values[0] == "cute":
            self.parent_view.raw_dict = {
                "color": 0xFFB6C1,
                "title": "Welcome to {server}",
                "description": (
                    "Welcome, {user}.\n\n"
                    "Grab your roles, say hello, and enjoy your stay."
                ),
                "footer": {"text": "Member #{member_count}"},
                "thumbnail": {"url": "{avatar}"},
            }
        elif self.values[0] == "minimal":
            self.parent_view.raw_dict = {
                "color": 0xFFFFFF,
                "title": "Server Directory",
                "description": (
                    "**Welcome to {server}, {user}.**\n\n"
                    "Please read the rules before participating.\n\n"
                    "[Information](https://discord.com)\n"
                    "[Roles](https://discord.com)"
                ),
                "footer": {"text": "Total members: {member_count}"},
            }
        else:
            self.parent_view.raw_dict = {
                "color": 0x2B2D31,
                "title": "New Embed",
                "description": "Click the buttons below to build your embed.",
            }

        await self.parent_view.update_preview(interaction)


class EmbedBuilderView(discord.ui.View):
    def __init__(self, ctx, target_channel):
        super().__init__(timeout=600)
        self.ctx = ctx
        self.target_channel = target_channel

        self.raw_dict = {
            "title": "New Embed",
            "description": "Click the buttons below or select a template to build your embed.",
            "color": 0x2B2D31,
        }

        self.add_item(TemplateSelect(self))

    def build_preview_embed(self):
        raw_str = json.dumps(self.raw_dict)

        user = self.ctx.author
        server = self.ctx.guild
        avatar_url = user.display_avatar.url

        preview_str = (
            raw_str.replace("{user}", user.mention)
            .replace("{username}", user.display_name)
            .replace("{server}", server.name)
            .replace("{member_count}", str(server.member_count))
            .replace("{avatar}", avatar_url)
        )

        preview_dict = json.loads(preview_str)
        return discord.Embed.from_dict(preview_dict)

    async def update_preview(self, interaction: discord.Interaction):
        try:
            preview_embed = self.build_preview_embed()
        except Exception as exc:
            await interaction.response.send_message(
                f"Could not build that embed: `{exc}`",
                ephemeral=True,
            )
            return

        await interaction.response.edit_message(embed=preview_embed, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "You didn't run this command.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(
        label="Edit basic information",
        style=discord.ButtonStyle.secondary,
        row=0,
    )
    async def btn_basic(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(BasicInfoModal(self))

    @discord.ui.button(
        label="Edit author",
        style=discord.ButtonStyle.secondary,
        row=1,
    )
    async def btn_author(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(AuthorModal(self))

    @discord.ui.button(
        label="Edit footer",
        style=discord.ButtonStyle.secondary,
        row=1,
    )
    async def btn_footer(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(FooterModal(self))

    @discord.ui.button(
        label="Edit images",
        style=discord.ButtonStyle.secondary,
        row=2,
    )
    async def btn_images(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(ImagesModal(self))

    @discord.ui.button(
        label="Save Welcome Setup",
        style=discord.ButtonStyle.success,
        row=3,
    )
    async def btn_send(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            content="Saving welcome setup...",
            embed=None,
            view=None,
        )

        collection = self.ctx.bot.db["servers"]
        await collection.update_one(
            {"_id": self.ctx.guild.id},
            {
                "$set": {
                    "welcome_channel": self.target_channel.id,
                    "welcome_embed": self.raw_dict,
                }
            },
            upsert=True,
        )

        await interaction.followup.send(
            (
                "**Welcome setup saved.** New members will be welcomed in "
                f"{self.target_channel.mention}."
            ),
            ephemeral=True,
        )
        self.stop()

    @discord.ui.button(
        label="Cancel",
        style=discord.ButtonStyle.danger,
        row=3,
    )
    async def btn_cancel(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            content="Welcome setup cancelled.",
            embed=None,
            view=None,
        )
        self.stop()


class CreateWelcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="create_welcome",
        description="Open the interactive Welcome Embed Builder.",
    )
    @commands.has_permissions(manage_messages=True)
    async def create_welcome(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel = None,
    ):
        if ctx.interaction:
            await ctx.defer(ephemeral=True)

        target = channel or ctx.channel
        view = EmbedBuilderView(ctx, target)
        preview_embed = view.build_preview_embed()

        content = (
            f"**Welcome Builder** | Target: {target.mention}\n"
            "Pick a template below or use the buttons to get started.\n\n"
            "**Available Variables:**\n"
            f"`{{user}}` -> pings the new user, example {ctx.author.mention}\n"
            f"`{{username}}` -> the user's display name, example {ctx.author.display_name}\n"
            "`{server}` -> the server name\n"
            f"`{{member_count}}` -> total members, example {ctx.guild.member_count}\n"
            "`{avatar}` -> the user's avatar URL for image boxes"
        )

        await send_ctx(
            ctx,
            content=content,
            embed=preview_embed,
            view=view,
            ephemeral=True,
        )

    @create_welcome.error
    async def create_welcome_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await send_ctx(
                ctx,
                "You need `Manage Messages` permission to use this command.",
                ephemeral=True,
            )
        else:
            await send_ctx(
                ctx,
                f"Something went wrong while opening the builder: `{error}`",
                ephemeral=True,
            )

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
        avatar_url = member.display_avatar.url

        final_str = (
            raw_str.replace("{user}", member.mention)
            .replace("{username}", member.display_name)
            .replace("{server}", member.guild.name)
            .replace("{member_count}", str(member.guild.member_count))
            .replace("{avatar}", avatar_url)
        )

        final_dict = json.loads(final_str)
        final_embed = discord.Embed.from_dict(final_dict)

        try:
            await channel.send(
                content=f"Welcome to the underground, {member.mention}...",
                embed=final_embed,
            )
        except discord.Forbidden:
            pass

    @commands.hybrid_command(
        name="remove_embed",
        aliases=["delete_embed", "delwelcome"],
        description="Delete an existing bot message using its ID.",
    )
    @commands.has_permissions(manage_messages=True)
    async def remove_embed(
        self,
        ctx: commands.Context,
        message_id: str,
        channel: discord.TextChannel = None,
    ):
        if ctx.interaction:
            await ctx.defer(ephemeral=True)

        target_channel = channel or ctx.channel

        try:
            msg = await target_channel.fetch_message(int(message_id))

            if msg.author.id != self.bot.user.id:
                return await send_ctx(
                    ctx,
                    "I can only delete messages that were sent by me.",
                    ephemeral=True,
                )

            await msg.delete()
            await send_ctx(
                ctx,
                f"Successfully deleted the bot message in {target_channel.mention}.",
                ephemeral=True,
            )
        except discord.NotFound:
            await send_ctx(
                ctx,
                "Could not find that message. Check the ID and channel.",
                ephemeral=True,
            )
        except discord.Forbidden:
            await send_ctx(
                ctx,
                "I don't have permission to delete that message.",
                ephemeral=True,
            )
        except ValueError:
            await send_ctx(
                ctx,
                "Invalid ID format. Please provide a numeric message ID.",
                ephemeral=True,
            )

    @remove_embed.error
    async def remove_embed_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await send_ctx(
                ctx,
                "You need `Manage Messages` permission to use this command.",
                ephemeral=True,
            )
        else:
            await send_ctx(
                ctx,
                f"Something went wrong: `{error}`",
                ephemeral=True,
            )


async def setup(bot):
    await bot.add_cog(CreateWelcome(bot))
