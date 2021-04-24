from discord.ext import commands, menus

from typing import Union
import discord
from custom_funcs import *


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
    async def user(self, ctx, user: Union[discord.Member, discord.User]):
        """Displays some information about an user, if they are in the server, then the join date is available."""

        embed = embed_create(ctx.author, title=f'Info for {user}:')
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

    @commands.command(aliases=['recentusers', 'recent', 'newjoins', 'newusers', 'rj'])
    async def recentjoins(self, ctx):
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at, reverse=True)[:25]

        pages = menus.MenuPages(source=RecentJoinsMenu(members, per_page=5), clear_reactions_after=True)
        pages.add_button(trash_button)
        await pages.start(ctx)


def setup(bot):
    bot.add_cog(UtilityCog(bot))
