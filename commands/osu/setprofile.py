from __future__ import annotations

import discord
from discord.ext import commands
from typing import TYPE_CHECKING

from objects import glob
from utils.OsuMapping import Mode

if TYPE_CHECKING:
    from main import Bot

class SetProfile(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot
        self.mode = Mode

    @commands.hybrid_command(
        name="setprofile",
        description="set your in-game username and mode.",
    )
    async def setprofile(self, ctx: commands.Context, username: str = None, mode: str = None) -> None:
        """set the in-game username and mode."""
        if not username or not mode:
            await ctx.send("you must provide both an username and a mode: `!setprofile <username> <mode>`")
            return

        mode_int = self.mode.from_string(mode)
        user_id = str(ctx.author.id)

        result = await glob.db.fetch('select * from users where id = %s', [user_id])

        if result:
            await glob.db.execute(
                'update users set name = %s, mode = %s where id = %s',
                [username, mode_int, user_id]
            )
        else:
            await glob.db.execute(
                'insert into users (id, name, mode) values (%s, %s, %s)',
                [user_id, username, mode_int]
            )

        await ctx.send(f"profile set for {username} in mode {mode}.")

    def get_mode_id(self, mode_str: str) -> int:
        """Map a mode string to its corresponding integer ID."""
        mode_mapping = {
            "vn!std": 0,
            "vn!taiko": 1,
            "vn!catch": 2,
            "vn!mania": 3,
            "rx!std": 4,
            "rx!taiko": 5,
            "rx!catch": 6,
            "ap!std": 8,
        }

        return mode_mapping.get(mode_str.lower(), 0)

async def setup(bot: Bot) -> None:
    await bot.add_cog(SetProfile(bot))