import random
import time
import discord
from discord.ext import commands

# --- JOB DATABASE ---
JOBS = {
    "criminal": {"name": "Criminal", "emoji": "<a:criminal:1506977349055287307>", "stages": ["Street Thug", "Mobster", "Crime Boss"]},
    "dancer": {"name": "Dancer", "emoji": "<a:dancer:1506977182629626009>", "stages": ["Backup Dancer", "Lead Dancer", "Pop Star"]},
    "singer": {"name": "Singer", "emoji": "<a:singer:1506977180784132146>", "stages": ["Busker", "Vocalist", "Global Idol"]},
    "programmer": {"name": "Programmer", "emoji": "<a:programmer:1506977179165130752>", "stages": ["Junior Dev", "Software Engineer", "Tech Lead"]},
    "teacher": {"name": "Teacher", "emoji": "<a:teacher:1506977177386746038>", "stages": ["Substitute", "Teacher", "Professor"]},
    "engineer": {"name": "Engineer", "emoji": "<a:engineer:1506977175331667988>", "stages": ["Apprentice", "Engineer", "Chief Engineer"]},
    "doctor": {"name": "Doctor", "emoji": "<a:doctor:1506977171237900379>", "stages": ["Rookie Doctor", "Doctor", "International Doctor"]}
}

class JobSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=job["name"], value=key, emoji=discord.PartialEmoji.from_str(job["emoji"]))
            for key, job in JOBS.items()
        ]
        super().__init__(placeholder="Select your career path...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_job = self.values[0]
        collection = interaction.client.db["daily_cooldowns"]
        
        await collection.update_one(
            {"_id": interaction.user.id},
            {"$set": {"job": selected_job, "shifts": 0}},
            upsert=True
        )
        
        job_info = JOBS[selected_job]
        await interaction.response.edit_message(
            content=f"✅ You have officially started your career as a {job_info['emoji']} **{job_info['stages'][0]}**!\nUse `/work` again to start your first shift.",
            view=None
        )

class JobSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(JobSelect())

# --- RESIGN BUTTON VIEW ---
class ResignView(discord.ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=120)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You can only resign from your own job!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Resign", style=discord.ButtonStyle.danger)
    async def resign_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        collection = interaction.client.db["daily_cooldowns"]
        now = time.time()
        
        # 5 Hour Cooldown Penalty
        resign_cooldown = now + (5 * 3600)
        
        # Unset removes the job and shifts completely from the user's database profile
        await collection.update_one(
            {"_id": interaction.user.id},
            {
                "$unset": {"job": "", "shifts": ""},
                "$set": {"resign_cooldown": resign_cooldown}
            }
        )
        
        button.disabled = True
        button.label = "Resigned"
        button.style = discord.ButtonStyle.secondary
        await interaction.response.edit_message(view=self)
        
        # Send a private confirmation that they quit with the new small text cooldown
        text = (
            "💼 You have officially resigned from your job. You must wait **5 Hours** before taking a new occupation.\n"
            f"-# You are exhausted. Your next shift is available <t:{int(resign_cooldown)}:R>."
        )
        
        await interaction.followup.send(text, ephemeral=True)

class WorkCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_stage_and_salary(self, shifts):
        if shifts < 10: return 0, random.randint(1000, 3000)
        elif shifts < 25: return 1, random.randint(3000, 6000)
        else: return 2, random.randint(6000, 10000)

    @commands.hybrid_command(name="work", aliases=["swork"], description="Work a shift to earn money based on your occupation.")
    async def work(self, ctx: commands.Context):
        collection = self.bot.db["daily_cooldowns"]
        user_data = await collection.find_one({"_id": ctx.author.id}) or {}
        now = time.time()
        
        # 1. Jail Check
        jail_until = user_data.get("jail_until", 0)
        if now < jail_until:
            return await ctx.send(f"🚔 **You are in JAIL!** You cannot work until <t:{int(jail_until)}:R>.")

        job_key = user_data.get("job")

        # 2. Work Cooldown Check
        work_cd = user_data.get("work_cooldown", 0)
        if now < work_cd:
            # If they are on cooldown but have a job, attach the Resign button so they can still quit
            view = ResignView(ctx.author.id) if job_key else None
            return await ctx.send(f"⏳ You are exhausted. Your next shift is available <t:{int(work_cd)}:R>.", view=view)

        # 3. Unemployed & Resign Cooldown Check
        if not job_key or job_key not in JOBS:
            resign_cd = user_data.get("resign_cooldown", 0)
            if now < resign_cd:
                return await ctx.send(f"⏳ You recently resigned from your job. You can apply for a new occupation <t:{int(resign_cd)}:R>.")
                
            text = "🏢 **City Employment Agency**\nYou are currently unemployed. Select a career path from the menu below to start earning."
            return await ctx.send(content=text, view=JobSelectView())

        # 4. Work Shift & Salary Payout
        shifts = user_data.get("shifts", 0) + 1
        stage_idx, salary = self.get_stage_and_salary(shifts)
        job_info = JOBS[job_key]
        job_title = job_info["stages"][stage_idx]
        next_work = now + 3600
        
        await collection.update_one(
            {"_id": ctx.author.id},
            {"$inc": {"coins": salary, "shifts": 1}, "$set": {"work_cooldown": next_work}},
            upsert=True
        )

        cash_emoji = "<a:cash:1506921225484767282>"
        text = (
            f"{job_info['emoji']} You earned {cash_emoji} **{salary:,}** for your hardwork.\n"
            f"-# Great job, {job_title}!"
        )
        
        # Attach the Resign button to the successful work payout
        view = ResignView(ctx.author.id)
        await ctx.send(content=text, view=view)

async def setup(bot):
    await bot.add_cog(WorkCommand(bot))
