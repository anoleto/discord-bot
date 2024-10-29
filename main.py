
from __future__ import annotations

import os
import config

import discord
from discord.ext import commands, tasks
import os
from datetime import datetime

from utils.logging import log
from utils.logging import Ansi
from cmyui.mysql import AsyncSQLPool

from objects import glob

from commands import CATEGORIES
from utils.help import Help

class Bot(commands.Bot):
    def __init__(self) -> None:
        self.config = config
        intents = discord.Intents.default() # init intents
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(command_prefix=self.config.PREFIX, 
                         intents=intents,
                         activity=discord.CustomActivity(name=self.config.Status),
                         help_command=Help())
        
        self.startup_time = datetime.utcnow()
    
    async def setup_hook(self) -> None: 
        log("starting bot setup...", Ansi.CYAN)
        log("syncing slash commands...", Ansi.CYAN)
        await self.tree.sync()
        
        await self.load_extensions()
        log(f"logged in as {self.user} (ID: {self.user.id})", Ansi.BLUE)
        log("bot is ready!", Ansi.GREEN)

        self.check_db_connection.start()
    
    async def load_extensions(self) -> None:
        for category in CATEGORIES:
            category_path = f'./commands/{category}'
            if os.path.isdir(category_path):
                for filename in os.listdir(category_path):
                    if filename.endswith('.py') and not filename.startswith('__'):
                        try:
                            await self.load_extension(f'commands.{category}.{filename[:-3]}')
                            log(f'loaded command: {category}.{filename}', Ansi.GREEN)
                        except Exception as e:
                            log(f'failed to load {filename}: {e}', Ansi.RED)

    async def on_command(self, ctx: commands.Context) -> None:
        """logs every command executed"""
        if self.config.DEBUG:
            log(f"command executed: {ctx.command} by {ctx.author} in {ctx.guild}/{ctx.channel}", Ansi.YELLOW)

    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        """global error handler"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if self.config.DEBUG:
            log(f"command error in {ctx.command}: {str(error)}", Ansi.RED)
        
        await ctx.send(f"an error occurred: {str(error)}")

    async def on_connect(self) -> None:
        await self.initialize_db()

    async def initialize_db(self) -> None:
        try:
            glob.db = AsyncSQLPool()
            await glob.db.connect(glob.config.db_config)
            log('connected to MySQL!', Ansi.LGREEN)
        except Exception as e:
            log(f"database connection failed: {str(e)}", Ansi.RED)

    @tasks.loop(minutes=3)
    async def check_db_connection(self) -> None:
        """db connection check"""
        # XXX: per sometime the db just throws ConnectionResetError??
        # XXX: idk anymore i just want to sleep
        if glob.db:
            try:
                await glob.db.fetch('select 1') # just try to fetch somethign
            except:
                await self.initialize_db()

    @check_db_connection.before_loop
    async def before_check_db_connection(self) -> None:
        await self.wait_until_ready()

if __name__ == '__main__':
    try:
        bot = Bot()
        log("starting bot...", Ansi.CYAN)
        bot.run(config.TOKEN)
    except Exception as e:
        log(f"failed to start bot: {str(e)}", Ansi.RED)