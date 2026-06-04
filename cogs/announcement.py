import time

import discord
from discord.ext import commands


OWNER_ID = 879936602414133288


async def send_pending_announcement(bot, ctx: commands.Context, user_id: int):
    announcements = bot.db["announcements"]
    users = bot.db["daily_cooldowns"]

    announcement = await announcements.find_one({"_id": "current"})
    if not announcement:
        return

    announcement_id = announcement.get("announcement_id")
    if not announcement_id:
        return

    user_data = await users.find_one(
        {"$or": [{"_id": user_id}, {"_id": str(user_id)}]}
    ) or {}

    if user_data.get("seen_announcement_id") == announcement_id:
        return

    embed = discord.Embed(
        title=announcement.get("title", "Announcement"),
        description=announcement.get("description", ""),
        color=0x000000,
    )

    await ctx.send(embed=embed)

    await users.update_one(
        {"_id": user_data.get("_id", user_id)},
        {"$set": {"seen_announcement_id": announcement_id}},
        upsert=True,
    )


class AnnouncementCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="announcement",
        description="Create a one-time announcement shown on each user's next daily.",
    )
    async def announcement(self, ctx: commands.Context, title: str, description: str):
        if ctx.author.id != OWNER_ID:
            return await ctx.send(
                "Only the bot owner can use this command.",
                ephemeral=True,
            )

        announcement_id = int(time.time())

        await self.bot.db["announcements"].update_one(
            {"_id": "current"},
            {
                "$set": {
                    "announcement_id": announcement_id,
                    "title": title,
                    "description": description,
                    "created_by": ctx.author.id,
                    "created_at": time.time(),
                }
            },
            upsert=True,
        )

        embed = discord.Embed(title=title, description=description, color=0x000000)

        await ctx.send(
            content="**Announcement saved.** It will show once when each user runs `/daily`.",
            embed=embed,
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(AnnouncementCommand(bot))
