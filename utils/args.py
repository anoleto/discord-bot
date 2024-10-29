from __future__ import annotations

from utils.OsuMapping import Mode

from typing import Tuple, Optional
from discord.ext import commands
from objects import glob

class ArgParsing:
    def __init__(self) -> None:
        """for the annoying args parsing"""
        self.mode = Mode

    async def parse_args(self, ctx: commands.Context, args: str) -> Tuple[Optional[str], Optional[int]]:
        user_id = str(ctx.author.id)
        username, mode = None, None

        mentioned_users = [user for user in ctx.message.mentions if user.id != ctx.bot.user.id]
        
        if mentioned_users:
            mentioned_user_id = str(mentioned_users[0].id)
            user_data = await glob.db.fetch('SELECT name, mode FROM users WHERE id = %s', [mentioned_user_id])
            if user_data:
                username, mode = user_data['name'], user_data['mode']
            else:
                await ctx.send(f"User <@{mentioned_user_id}> not found in the database.")
                return None, None
        else:
            # XXX: parse arguments when no user is mentioned
            if args:
                arg_parts = args.split()
                potential_mode = self.mode.from_string(arg_parts[0])

                if potential_mode is not None:
                    mode = potential_mode
                    if len(arg_parts) > 1:
                        username = arg_parts[1]
                else:
                    username = arg_parts[0]
                    if len(arg_parts) > 1:
                        mode = self.mode.from_string(arg_parts[1])

            # XXX: if username is still None, we use the user's profile
            if not username:
                user_data = await glob.db.fetch('SELECT name, mode FROM users WHERE id = %s', [user_id])
                if user_data:
                    username = user_data['name']
                    mode = mode if mode is not None else user_data['mode']
                else:
                    await ctx.send("No profile set. Use `!setprofile <name> (mode)` to set a default profile.")
                    return None, None

        return username, mode