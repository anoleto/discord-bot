from __future__ import annotations

import discord
from discord.ext import commands
from typing import Set, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from main import Bot

class PollView(discord.ui.View):
    def __init__(self) -> None:
        """for the poll view buttons"""
        super().__init__(timeout=None)
        self.yes_votes: int = 0
        self.no_votes: int = 0
        self.voters: Set[int] = set()
    
    @discord.ui.button(label="yes (0)", style=discord.ButtonStyle.green, custom_id="yes")
    async def yes_button( # yes king
        self, 
        interaction: discord.Interaction, 
        button: discord.ui.Button[PollView]
    ) -> None:
        if interaction.user.id in self.voters:
            await interaction.response.send_message("you've already voted!", ephemeral=True)
            return
        
        self.yes_votes += 1
        self.voters.add(interaction.user.id)
        button.label = f"yes ({self.yes_votes})"
        
        no_button: discord.ui.Button = [x for x in self.children if x.custom_id == "no"][0]  # type: ignore
        no_button.label = f"no ({self.no_votes})"
        
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(label="no (0)", style=discord.ButtonStyle.red, custom_id="no")
    async def no_button(
        self, 
        interaction: discord.Interaction, 
        button: discord.ui.Button[PollView]
    ) -> None:
        if interaction.user.id in self.voters:
            await interaction.response.send_message("you've already voted!", ephemeral=True)
            return
        
        self.no_votes += 1
        self.voters.add(interaction.user.id)
        button.label = f"No ({self.no_votes})"
        
        yes_button: discord.ui.Button = [x for x in self.children if x.custom_id == "yes"][0]  # type: ignore
        yes_button.label = f"Yes ({self.yes_votes})"
        
        await interaction.response.edit_message(view=self)

class Poll(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot: Bot = bot
    
    @commands.hybrid_command(
        name="poll",
        description="simple command to create a yes/no poll"
    )
    async def create_poll(
        self, 
        ctx: commands.Context,
        question: str,
        timeout_minutes: Optional[int] = None
    ) -> None:
        """simple command to create a yes/no poll"""
        embed: discord.Embed = discord.Embed(
            title="poll",
            description=question,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"created by {ctx.author.display_name}")
        
        if timeout_minutes is not None:
            embed.add_field(
                name="timeout", 
                value=f"this poll will end in {timeout_minutes} minutes"
            )
        
        view: PollView = PollView()
        await ctx.send(embed=embed, view=view)

    @create_poll.autocomplete('timeout_minutes')
    async def timeout_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[discord.app_commands.Choice[int]]:
        return [
            discord.app_commands.Choice(name='1 minute', value=1),
            discord.app_commands.Choice(name='5 minutes', value=5),
            discord.app_commands.Choice(name='10 minutes', value=10),
            discord.app_commands.Choice(name='30 minutes', value=30),
            discord.app_commands.Choice(name='1 hour', value=60)
        ]

async def setup(bot: Bot) -> None:
    await bot.add_cog(Poll(bot))