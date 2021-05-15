from discord.ext import commands, menus
from discord.ext.commands import Greedy

from typing import Union
import discord
from custom_funcs import *
import time
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
