from __future__ import annotations

import discord
import traceback
import textwrap

from discord.ext import commands
from typing import TYPE_CHECKING
from objects import glob

if TYPE_CHECKING:
    from main import Bot

class Eval(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot
    
    @commands.is_owner()
    @commands.hybrid_command(
        name="eval",
        description="eval",
    )
    async def eval_command(self, ctx: commands.Context, *, code: str) -> None:
        """eval"""
        
        exec_globals = globals()
        exec_locals = locals()

        indented_code = textwrap.indent(textwrap.dedent(code), '    ')
        wrapped_code = f"""
async def _execute():
{indented_code}
"""

        try:
            exec(wrapped_code, exec_globals, exec_locals)
            result = await exec_locals["_execute"]()
            await ctx.send(result)
        except Exception:
            await ctx.send(f"Error: {traceback.format_exc()}")

async def setup(bot: discord.Bot) -> None:
    await bot.add_cog(Eval(bot))