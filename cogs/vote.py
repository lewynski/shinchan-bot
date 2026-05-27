import random
import discord
from discord.ext import commands

class VoteCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="vote", aliases=["svote"], description="Get the official link to vote for the bot on Top.gg.")
    async def vote(self, ctx: commands.Context):
        demoncat_emoji = "<a:demoncat:1506995624879329490>"
        vote_url = "https://top.gg/bot/1506864083985629305/vote"

        # --- Formal Phrases ---
        phrases = [
            "Every vote keeps the underground running smoothly.",
            "Your support helps expand our city network.",
            "Help us climb the charts and control the streets.",
            "The streets remember who supports the empire."
        ]

        # --- Structured Formal Layout ---
        # Wrapping the URL in < > completely disables the ugly link preview card
        text = (
            f"{demoncat_emoji} **SHINCHAN | OFFICIAL TOP.GG VOTING**\n"
            f"‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n"
            f"Voting takes less than a minute and significantly helps increase our bot's visibility on the global charts, bringing more players into the economy.\n\n"
            f"🔗 **Secure Link:** <{vote_url}>\n\n"
            f"-# {random.choice(phrases)}"
        )
        
        # --- Sleek Interactive Button ---
        view = discord.ui.View()
        view.add_item(discord.ui.Button(
            label="Open Voting Page", 
            url=vote_url, 
            style=discord.ButtonStyle.link, 
            emoji="🚀"
        ))

        # Make sure to include view=view so the button actually renders!
        await ctx.send(content=text, view=view)

async def setup(bot):
    await bot.add_cog(VoteCommand(bot))
