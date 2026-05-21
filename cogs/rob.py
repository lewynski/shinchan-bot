import random
import time
import discord
from discord.ext import commands

class RobCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="rob", aliases=["srob"], description="Attempt to rob another citizen. High risk, high reward.")
    async def rob(self, ctx: commands.Context, target: discord.Member):
        if target.id == ctx.author.id:
            return await ctx.send("You can't rob yourself...")

        collection = self.bot.db["daily_cooldowns"]
        user_data = await collection.find_one({"_id": ctx.author.id}) or {}
        target_data = await collection.find_one({"_id": target.id}) or {}
        now = time.time()
        
        jail_until = user_data.get("jail_until", 0)
        if now < jail_until:
            return await ctx.send(f"🚔 **You are in JAIL!** You can't rob anyone from behind bars. Released <t:{int(jail_until)}:R>.")
            
        rob_cd = user_data.get("rob_cooldown", 0)
        if now < rob_cd:
            return await ctx.send(f"⏳ The cops are actively patrolling. Lay low. You can strike again <t:{int(rob_cd)}:R>.")

        target_coins = target_data.get("coins", 0)
        if target_coins < 1000:
            return await ctx.send("That citizen is too poor to rob. Pick a richer target!")

        pendant_until = target_data.get("pendant_until", 0)
        if now < pendant_until:
            await collection.update_one({"_id": ctx.author.id}, {"$set": {"rob_cooldown": now + 1800}})
            return await ctx.send(f"🛡️ **Robbery Failed!** {target.mention} is protected by a magical Pendant! You flee the scene.")

        user_coins = user_data.get("coins", 0)
        outcome = random.choices(["success", "fail", "jail"], weights=[40, 30, 30])[0]
        new_cooldown = now + 1800 

        if outcome == "success":
            stolen_percent = random.uniform(0.05, 0.15)
            stolen_amount = int(target_coins * stolen_percent)
            
            await collection.update_one({"_id": target.id}, {"$inc": {"coins": -stolen_amount}})
            await collection.update_one({"_id": ctx.author.id}, {"$inc": {"coins": stolen_amount}, "$set": {"rob_cooldown": new_cooldown}})
            
            embed = discord.Embed(
                title="💰 Heist Successful",
                description=f"You slipped into the shadows and stole **{stolen_amount:,} Coins** from {target.mention}!",
                color=0x57F287
            )
            await ctx.send(embed=embed)

        elif outcome == "fail":
            penalty = user_coins if user_coins < 500 else int(user_coins * 0.10)
            await collection.update_one({"_id": ctx.author.id}, {"$inc": {"coins": -penalty}, "$set": {"rob_cooldown": new_cooldown}})
            await collection.update_one({"_id": target.id}, {"$inc": {"coins": penalty}})

            embed = discord.Embed(
                title="💥 Robbery Botched",
                description=f"You tripped and dropped **{penalty:,} Coins** while running away! {target.mention} picked it up.",
                color=0xED4245
            )
            await ctx.send(embed=embed)

        elif outcome == "jail":
            jail_time = now + (5 * 3600)
            await collection.update_one({"_id": ctx.author.id}, {"$set": {"jail_until": jail_time, "rob_cooldown": new_cooldown}})
            
            embed = discord.Embed(
                title="🚔 BUSTED!",
                description=f"The police caught you red-handed trying to rob {target.mention}!\n\nYou have been thrown in jail for **5 Hours**. You cannot work or rob during this time.",
                color=0xED4245
            )
            embed.set_image(url="https://media.giphy.com/media/RYjnzPS8u0jAs/giphy.gif")
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RobCommand(bot))
