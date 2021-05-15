from discord.ext import commands, menus
from discord.ext.commands import Greedy

from typing import Union, Optional
import discord
from custom_funcs import *


async def maybe_first_snipe_msg(ctx, channel):
    embed = embed_create(ctx.author, title='⚠ Warning!',
                         description='That channel seems to be locked, and this channel'
                         ' isn\'t. You should move to a private channel to avoid leaking sensitive information. '
                         'However, you have permissions to snipe from that channel, so you may proceed with caution.',
                         color=discord.Color.orange())
    return await channel.send(embed=embed)


class SnipeMenu(menus.ListPageSource):
    def __init__(self, entries):
        super().__init__(entries, per_page=1)

    async def format_page(self, menu, entries):
        index = menu.current_page + 1
        message = entries
        embed = embed_create(menu.ctx.author, title=f'Sniped message {index}/{self._max_pages}:',
                             description=f'{message.content}')
        embed.set_author(name=f'{message.author}: {message.author.id}', icon_url=message.author.avatar_url)

        if message.attachments:
            if message.attachments[0].filename.endswith(('png', 'jpg', 'jpeg', 'gif', 'webp')):
                embed.set_image(url=message.attachments[0].proxy_url)

            file_urls = [f'[{file.filename}]({file.proxy_url})' for file in message.attachments]
            embed.add_field(name='Deleted files:', value=f'\n'.join(file_urls))

        embed.add_field(name=f'Message created at:', value=message.created_at.strftime('%A, %d %b %Y, %I:%M:%S %p UTC'),
                        inline=False)
        embed.add_field(name='Message channel:', value=message.channel.mention, inline=False)
        return embed


class ModCog(commands.Cog, name="Moderator Commands"):
    def __init__(self, bot):
        self.bot = bot
        print('ModCog init')

    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.command(usage='<users>... [reason]')
    async def ban(self, ctx, users: Greedy[Union[IntentionalMember, IntentionalUser]], *, reason: Optional[str]):
        """Ban members who broke the rules! You can specify multiple members in one command
        ,You can also ban users not in the guild using their ID!, You and this bot needs the "Ban Members" permission.
        """
        if not users:
            embed = embed_create(ctx.author, title='Users not found!',
                                 description='Either no users were specified, or they weren\'t found.\n'
                                             'Use their mention, name#tag, or ID.', color=discord.Color.red())
            return await ctx.send(embed=embed)

        async with ctx.channel.typing():

            banned, not_banned = await ctx.multi_ban(ctx.author, users, reason)

            color = 0x46ff2e if not not_banned else 0xf9ff4d

            embed = embed_create(ctx.author, title=f'{len(banned)} user{"s" if len(banned) != 1 else ""} banned!'
                                                   f"{' (Some users couldn’t be banned!)' if not_banned else ''}",
                                 color=color)
            embed.add_field(name=f'Banned user{"s" if len(banned) != 1 else ""}:', value=', '.join(map(str, banned)))
            if not_banned:
                embed.add_field(name=f'User{"s" if len(not_banned) != 1 else ""} not banned:',
                                value=', '.join(map(str, not_banned)))
            embed.add_field(name='Reason:', value=reason or "No reason specified", inline=False)

        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.command(usage='<users>... [reason]')
    async def unban(self, ctx, users: Greedy[IntentionalUser], *, reason: Optional[str]):
        """Unban banned users with their User ID, you can specify multiple people to be unbanned.
        You and this bot need the "Ban Members" permission!
        """
        if not users:
            embed = embed_create(ctx.author, title='Users not found!',
                                 description='Either no users were specified, or they weren\'t found.\n'
                                             'Use their mention or ID.', color=discord.Color.red())
            return await ctx.send(embed=embed)

        async with ctx.channel.typing():

            unbanned, not_unbanned = await ctx.multi_unban(ctx.author, users, reason)

            color = 0x46ff2e if not not_unbanned else 0xf9ff4d

            embed = embed_create(ctx.author, title=f'{len(unbanned)} user{"s" if len(unbanned) != 1 else ""} unbanned!'
                                                   f"{' (Some users couldn’t be unbanned!)' if not_unbanned else ''}",
                                 color=color)
            embed.add_field(name=f'Unbanned user{"s" if len(unbanned) != 1 else ""}:', value=', '.join(map(str, unbanned)))
            if not_unbanned:
                embed.add_field(name=f'User{"s" if len(not_unbanned) != 1 else ""} not unbanned:',
                                value=', '.join(map(str, not_unbanned)))
            embed.add_field(name='Reason:', value=reason or "No reason specified", inline=False)

        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    @commands.command(usage='<users>... [reason]')
    async def softban(self, ctx, users: Greedy[IntentionalMember], *, reason: Optional[str]):
        """Bans then unbans the specified users, which deletes their recent messages and 'kicks' them.
        You and this bot needs the "Ban Members" permission!"""
        reason = reason or "No reason specified"
        if not users:
            embed = embed_create(ctx.author, title='Users not found!',
                                 description='Either no users were specified, or they weren\'t found.\n'
                                             'Use their mention, name#tag, or ID.', color=discord.Color.red())
            return await ctx.send(embed=embed)

        async with ctx.channel.typing():

            banned, not_banned = await ctx.multi_ban(ctx.author, users, f'Softban: {reason}')
            unbanned, not_unbanned = await ctx.multi_unban(ctx.author, banned, f'Softban: {reason}')

            color = 0x46ff2e if not unbanned else 0xf9ff4d

            embed = embed_create(ctx.author, title=f'{len(unbanned)} user{"s" if len(unbanned) != 1 else ""} softbanned!'
                                                   f"{' (Some users couldn’t be softbanned!)' if not_unbanned else ''}",
                                 color=color)
            embed.add_field(name=f'Softbanned user{"s" if len(unbanned) != 1 else ""}:',
                            value=', '.join(map(str, unbanned)))
            if not_banned:
                embed.add_field(name=f'User{"s" if len(not_banned) != 1 else ""} not softbanned:',
                                value=', '.join(map(str, not_banned)))
            embed.add_field(name='Reason:', value=reason, inline=False)

        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    @commands.command(usage='<users>... [reason]')
    async def kick(self, ctx, users: Greedy[IntentionalMember], *, reason: Optional[str]):
        """Kick members who broke the rules! You can specify multiple members in one command.
        You and this bot needs the "Kick Members" permission!
        """
        if not users:
            embed = embed_create(ctx.author, title='Users not found!',
                                 description='Either no users were specified, or they weren\'t found.\n'
                                             'Use their mention, name#tag, or ID.', color=discord.Color.red())
            return await ctx.send(embed=embed)

        async with ctx.channel.typing():

            kicked, not_kicked = await ctx.multi_kick(ctx.author, users, reason)

            color = 0x46ff2e if not not_kicked else 0xf9ff4d

            embed = embed_create(ctx.author, title=f'{len(kicked)} user{"s" if len(kicked) != 1 else ""} kicked!'
                                                   f"{' (Some users couldn’t be kicked!)' if not_kicked else ''}",
                                 color=color)
            embed.add_field(name=f'Kicked user{"s" if len(kicked) != 1 else ""}:', value=', '.join(map(str, kicked)))
            if not_kicked:
                embed.add_field(name=f'User{"s" if len(kicked) != 1 else ""} not kicked:',
                                value=', '.join(map(str, not_kicked)))
            embed.add_field(name='Reason:', value=reason or "No reason specified", inline=False)

        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.command(aliases=['clear'])
    async def purge(self, ctx, users: Greedy[Union[IntentionalMember, IntentionalUser]], amount=20):
        """Deletes multiple messages from the current channel, you can specify users that it will delete messages from.
        You can also specify the amount of messages to check. You and this bot needs the "Manage Messages" permission"""

        async with ctx.channel.typing():

            def check(message):
                if (not users) or (message.author in users):
                    return True
                else:
                    return False

            messages_deleted = await ctx.channel.purge(limit=amount, check=check)

            users = [user.mention for user in users] if users else ['anyone']
            embed = embed_create(ctx.author, title=f'{len(messages_deleted)} messages deleted!',
                                 description='Deleted messages from ' + ', '.join(users))
        await ctx.send(embed=embed, delete_after=10)

        log_em = discord.Embed(title='Messages purged', description=f'{len(messages_deleted)} messages deleted from ' +
                                                                    ', '.join(users) + f' in {ctx.channel.mention}',
                               color=discord.Color.red())
        log_em.add_field(name='Moderator:', value=ctx.author.mention)
        await ctx.log(log_em)

    @commands.max_concurrency(1, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(aliases=['snpied', 'deleted'])
    async def snipe(self, ctx, channel: Optional[discord.TextChannel], *, user: Optional[discord.User]):
        """Shows recent deleted messages! You can specify an user to get deleted messages from. You can also specify a
        channel to get messages from, if no channel is specified it will get messages from the current channel.
        You can only snipe messages from channels in which you have `Manage Messages` and `View Channel` in."""

        async with ctx.channel.typing():

            channel = channel or ctx.channel

            if not ((channel.permissions_for(ctx.author).manage_messages and
                    channel.permissions_for(ctx.author).view_channel) or ctx.author.id == 203161760297910273):
                embed = embed_create(ctx.author, title='Can\'t snipe from that channel!',
                                     description='You need permissions to view and manage messages of that channel '
                                                 'before you can snipe messages from it!', color=discord.Color.red())
                return await ctx.send(embed=embed)

            filtered = [message for message in self.bot.sniped if (message.guild == ctx.guild)
                        and (user is None or user == message.author) and (channel == message.channel)][:100]

            if not filtered:
                embed = embed_create(ctx.author, title='No messages found!',
                                     description=f'No sniped messages were found for {user or "this guild"}'
                                                 f'{f" in {channel.mention}" or ""}', color=discord.Color.red())
                return await ctx.send(embed=embed)

        pages = CustomMenu(source=SnipeMenu(filtered), clear_reactions_after=True)
        if (channel.overwrites_for(ctx.guild.default_role).view_channel == False and
                ctx.channel.overwrites_for(ctx.guild.default_role).view_channel != False):
            pages.send_initial_message = maybe_first_snipe_msg
        await pages.start(ctx)
        await self.bot.wait_for('finalize_menu', check=lambda c: c == ctx)

    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    @commands.command(usage='<users>... [reason]')
    async def mute(self, ctx, users: Greedy[IntentionalMember], *, reason: Optional[str]):
        if not users:
            raise discord.ext.commands.MissingRequiredArgument(ctx.author)
        if not ctx.mute:
            embed = embed_create(ctx.author, title='Mute role not set!',
                                 description='A mute role hasn\'t been set for this guild, use command ``config '
                                             'mute_role <role>`` to set a mute role!', color=discord.Color.red())
            return await ctx.send(embed=embed)
        muted, not_muted = await ctx.multi_mute(ctx.author, users, reason)
        color = discord.Color.green() if not not_muted else discord.Color.orange()

        embed = embed_create(ctx.author, title=f'{len(muted)} user{"s" if len(muted) != 1 else ""} muted!'
                                               f"{' (Some users couldn’t be muted!)' if not_muted else ''}",
                             color=color)
        embed.add_field(name=f'Muted user{"s" if len(muted) != 1 else ""}:', value=', '.join(map(str, muted)))
        if not_muted:
            embed.add_field(name=f'User{"s" if len(muted) != 1 else ""} not muted:',
                            value=', '.join(map(str, not_muted)))
        embed.add_field(name='Reason:', value=reason or "No reason specified", inline=False)

        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    @commands.command(usage='<users>... [reason]')
    async def unmute(self, ctx, users: Greedy[IntentionalMember], *, reason: Optional[str]):
        if not users:
            raise discord.ext.commands.MissingRequiredArgument(ctx.author)
        if not ctx.mute:
            embed = embed_create(ctx.author, title='Mute role not set!',
                                 description='A mute role hasn\'t been set for this guild, use command ``config '
                                             'mute_role <role>`` to set a mute role!', color=discord.Color.red())
            return await ctx.send(embed=embed)
        unmuted, not_unmuted = await ctx.multi_unmute(ctx.author, users, reason)
        color = discord.Color.green() if not not_unmuted else discord.Color.orange()

        embed = embed_create(ctx.author, title=f'{len(unmuted)} user{"s" if len(unmuted) != 1 else ""} unmuted!'
                                               f"{' (Some users couldn’t be unmuted!)' if not_unmuted else ''}",
                             color=color)
        embed.add_field(name=f'unmuted user{"s" if len(unmuted) != 1 else ""}:', value=', '.join(map(str, unmuted)))
        if not_unmuted:
            embed.add_field(name=f'User{"s" if len(unmuted) != 1 else ""} not unmuted:',
                            value=', '.join(map(str, not_unmuted)))
        embed.add_field(name='Reason:', value=reason or "No reason specified", inline=False)

        await ctx.send(embed=embed)

    @snipe.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MaxConcurrencyReached):
            embed = embed_create(ctx.author, title=f'Error!', color=0xeb4034)
            embed.add_field(name='Snipe menu already open!',
                            value=f'You can only have {error.number} snipe menu running at once, '
                                  f'use the ⏹ or 🗑 buttons to close the current menu!')
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ModCog(bot))
