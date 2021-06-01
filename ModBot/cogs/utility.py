from discord.ext import commands, menus
from discord.ext.commands import Greedy

from typing import Union
import discord
from custom_funcs import *
import time
from datetime import timedelta
import string
import inspect
from io import StringIO
import asyncio


class RecentJoinsMenu(menus.ListPageSource):
    async def format_page(self, menu, entries):
        index = menu.current_page + 1
        embed = embed_create(menu.ctx.author, title=f'Showing recent joins for {menu.ctx.guild} '
                                                    f'({index}/{self._max_pages}):')
        for member in entries:
            joined_at = member.joined_at.strftime("%A, %d %b %Y, %I:%M:%S %p UTC")
            created_at = member.created_at.strftime("%A, %d %b %Y, %I:%M:%S %p UTC")
            embed.add_field(name=f'{member}', value=f'ID: {member.id}\n'
                                                    f'Joined at: {joined_at}\n'
                                                    f'Created at: {created_at}', inline=False)
        return embed


class HoistersMenu(menus.ListPageSource):
    async def format_page(self, menu, entries):
        index = menu.current_page + 1
        embed = embed_create(menu.ctx.author, title=f'Showing potential hoisters for {menu.ctx.guild} '
                                                    f'({index}/{self._max_pages}):')

        for member in entries:
            embed.add_field(name=f'{member.display_name}', value=f'Username: {member} ({member.mention})\n'
                                                                 f'ID: {member.id}', inline=False)
        return embed


class HoistersIDMenu(menus.ListPageSource):
    async def format_page(self, menu, entries):
        return " ".join(map(str, entries))


class UtilityCog(commands.Cog, name="Utility Commands"):
    def __init__(self, bot):
        self.bot = bot
        print('UtilityCog init')

    @commands.command()
    async def user(self, ctx, *, user: Union[discord.Member, discord.User]):
        """Displays some information about an user, if they are in the server, then the join date is available."""

        embed = embed_create(ctx.author, title=f'Info for {user}:', description=user.mention)
        embed.set_thumbnail(url=user.avatar_url)

        embed.add_field(name='ID', value=f'{user.id}')
        embed.add_field(name='Bot?', value='Yes' if user.bot else 'No')

        embed.add_field(name='Creation Date',
                        value=user.created_at.strftime("%A, %d %b %Y, %I:%M:%S %p UTC"),
                        inline=False)

        if isinstance(user, discord.Member):
            embed.add_field(name='Server Join Date',
                            value=user.joined_at.strftime("%A, %d %b %Y, %I:%M:%S %p UTC"),
                            inline=False)

        await ctx.send(embed=embed)

    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(aliases=['recentusers', 'recent', 'newjoins', 'newusers', 'rj', 'joins'])
    async def recentjoins(self, ctx):
        async with ctx.channel.typing():
            members = sorted(ctx.guild.members, key=lambda m: m.joined_at, reverse=True)[:100]

            pages = CustomMenu(source=RecentJoinsMenu(members, per_page=5), clear_reactions_after=True)

        await pages.start(ctx)

        async with ctx.channel.typing():
            await self.bot.wait_for('finalize_menu', check=lambda c: c == ctx)

    @commands.max_concurrency(5, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(aliases=['bottest', 'selfbottest', 'bt', 'sbt'])
    async def selfbot(self, ctx, users: Greedy[discord.Member]):
        """Creates a fake Nitro giveaway to catch a selfbot (Automated user accounts which auto-react to giveaways)
        When someone reacts with to the message, The user and the time will be sent.
        You can specify users so that the bot will only respond to their reactions."""
        if users: users.append(ctx.author)
        message = await ctx.send("""
:tada: GIVEAWAY :tada: 

Prize: Nitro
Timeleft: Infinity
React with :tada: to participate!
        """)
        await message.add_reaction('\N{PARTY POPPER}')
        t = time.perf_counter()
        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=600,
                                                     check=lambda _reaction, _user: _reaction.message == message and (
                                                             not _user.bot and not users) or _user in users
                                                                                    and _reaction.emoji == '\N{PARTY POPPER}')
        except asyncio.TimeoutError:

            embed = embed_create(ctx.author, title='Test timed out!',
                                 description=f'No one reacted within 10 minutes!', color=discord.Color.red())
        else:
            if user == ctx.author:
                embed = embed_create(ctx.author, title='Test canceled!',
                                     description=f'You reacted to your own test, so it was canceled.\nAnyways, '
                                                 f'your time is {round(time.perf_counter() - t, 2)} seconds.',
                                     color=discord.Color.red())
            else:
                embed = embed_create(ctx.author, title='Reaction found!',
                                     description=f'{user} (ID: {user.id})\nreacted with {reaction} in '
                                                 f'{round(time.perf_counter() - t, 2)} seconds')
        try:
            await message.reply(embed=embed)
        except (discord.Forbidden, discord.NotFound, discord.HTTPException):
            await ctx.send(embed=embed)

    @commands.command(aliases=['invite', 'ping', 'code'])
    async def info(self, ctx):
        """Shows information for the bot, such as ping, the invite, owner info, and source code."""
        embed = embed_create(ctx.author, title="Info for Mini Mod",
                             description="This bot has commands useful for moderation!")
        embed.add_field(name="Invite this bot!", value=
        "[**Invite**](https://discord.com/oauth2/authorize?"
        "client_id=829104096324616192&permissions=402680006&scope=bot)",
                        inline=False)
        embed.add_field(name="Join support server!", value="[**Support Server**](https://discord.gg/Uk6fg39cWn)",
                        inline=False)
        embed.add_field(name='Bot Creator:',
                        value='[Doggie](https://github.com/DoggieLicc/)#1641',
                        inline=True)
        embed.add_field(name='Bot Code',
                        value='[Source Code](https://github.com/DoggieLicc/MiniMod)')
        embed.add_field(name='Bot Uptime:',
                        value=str(timedelta(seconds=round(time.time() - self.bot.start_time))), inline=False)
        embed.add_field(name='Ping:',
                        value='{} ms'.format(round(1000 * self.bot.latency), inline=False))
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.cooldown(5, 60)
    @commands.group(aliases=['hoist'], invoke_without_command=True)
    async def hoisters(self, ctx):
        """Shows a list of members who have names made to 'hoist' themselves to the top of the member list!"""
        ok_chars = list(string.ascii_letters + string.digits)
        members = sorted(ctx.guild.members, key=lambda m: m.display_name)[:200]

        hoisters: [discord.Member] = []

        for member in members:
            if member.display_name[0] in ok_chars:
                break
            hoisters.append(member)

        if not hoisters:
            embed = embed_create(ctx.author, title="No hoisters found!",
                                 description="There weren't any members with odd characters found!",
                                 color=discord.Color.red())
            return await ctx.send(embed=embed)

        pages = CustomMenu(source=HoistersMenu(hoisters, per_page=10), clear_reactions_after=True)

        await pages.start(ctx)

    @commands.guild_only()
    @hoisters.command(aliases=['ids'])
    async def id(self, ctx):
        """Like `hoisters`, but only shows the ids"""
        ok_chars = list(string.ascii_letters + string.digits)
        members = sorted(ctx.guild.members, key=lambda m: m.display_name)[:200]

        hoisters: [int] = []

        for member in members:
            if member.display_name[0] in ok_chars:
                break
            hoisters.append(member.id)

        if not hoisters:
            embed = embed_create(ctx.author, title="No hoisters found!",
                                 description="There weren't any members with odd characters found!",
                                 color=discord.Color.red())
            return await ctx.send(embed=embed)

        pages = CustomMenu(source=HoistersIDMenu(hoisters, per_page=100), clear_reactions_after=True)
        await pages.start(ctx)

    @commands.command()
    async def source(self, ctx, *, command: str = None):
        """Look at this shit code lol (usage: source <command>)"""
        if command is None:
            embed = embed_create(ctx.author, title='Source Code:',
                                 description='[Github for **MiniMod**](https://github.com/DoggieLicc/MiniMod)')
            return await ctx.send(embed=embed)

        if command == 'help':
            src = type(self.bot.help_command)
            filename = inspect.getsourcefile(src)
        else:
            obj = self.bot.get_command(command.replace('.', ' '))
            if obj is None:
                embed = embed_create(ctx.author, title='Command not found!',
                                     description='This command wasn\'t found in this bot.')
                return await ctx.send(embed=embed)

            src = obj.callback.__code__
            filename = src.co_filename

        lines, _ = inspect.getsourcelines(src)
        code = ''.join(lines)

        buffer = StringIO(code)

        file = discord.File(fp=buffer, filename=filename)

        await ctx.send(f"Here you go, {ctx.author.mention}. (You should view this on a PC)", file=file)

    @selfbot.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MaxConcurrencyReached):
            embed = embed_create(ctx.author, title=f'Error!', color=0xeb4034)
            embed.add_field(name='Too many tests running!',
                            value=f'You can only have {error.number} tests running at the same time!')
            await ctx.send(embed=embed)

    @recentjoins.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MaxConcurrencyReached):
            embed = embed_create(ctx.author, title=f'Error!', color=0xeb4034)
            embed.add_field(name='Menu already open!',
                            value=f'You can only have {error.number} menu running at once, '
                                  f'use the ⏹ or 🗑 buttons to close the current menu!')
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(UtilityCog(bot))
