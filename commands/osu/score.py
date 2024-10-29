from __future__ import annotations

import discord
import config

from discord.ext import commands
from typing import TYPE_CHECKING, List, Dict
from objects import glob

from commands.osu.OsuApi.api import ApiClient

from utils.logging import log
from utils.OsuMapping import Mode, grade_emojis
from utils.args import ArgParsing

if TYPE_CHECKING:
    from main import Bot

# TODO: top, simulate, compare
# and use usecases/performance

class Score(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot
        self.api = ApiClient()
        self.server = config.Bancho
        self.mode = Mode
        self.current_page = 0
        self.pages = {}
        self.retries = {}
        self.player_id = None
        self.arg = ArgParsing

    @commands.command(
        name="recent",
        aliases=['r', 'rs'],
        description="get player's recent score",
    )
    async def recent(self, ctx: commands.Context, *, args: str = None) -> None:
        """get player's most recent scores."""
        username, mode = await self.arg.parse_args(self, ctx, args)

        if username is None or mode is None:
            return

        try:
            response = await self.api.get_player_scores("recent", username=username, mode_arg=mode)
            if response['status'] != 'success':
                await ctx.send("failed to fetch scores.")
                return
            
            # TODO: move
            self.player_id = response['player']['id']

            scores = response['scores']

            if not scores:
                await ctx.send("no recent scores found.")
                return
            
            self.pages = self.create_pages(scores)
            self.current_page = 0

            embed = self.create_embed(self.pages[self.current_page][0], username)
            message = await ctx.send(f"recent score for {response['player']['name']}: ", embed=embed, view=self.create_buttons(len(self.pages)))

            # XXX: ima just implement pagination by setting up the navigation buttons and using a loop to listen for button shi
            # then we track the current_page and updating it based on button clicks, you get the point
            # on the old code i really used the emojis to handle pagination.. :broken_heart:
            def check(interaction: discord.Interaction):
                return interaction.message.id == message.id and interaction.user.id == ctx.author.id
            
            while True:
                try:
                    interaction = await self.bot.wait_for("interaction", check=check, timeout=60.0)
                    if interaction.data['custom_id'] == 'previous':
                        self.current_page = max(0, self.current_page - 1)
                    elif interaction.data['custom_id'] == 'next':
                        self.current_page = min(len(self.pages) - 1, self.current_page + 1)

                    embed = self.create_embed(self.pages[self.current_page][0], username)
                    await interaction.response.edit_message(embed=embed, view=self.create_buttons(len(self.pages)))
                except Exception as e:
                    log(f"error handling pagination: {e}")
                    break

        except Exception as e:
            await ctx.send(f"an error occurred: {e}")

    def create_pages(self, scores: List[Dict]) -> List[List[Dict]]:
        return [[score] for score in scores]

    def create_embed(self, score: Dict, username: str) -> discord.Embed:
        beatmap = score['beatmap']

        # NOTE: users cant download failed replay
        ReplayCheck = f" ▸ [Replay](https://api.{self.server}/v1/get_replay?id={score['id']})" if score['grade'] != 'F' else ""

        embed = discord.Embed(
            title=f"{beatmap['artist']} - {beatmap['title']} [{beatmap['version']}]",
            description=f"▸ {grade_emojis.get(score['grade'], score['grade'])} ▸ **{round(score['pp'], 2)}pp** ▸ {float(score['acc']):.2f}%\n"
                        f"▸ {score['score']:,} ▸ {score['max_combo']}x/{beatmap['max_combo']}x ▸ [{score['n300']}/{score['n100']}/{score['n50']}/{score['nmiss']}]\n"
                        f"{ReplayCheck}\n",
            color=0x2ECC71 if score['grade'] != 'F' else 0xE74C3C
        )
        
        embed.set_image(url=f"https://assets.ppy.sh/beatmaps/{beatmap['set_id']}/covers/cover.jpg")
        embed.set_author(
            name=f"{beatmap['artist']} - {beatmap['title']} [{beatmap['version']}] {score['mods_readable']} [0.0★]",
            icon_url=f"https://a.{self.server}/{self.player_id}",
            url=f"https://osu.ppy.sh/b/{beatmap['id']}"
        )
        embed.set_footer(text=f"on {self.server}") # TODO: add retry count and datetime

        return embed

    def create_buttons(self, total_pages: int) -> discord.ui.View:
        view = discord.ui.View(timeout=None)
        if self.current_page > 0:
            view.add_item(discord.ui.Button(label="<-", custom_id='previous', style=discord.ButtonStyle.primary))
        if self.current_page < total_pages - 1:
            view.add_item(discord.ui.Button(label="->", custom_id='next', style=discord.ButtonStyle.primary))

        return view

async def setup(bot: Bot) -> None:
    await bot.add_cog(Score(bot))