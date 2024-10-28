from __future__ import annotations

import discord
import config

from discord.ext import commands
from typing import TYPE_CHECKING, Tuple, Optional
from datetime import datetime
from datetime import timedelta

from commands.osu.OsuApi.api import ApiClient
from utils.logging import log
from objects import glob

if TYPE_CHECKING:
    from main import Bot

class Profile(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        """Get player profile info from the Bancho.py-based server"""
        self.bot: Bot = bot
        self.api = ApiClient()
        self.server = config.Bancho

    @commands.hybrid_command(
        name="profile",
        aliases=['pf', 'osu'],
        description="get player profile",
    )
    async def profile(self, ctx: commands.Context, *, args: str = None) -> None:
        """get player profile
        usage: `!pf <username> (mode)`
        mode args:
        vn!std, vn!taiko, vn!mania, vn!ctb | rx!std, rx!taiko, rx!ctb | ap!std
        """
        username, mode = await self.parse_args(ctx, args)
        if username is None or mode is None:
            return

        modestr = self.get_mode_str(mode)
        
        try:
            profile = await self.api.get_player_info("all", username=username)
            player_info = profile["player"]["info"]
            player_stats = profile["player"]["stats"].get(str(mode))

            if not player_stats:
                await ctx.send("no stats available for the specified mode.")
                return

            creation_time = int(player_info["creation_time"])
            latest_activity = int(player_info["latest_activity"])

            playtime_seconds = player_stats["playtime"]
            days, remainder = divmod(playtime_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            playtime = f"{days}d {hours}h {minutes}m {seconds}s"

            embed = discord.Embed(title=f"{player_info['name']}'s {modestr} profile",
                                  color=discord.Color.random(),
                                  url=f"https://{self.server}/u/{player_info['id']}")
            
            embed.set_thumbnail(url=f"https://a.{self.server}/{player_info['id']}")

            # XXX: in refx theres xp calculation
            xp_check = f"**xp:** {player_stats['xp']}\n" if 'refx.online' in self.server else ""

            embed.add_field(name="performance", value=(
                f"**pp:** {player_stats['pp']:,}pp\n"
                f"{xp_check}"
                f"**accuracy:** {player_stats['acc']:.2f}%\n"
                f"**global rank:** #{player_stats['rank']:,} (:flag_{player_info['country']}:, "
                f"#{player_stats['country_rank']})\n"
                f"**playcount:** {player_stats['plays']:,}\n"
                f"**playtime:** {playtime}\n"
                f"**grades:** <:rank_x:1278891650520842362> {player_stats['xh_count']} <:grade_ssh:1251961164225581207> {player_stats['x_count']} "
                f"<:grade_sh:1251961168763945102> {player_stats['sh_count']} <:grade_s:1251961171335188551> {player_stats['s_count']} <:grade_a:1239381666552877056> {player_stats['a_count']}"
            ), inline=False)

            embed.add_field(name="general Info", value=(
                f"**account created:** <t:{creation_time}:R>\n"
                f"**last seen:** <t:{latest_activity}:R>"
            ), inline=False)

            await ctx.send(embed=embed)

        except Exception as e:
            log(e)
            await ctx.send("error getting profile. did you type the username correctly?")
            return

    async def parse_args(self, ctx: commands.Context, args: str) -> Tuple[Optional[str], int]:
        """parse the username and mode from the arguments."""
        # TODO: cleanup
        user_id = str(ctx.author.id)
        username = ""
        mode = 0

        mentioned_users = ctx.message.mentions
        mentioned_users = [user for user in mentioned_users if user.id != ctx.bot.user.id]

        if mentioned_users:
            mentioned_user = str(mentioned_users[0].id)
            try:
                result = await glob.db.fetch('select name, mode from users where id = %s', [mentioned_user])
                if result:
                    username = result['name']
                    mode = result['mode']
                else:
                    await ctx.send(f"user <@{mentioned_user}> not found in the database.")
                    return
            except Exception as err:
                await ctx.send(f"error retrieving profile from database: {err}")
                return
        else:
            if args:
                arg_parts = args.split()
                for arg in arg_parts:
                    mode = self.get_mode_id(arg)
                    arg_parts.remove(arg)
                    break
                username = " ".join(arg_parts).strip()

            if not username:
                result = await glob.db.fetch('select name, mode from users where id = %s', [user_id])
                if result:
                    username = result['name']
                    mode = result['mode'] if mode == 0 else mode
                else:
                    await ctx.send("no profile set. Use `!setprofile <name> (mode)` to set a default profile.")
                    return
                
        return username, mode
    
    # TODO: put these in a new file
    def get_mode_id(self, mode_str: str) -> int:
        """get mode id mapping from mode string."""
        mode_mapping = {
            "vn!std": 0,
            "vn!taiko": 1,
            "vn!catch": 2,
            "vn!mania": 3,
            "rx!std": 4,
            "rx!taiko": 5,
            "rx!catch": 6,
            "ap!std": 8
        }

        return mode_mapping.get(mode_str.lower(), 0)

    def get_mode_str(self, mode_id: int) -> str:
        """get mode string mapping from integer."""
        int2mode = {
            0: "vn!std",
            1: "vn!taiko",
            2: "vn!catch",
            3: "vn!mania",
            4: "rx!std",
            5: "rx!taiko",
            6: "rx!catch",
            8: "ap!std"
        }
        
        return int2mode.get(mode_id, "vn!std")

async def setup(bot: Bot) -> None:
    await bot.add_cog(Profile(bot))