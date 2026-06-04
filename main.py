import os
import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# 1. Securely load secrets from environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URI = os.getenv('MONGO_URI')

# 2. Configure Discord Intents so Shinchan can track messages and roles
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# 3. Create the Bot Class
class ShinchanBot(commands.Bot):
    def __init__(self):
        # Set your prefix to 's' as requested
        super().__init__(command_prefix='s', intents=intents)
        self.db_client = None
        self.db = None

    async def setup_hook(self):
        # A. Initialize Asynchronous MongoDB Connection
        print("Connecting to MongoDB...")
        self.db_client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.db_client['shinchan_db']
        
        try:
            await self.db_client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")

        # B. Automatically Scan and Load Cogs from the /cogs folder
        print("Loading extensions...")
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and filename != '__init__.py':
                await self.load_extension(f'cogs.{filename[:-3]}')
                print(f"Loaded Cog: {filename}")
                
        # C. Sync Slash Commands with Discord Global Servers
        print("Syncing slash commands...")
        try:
            await self.tree.sync()
            print("Slash commands globally synced successfully!")
        except Exception as e:
            print(f"Failed to sync slash commands: {e}")

    async def close(self):
        # Gracefully shut down database connections on close
        if self.db_client:
            self.db_client.close()
        await super().close()

# 4. Initialize the bot instance
bot = ShinchanBot()

# 5. Core Global Events
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    print(f'Active in {len(bot.guilds)} servers.')
    
    # Set Shinchan's rich presence status
    await bot.change_presence(activity=discord.Game(name="/shinchan 666"))

# 6. Run the script using the environment token
if __name__ == '__main__':
    bot.run(TOKEN)
