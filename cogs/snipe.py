import discord
from discord.ext import commands

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Format: {channel_id: [list of deleted_messages]}
        self.snipe_cache = {} 

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        # Ignore bots and system messages
        if message.author.bot:
            return
        
        # Save up to 5 messages per channel
        if message.channel.id not in self.snipe_cache:
            self.snipe_cache[message.channel.id] = []
        
        self.snipe_cache[message.channel.id].append(message)
        
        # Keep only the last 5 messages in memory
        if len(self.snipe_cache[message.channel.id]) > 5:
            self.snipe_cache[message.channel.id].pop(0)

    @commands.hybrid_command(name="snipe", description="Retrieve the last deleted message.")
    @commands.cooldown(1, 60, commands.BucketType.user) # 1 use every 60 seconds per user
    async def snipe(self, ctx: commands.Context, index: int = 1):
        # Get the cache for this channel
        cache = self.snipe_cache.get(ctx.channel.id, [])
        
        # Validation checks
        if not cache:
            return await ctx.send("There are no deleted messages to snipe in this channel.", ephemeral=True)
        
        if index > len(cache) or index < 1:
            return await ctx.send(f"I only have {len(cache)} deleted messages saved. Please pick a number between 1 and {len(cache)}.", ephemeral=True)

        # Get the message (index 1 is the most recent)
        msg = cache[-index]
        
        # Create embed for the sniped message
        embed = discord.Embed(
            description=msg.content or "*[No text content in this message]*",
            color=discord.Color.blue()
        )
        embed.set_author(name=msg.author.display_name, icon_url=msg.author.display_avatar.url)
        embed.set_footer(text=f"Sniped by {ctx.author.name} | Message {index} of {len(cache)}")
        
        await ctx.send(embed=embed)

    @snipe.error
    async def snipe_error(self, ctx: commands.Context, error):
        # Handle the cooldown error
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Slow down! Wait {error.retry_after:.1f}s before sniping again.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Snipe(bot))
