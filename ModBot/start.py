import os
import sys

try:
    os.chdir(os.path.dirname(sys.argv[0]))
except OSError:
    pass

import discord

from discord.ext import commands
import json
from typing import Optional
from custom_funcs import *

import datetime

with open('config.json') as setup:
    secrets = json.load(setup)

intents = discord.Intents.default()
intents.members = secrets['MEMBER_INTENTS']
intents.presences = secrets['PRESENCE_INTENTS']


class CustomBot(commands.Bot):
    db = None
    sniped = []
    first_on_ready = True

    def __init__(self, **options):
        super().__init__(help_command=None, description=None, **options)
        self._secrets = secrets
        self._default_prefix = secrets['DEFAULT_PREFIX']

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=cls or CustomContext)

    class GuildConfig(object):
        def __init__(self, guild: discord.Guild, logs: discord.TextChannel = None,
                     prefix: str = None, mute: discord.Role = None):
            self._guild = guild
            self._logs = logs
            self._prefix = prefix
            self._mute = mute

        async def set_config(self, **kwargs):
            self._logs = kwargs.get('logs', self._logs)
            self._prefix = kwargs.get('prefix', self._prefix)
            self._mute = kwargs.get('mute', self._mute)

            async with bot.db.cursor() as cursor:
                await cursor.execute('REPLACE INTO config VALUES(?, ?, ?, ?)',
                                     (self._guild.id, self._logs.id, self._prefix, self._mute.id))
                await bot.db.commit()
            await bot.GuildConfig.load_all_configs()
            return self

        @staticmethod
        async def load_all_configs():
            guild_configs = []
            async with bot.db.cursor() as cursor:
                for row in await cursor.execute('SELECT * FROM config'):
                    if not (guild := bot.get_guild(row[0])):
                        continue
                    log_channel = guild.get_channel(row[1])
                    prefix = row[2]
                    mute = guild.get_role(row[3])
                    guild_configs.append(bot.GuildConfig(guild, log_channel, prefix, mute))

            bot.configs = guild_configs
            return guild_configs

        @staticmethod
        def get_config(guild: discord.Guild):
            if not isinstance(guild, discord.Guild):
                return None
            for config in bot.configs:
                if config.guild == guild:
                    return config
            return bot.GuildConfig(guild)

        async def multi_ban(self, mod: discord.Member, users: [discord.Member, discord.User], reason: Optional[str]):
            if not mod.guild_permissions.ban_members:
                return
            not_banned, banned = [], []
            for user in users:
                if isinstance(user, discord.Member):
                    if (not mod.top_role > user.top_role and self.guild.owner != mod) or user == self.guild.owner:
                        not_banned.append(user)
                        continue
                if user == mod:
                    not_banned.append(user)
                    continue
                try:
                    await mod.guild.ban(user, reason=f'{mod}: {reason if reason else "No reason specified"}',
                                        delete_message_days=7)
                    banned.append(user)
                except (discord.Forbidden, discord.HTTPException):
                    not_banned.append(user)
            if len(users) == len(not_banned):
                raise CannotPunish('ban', not_banned, mod)
            return banned, not_banned

        async def multi_kick(self, mod: discord.Member, users: [discord.Member], reason: Optional[str]):
            if not mod.guild_permissions.kick_members:
                return
            not_kicked, kicked = [], []
            for user in users:
                if (not mod.top_role > user.top_role and self.guild.owner != mod) \
                        or user == self.guild.owner or user == mod:
                    not_kicked.append(user)
                    continue
                try:
                    await self.guild.kick(user, reason=f'{mod}: {reason if reason else "No reason specified"}')
                    kicked.append(user)
                except (discord.Forbidden, discord.HTTPException):
                    not_kicked.append(user)
            if len(users) == len(not_kicked):
                raise CannotPunish('kick', not_kicked, mod)
            return kicked, not_kicked

        async def multi_unban(self, mod: discord.Member, users: [discord.Member], reason: Optional[str]):
            if not mod.guild_permissions.ban_members:
                return
            unbanned, not_unbanned = [], []
            for user in users:
                try:
                    await self.guild.unban(user, reason=f'{mod}: {reason if reason else "No reason specified"}')
                    unbanned.append(user)
                except (discord.Forbidden, discord.HTTPException):
                    not_unbanned.append(user)
            if len(users) == len(not_unbanned):
                raise CannotPunish('unban', not_unbanned, mod)
            return unbanned, not_unbanned

        async def multi_mute(self, mod: discord.Member, users: [discord.Member], reason: Optional[str]):
            if not mod.guild_permissions.manage_roles or not self.mute:
                return
            muted, not_muted = [], []
            for user in users:
                if (not mod.top_role > user.top_role and self.guild.owner != mod) \
                        or user == self.guild.owner or user == mod:
                    not_muted.append(user)
                    continue
                try:
                    await user.add_roles(self.mute, reason=f'{mod}: {reason if reason else "No reason specified"}')
                    muted.append(user)
                except (discord.Forbidden, discord.HTTPException):
                    not_muted.append(user)
            if len(users) == len(not_muted):
                raise CannotPunish('mute', not_muted, mod)
            return muted, not_muted

        async def multi_unmute(self, mod: discord.Member, users: [discord.Member], reason: Optional[str]):
            if not mod.guild_permissions.manage_roles or not self.mute:
                return
            unmuted, not_unmuted = [], []
            for user in users:
                if (not mod.top_role > user.top_role and self.guild.owner != mod) \
                        or user == self.guild.owner or user == mod:
                    not_unmuted.append(user)
                    continue
                try:
                    await user.remove_roles(self.mute, reason=f'{mod}: {reason if reason else "No reason specified"}')
                    unmuted.append(user)
                except (discord.Forbidden, discord.HTTPException):
                    not_unmuted.append(user)
            if len(users) == len(not_unmuted):
                raise CannotPunish('unmute', not_unmuted, mod)
            return unmuted, not_unmuted

        async def log(self, embed: discord.Embed):
            if not self._logs:
                return
            try:
                embed.set_footer(text=datetime.datetime.now().strftime("%A, %d %b %Y, %I:%M:%S %p UTC"))
                return await self._logs.send(embed=embed)
            except (discord.HTTPException, discord.Forbidden) as e:
                print(e)

        @property
        def guild(self):
            return self._guild

        @property
        def logs(self):
            return self._logs

        @property
        def prefix(self):
            return self._prefix

        @property
        def mute(self):
            return self._mute

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content in [f"<@!{self.user.id}>", f"<@{self.user.id}>"]:
            prefix = _get_prefix(self, message)
            embed = embed_create(message.author, title='Pinged!', description=f'The current prefix is ``{prefix}``')
            await message.channel.send(embed=embed)

        await self.process_commands(message)

    @property
    def secrets(self):
        return self._secrets

    @property
    def default_prefix(self):
        return self._default_prefix


class CustomContext(commands.Context):
    def __init__(self, **attrs):
        super().__init__(**attrs)
        self._config = bot.GuildConfig.get_config(self.guild)

    async def multi_ban(self, *args):
        return await self._config.multi_ban(*args)

    async def multi_unban(self, *args):
        return await self._config.multi_unban(*args)

    async def multi_kick(self, *args):
        return await self._config.multi_kick(*args)

    async def multi_mute(self, *args):
        return await self._config.multi_mute(*args)

    async def multi_unmute(self, *args):
        return await self._config.multi_unmute(*args)

    async def set_config(self, **kwargs):
        return await self._config.set_config(**kwargs)

    def get_config(self):
        return self._config.get_config(self.guild)

    @property
    def logs(self):
        return self._config.logs

    @property
    def custom_prefix(self):
        return self._config.prefix

    @property
    def mute(self):
        return self._config.mute

    @property
    def config(self):
        return self._config


def _get_prefix(b, msg: discord.Message):
    if not msg.guild:
        return b.default_prefix
    if config := b.GuildConfig.get_config(msg.guild):
        return config.prefix
    return b.default_prefix


bot = CustomBot(case_insensitive=True, intents=intents, command_prefix=_get_prefix,
                activity=discord.Game(name='mod.help for help!'), strip_after_prefix=True)

if __name__ == '__main__':
    for file in os.listdir('./cogs'):
        if file.endswith('.py'):
            bot.load_extension(f'cogs.{file[:-3]}')

bot.run(bot.secrets['BOT_TOKEN'], bot=True, reconnect=True)
