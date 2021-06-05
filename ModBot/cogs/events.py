import discord
from discord.ext import commands

from typing import Union
import asyncio
from datetime import datetime, timedelta
import asqlite


class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print('EventsCog init')

    @commands.Cog.listener()
    async def on_ready(self):
        if self.bot.first_on_ready:
            self.bot.db = await asqlite.connect('guild_config.db', check_same_thread=False)
            self.bot.configs = await self.bot.load_all_configs()
            self.bot.first_on_ready = False
        print(f'\n\nLogged in as: {self.bot.user.name} - {self.bot.user.id}\nVersion: {discord.__version__}\n')
        print(f'Successfully logged in and booted...!')

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, banned: Union[discord.Member, discord.User]):
        mod, reason = None, "Unknown"
        await asyncio.sleep(3)
        try:
            async for entry in guild.audit_logs(limit=10, action=discord.AuditLogAction.ban):
                if entry.target == banned:
                    mod = entry.user
                    reason = entry.reason
        except discord.Forbidden:
            reason = '*Bot is missing Audit Log Permissions!*'
        embed = discord.Embed(title=f'{banned} has been banned! ({banned.id})',
                              description=f'Banned by: {mod.mention if mod else "Unknown"}\
        \n\nReason: {reason or "No reason specified"}', color=discord.Color.red())
        embed.set_thumbnail(url=banned.avatar_url)

        await self.bot.get_config(guild).log(embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, unbanned: discord.User):
        mod, reason = None, "Unknown"
        await asyncio.sleep(2)
        try:
            async for entry in guild.audit_logs(limit=10, action=discord.AuditLogAction.unban):
                if entry.target == unbanned:
                    mod = entry.user
                    reason = entry.reason
        except discord.Forbidden:
            reason = '*Bot is missing Audit Log Permissions!*'
        embed = discord.Embed(title=f'{unbanned} has been unbanned! ({unbanned.id})',
                              description=f'Unbanned by: {mod.mention if mod else "Unknown"}\
        \n\nReason: {reason or "No reason specified"}', color=discord.Color.green())
        embed.set_thumbnail(url=unbanned.avatar_url)

        await self.bot.get_config(guild).log(embed)

    @commands.Cog.listener()
    async def on_member_remove(self, kicked: discord.Member):
        mod, reason = None, "Unknown"
        await asyncio.sleep(2)
        d = datetime.now() - timedelta(seconds=5)
        try:
            async for entry in kicked.guild.audit_logs(after=d, limit=5, action=discord.AuditLogAction.kick):
                if entry.target == kicked:
                    mod = entry.user
                    reason = entry.reason
        except discord.Forbidden:
            return
        if not mod:
            return
        embed = discord.Embed(title=f'{kicked} has been kicked! ({kicked.id})',
                              description=f'Kicked by: {mod.mention if mod else "Unknown"}\
        \n\nReason: {reason or "No reason specified"}', color=discord.Color.red())
        embed.set_thumbnail(url=kicked.avatar_url)

        await self.bot.get_config(kicked.guild).log(embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild and not message.author.bot:
            ctx = await self.bot.get_context(message)
            if ctx.snipe:
                self.bot.sniped[:0] = [message]
                self.bot.sniped = self.bot.sniped[:5000]


def setup(bot):
    bot.add_cog(EventsCog(bot))
