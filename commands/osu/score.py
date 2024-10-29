from __future__ import annotations

import discord
import config

from discord.ext import commands
from typing import TYPE_CHECKING
from objects import glob

from commands.osu.OsuApi.api import ApiClient

from utils.logging import log
from utils.OsuMapping import Mods, Mode

if TYPE_CHECKING:
    from main import Bot

# TODO:

class Recent(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot
        self.api = ApiClient()
        self.server = config.Bancho
        self.mode = Mode

    @commands.hybrid_command(
        name="recent",
        aliases=['r', 'rs'],
        description="get player's recent score",
    )
    async def recent(self, ctx: commands.Context, *, args: str = None) -> None:
        """get player's most recent score."""
        ...

class Top(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot
        self.api = ApiClient()
        self.server = config.Bancho
        self.mode = Mode

    @commands.hybrid_command(
        name="top",
        aliases=['osutop', 't'],
        description="get player's top score",
    )
    async def top(self, ctx: commands.Context, *, args: str = None) -> None:
        """get player's top score."""
        ...


async def setup(bot: Bot) -> None:
    await bot.add_cog(Recent(bot))
    await bot.add_cog(Top(bot))