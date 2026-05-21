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
            return await ctx.send("You pat your own pockets. Congratulations, you robbed yourself.")

        collection = self.bot.db["daily_cooldowns"]
        user_data = await collection.find_one({"_id": ctx.author.id}) or {}
        target_data = await collection.find_one({"_id": target.id}) or {}
        now = time.time()
        
        # --- CUSTOM EMOJIS ---
        cash_emoji = "<a:cash:1506921225484767282>"
        cops_emoji = "<:cops:1506992674991902830>"
        jail_emoji = "<:jail:1506992899672379492>"
        shield_emoji = "<a:shield:1506993136084451348>"
        ninja_emoji = "<a:ninja:1506993597378068541>"
        botched_emoji = "<:botched:1506993810968678520>"
        busted_emoji = "<:busted:1506994017798197358>"

        # --- CHECKS ---
        jail_until = user_data.get("jail_until", 0)
        if now < jail_until:
            return await ctx.send(f"{jail_emoji} **You are in JAIL!** You can't rob anyone from behind bars. Released <t:{int(jail_until)}:R>.")
            
        rob_cd = user_data.get("rob_cooldown", 0)
        if now < rob_cd:
            return await ctx.send(f"{cops_emoji} The cops are actively patrolling. Lay low. You can strike again <t:{int(rob_cd)}:R>.")

        target_coins = target_data.get("coins", 0)
        if target_coins < 1000:
            return await ctx.send(f"They don't even have 1,000 Coins. Find a richer target to rob!")

        pendant_until = target_data.get("pendant_until", 0)
        if now < pendant_until:
            await collection.update_one({"_id": ctx.author.id}, {"$set": {"rob_cooldown": now + 1800}})
            return await ctx.send(f"{shield_emoji} **Robbery Failed!** {target.mention} is protected by a magical Pendant! You flee the scene.")

        # --- OUTCOME MECHANICS ---
        user_coins = user_data.get("coins", 0)
        outcome = random.choices(["success", "fail", "jail"], weights=[40, 30, 30])[0]
        new_cooldown = now + 1800 

        if outcome == "success":
            stolen_percent = random.uniform(0.05, 0.15)
            stolen_amount = int(target_coins * stolen_percent)
            
            await collection.update_one({"_id": target.id}, {"$inc": {"coins": -stolen_amount}})
            await collection.update_one({"_id": ctx.author.id}, {"$inc": {"coins": stolen_amount}, "$set": {"rob_cooldown": new_cooldown}})
            
            text = (
                f"{ninja_emoji} **Heist Successful!**\n"
                f"You slipped into the shadows and stole {cash_emoji} **{stolen_amount:,}** from {target.mention}!\n"
                f"-# They won't even realize it's gone until they check their wallet."
            )
            await ctx.send(content=text)

        elif outcome == "fail":
            penalty = user_coins if user_coins < 500 else int(user_coins * 0.10)
            await collection.update_one({"_id": ctx.author.id}, {"$inc": {"coins": -penalty}, "$set": {"rob_cooldown": new_cooldown}})
            await collection.update_one({"_id": target.id}, {"$inc": {"coins": penalty}})

            text = (
                f"{botched_emoji} **Robbery Botched!**\n"
                f"You tripped over a trash can while trying to rob {target.mention} and dropped {cash_emoji} **{penalty:,}** in the panic!\n"
                f"-# They picked up your dropped cash and walked away laughing."
            )
            await ctx.send(content=text)

        elif outcome == "jail":
            jail_time = now + (5 * 3600) # 5 Hours
            await collection.update_one({"_id": ctx.author.id}, {"$set": {"jail_until": jail_time, "rob_cooldown": new_cooldown}})
            
            text = (
                f"{busted_emoji} **BUSTED!**\n"
                f"The police caught you red-handed trying to pickpocket {target.mention}!\n"
                f"You have been thrown in a jail cell for **5 Hours**.\n"
                f"-# You cannot use /work or /rob until your sentence is over.\n"
                f"https://media.giphy.com/media/RYjnzPS8u0jAs/giphy.gif"
            )
            await ctx.send(content=text)

async def setup(bot):
    await bot.add_cog(RobCommand(bot))
