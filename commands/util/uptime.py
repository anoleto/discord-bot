from __future__ import annotations

import discord
from discord.ext import commands
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import Bot

class Uptime(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot
    
    @commands.hybrid_command(
        name="uptime",
        description="check how long the bot has been running"
    )
    async def uptime(self, ctx: commands.Context) -> None:
        """check how long the bot has been running"""
        d: datetime = datetime.utcnow() - self.bot.startup_time # delta
        h: int # hours
        m: int # minutes
        s: int # seconds
        h, remainder = divmod(int(d.total_seconds()), 3600)
        m, s = divmod(remainder, 60)
        
        await ctx.send(f"online for: {h}h {m}m {s}s\nstarted at: {self.bot.startup_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")

async def setup(bot: Bot) -> None:
    await bot.add_cog(Uptime(bot))