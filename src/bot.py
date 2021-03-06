import logging
import os
from pathlib import Path

import coloredlogs
import disnake
from disnake.ext import commands
from dotenv import load_dotenv

from utils.database import SqliteSingleton


class BuildBot(commands.Bot):
    def __init__(self):
        load_dotenv()
        intents = disnake.Intents.default()
        intents.members = True
        # intents.message_content = True

        super().__init__(reload=True, intents=intents) # Live reload of cogs on edits.

        self.log = logging.getLogger("BuildBot")
        coloredlogs.install(logger=self.log)
        logging.basicConfig(level=logging.INFO, format="(%(asctime)s) %(levelname)s %(message)s", datefmt="%m/%d/%y - %H:%M:%S %Z")

        self.loop.create_task(self.prepare_bot())

    async def prepare_bot(self):
        self.log.info("Connecting to database...")
        self.conn = await SqliteSingleton.get_connection()
        self.log.info("Database connection established.")

    def load_cogs(self):
        for file in os.listdir(str(Path(__file__).parents[0])+"/cogs"):
            if file.endswith(".py") and not file.startswith("_"):
                self.load_extension(f"cogs.{file[:-3]}")

        self.log.info("All cogs have been loaded. ")

    def run(self):
        if not os.getenv("BOT_TOKEN") or os.getenv("BOT_TOKEN") == "":
            return self.log.error("No .env file setup with proper token paramter.")
        self.load_cogs()
        super().run(os.getenv("BOT_TOKEN"))

bot = BuildBot()
bot.run()
