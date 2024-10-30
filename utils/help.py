from __future__ import annotations

import discord
import psutil
from discord.ext import commands

class Help(commands.HelpCommand):
    """some more cleaner help command maybe?"""
    async def send_help_message(self, ctx: commands.Context, help_text: str) -> None:
        embed = discord.Embed(title="help", description=help_text, color=discord.Color.random())
        await ctx.send(embed=embed)

    async def send_bot_help(self, mapping: dict) -> None:
        help_text = "here are the commands available:\n"
        
        for cog, commands in mapping.items():
            if commands:
                if cog is not None:
                    for command in commands:
                        help_text += f"`{command.name}`: {command.help}\n"
        
        if help_text == "here are the commands available:\n":
            help_text += "no commands available."
        
        # XXX: add infos
        memory_usage = psutil.Process().memory_info().rss / 1024 ** 2
        cpu = psutil.cpu_percent(interval=1)
        
        help_text += f"\nmemory usage: {memory_usage:.2f} MB\nCPU usages: {cpu}%"

        await self.send_help_message(self.context, help_text)

    async def send_cog_help(self, cog: commands.Cog) -> None:
        help_text = f"**{cog.qualified_name} commands:**\n"
        for command in cog.get_commands():
            help_text += f"`{command.name}`: {command.help}\n"
        
        await self.send_help_message(self.context, help_text)

    async def send_command_help(self, command: commands.Command) -> None:
        help_text = f"**{command.name}**\n{command.help}\n"
        help_text += f"**usage:** {self.get_command_signature(command)}"
        await self.send_help_message(self.context, help_text)