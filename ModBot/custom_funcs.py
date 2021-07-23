import datetime
from typing import Optional, Literal

import discord
import re
from discord.ext import commands, menus

__all__ = [
    "CannotPunish",
    "embed_create",
    "TimeConverter",
    "IntentionalUser",
    "IntentionalMember",
    "CustomMenu",
    "user_friendly_dt"
]


class CannotPunish(commands.CommandError):
    def __init__(self, punishment: str, users: [discord.Member, discord.User], mod: discord.Member):
        self.punish = punishment
        self.users = users
        self.ctx = mod


def embed_create(user, **kwargs):
    color = kwargs.get('color', 0x46ff2e)
    title = kwargs.get('title', discord.embeds.EmptyEmbed)
    url = kwargs.get('url', discord.embeds.EmptyEmbed)
    description = kwargs.get('description', discord.embeds.EmptyEmbed)

    embed = discord.Embed(description=description, title=title, color=color, url=url)
    embed.set_footer(
        text=f'Command sent by {user}',
        icon_url=user.avatar_url,
    )
    return embed


class Time(object):

    def __init__(self, unit_name, unit_time, amount_units, total_seconds):
        self.unit_name = unit_name
        self.unit_time = unit_time
        self.amount_units = amount_units
        self.total_seconds = total_seconds


class TimeConverter(commands.Converter):

    @staticmethod
    def unit_getter(unit):
        if unit in ["s", "sec", "secs", "second", "seconds"]:
            return 1, "second"
        if unit in ["m", "min", "mins", "minute", "minutes"]:
            return 60, "minute"
        if unit in ["h", "hr", "hrs", "hour", "hours"]:
            return 3600, "hour"
        if unit in ["d", "day", "days"]:
            return 86_000, "day"
        if unit in ["w", "wk", "wks", "week", "weeks"]:
            return 604_800, "week"
        if unit in ["mth", "mths", "mos", "month", "months"]:
            return 2_580_000, "month"
        if unit in ["y", "yr", "yrs", "year", "years"]:
            return 31_390_000, "month"
        else:
            return None, None

    async def convert(self, ctx, argument):
        reg = re.compile("([0-9]+)([a-zA-Z]+)")
        time, unit = reg.match(argument).groups()
        unit_time, unit_name = self.unit_getter(unit.lower())
        seconds = unit_time * time
        return Time(unit_name, unit_time, time, seconds)


class IntentionalMember(commands.converter.MemberConverter):
    async def query_member_named(self, guild, argument):
        cache = guild._state.member_cache_flags.joined
        if len(argument) > 5 and argument[-5] == '#':
            username, _, discriminator = argument.rpartition('#')
            members = await guild.query_members(username, limit=100, cache=cache)
            return discord.utils.get(members, name=username, discriminator=discriminator)
        else:
            return None

    async def convert(self, ctx, argument: str) -> discord.Member:
        bot = ctx.bot
        match = self._get_id_match(argument) or re.match(r'<@!?([0-9]{15,20})>$', argument)
        guild = ctx.guild
        user_id = None
        if match is None:
            # not a mention...
            if guild:
                result = await self.query_member_named(guild, argument)
            else:
                result = commands.converter._get_from_guilds(bot, 'get_member_named', argument)
        else:
            user_id = int(match.group(1))
            if guild:
                result = guild.get_member(user_id) or discord.utils.get(ctx.message.mentions, id=user_id)
            else:
                result = commands.converter._get_from_guilds(bot, 'get_member', user_id)

        if result is None:
            if guild is None:
                raise commands.errors.MemberNotFound(argument)

            if user_id is not None:
                result = await self.query_member_by_id(bot, guild, user_id)
            else:
                result = await self.query_member_named(guild, argument)

            if not result:
                raise commands.errors.MemberNotFound(argument)

        return result


class IntentionalUser(commands.converter.UserConverter):
    async def convert(self, ctx: commands.Context, argument: str) -> discord.User:
        match = self._get_id_match(argument) or re.match(r'<@!?([0-9]{15,20})>$', argument)
        state = ctx._state

        if match is not None:
            user_id = int(match.group(1))
            result = ctx.bot.get_user(user_id) or discord.utils.get(ctx.message.mentions, id=user_id)
            if result is None:
                try:
                    result = await ctx.bot.fetch_user(user_id)
                except discord.HTTPException:
                    raise commands.errors.UserNotFound(argument) from None

            return result

        arg = argument

        # Remove the '@' character if this is the first character from the argument
        if arg[0] == '@':
            # Remove first character
            arg = arg[1:]

        # check for discriminator if it exists,
        if len(arg) > 5 and arg[-5] == '#':
            discrim = arg[-4:]
            name = arg[:-5]
            predicate = lambda u: u.name == name and u.discriminator == discrim
            result = discord.utils.find(predicate, state._users.values())
            if result is not None:
                return result

        raise commands.errors.UserNotFound(argument)


class CustomMenu(menus.MenuPages):
    @menus.button('\N{WASTEBASKET}\ufe0f', position=menus.Last(3))
    async def do_trash(self, _):
        self.stop()
        await self.message.delete()

    def stop(self):
        self.call_end_event()
        super().stop()

    async def finalize(self, timed_out):
        self.call_end_event()

    def call_end_event(self):
        self.bot.dispatch('finalize_menu', self.ctx)


TimestampStyle = Literal['f', 'F', 'd', 'D', 't', 'T', 'R']


def format_dt(dt: datetime.datetime, /, style: Optional[TimestampStyle] = None) -> str:
    if style is None: return f'<t:{int(dt.timestamp())}>'
    return f'<t:{int(dt.timestamp())}:{style}>'


def user_friendly_dt(dt: datetime.datetime):
    return format_dt(dt, style='f') + f' ({format_dt(dt, style="R")})'
