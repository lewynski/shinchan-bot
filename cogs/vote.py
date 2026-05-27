import random
import discord
from discord.ext import commands

class VoteCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vote", aliases=["svote"], description="Get the link to vote for the bot on Top.gg.")
    async def vote(self, ctx: commands.Context):
        demoncat_emoji = "<a:demoncat:1506995624879329490>"
        vote_url = "https://top.gg/bot/1506864083985629305/vote"

        # --- Random Street Phrases ---
        phrases = [
            "Every vote keeps the underground running.",
            "The streets remember who supports the empire.",
            "Help us climb the ranks and rule the city.",
            "Rep the set. Drop a vote for the crew."
        ]

        # --- Plain Text Message Construction ---
        text = (
            f"{demoncat_emoji} **Support the Underground!**\n\n"
            f"Voting only takes a few seconds and pushes our bot higher on the charts so more players can hustle on these streets.\n\n"
            f"🔗 **Link:** {vote_url}\n\n"
            f"-# {random.choice(phrases)}"
        )
        
        # --- Clean Link Button View ---
        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label="Vote on Top.gg", 
            url=vote_url, 
            style=discord.ButtonStyle.link, 
            emoji="🚀"
        ))

        await ctx.send(content=text, view=view)

async def setup(bot):
    await bot.add_cog(VoteCommand(bot))
