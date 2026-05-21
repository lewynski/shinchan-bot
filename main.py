import os
import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URI = os.getenv('MONGO_URI')

intents = discord.Intents.default()
intents.message_content = True

class ShinchanBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.db_client = None
        self.db = None

    async def setup_hook(self):
        # 1. Initialize MongoDB
        print("Connecting to MongoDB...")
        self.db_client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.db_client['shinchan_db']
        
        try:
            await self.db_client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")

        # 2. Load Cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                # This loads the files without the '.py' extension (e.g., 'cogs.ping')
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f"Loaded Cog: {filename}")

    async def close(self):
        if self.db_client:
            self.db_client.close()
        await super().close()

bot = ShinchanBot()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    await bot.change_presence(activity=discord.Game(name="Domain Expansion"))

if __name__ == '__main__':
    bot.run(TOKEN)
