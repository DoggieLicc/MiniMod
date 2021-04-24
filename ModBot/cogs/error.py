import discord.ext.commands as err

import discord
from custom_funcs import *


class ErrorCog(err.Cog):
    def __init__(self, bot):
        self.bot = bot
        print('ErrorCog init')

    @err.Cog.listener()
    async def on_command_error(self, ctx, error):
        embed = discord.Embed(title=f'Error!', color=0xeb4034)
        print(f'Error: {error}')
        if isinstance(error, err.errors.CommandNotFound):
            embed.add_field(name='Command not found!:',
                            value='You should use the ``help`` command for a list of commands!')
        elif isinstance(error, err.MissingRequiredArgument):
            embed.add_field(name='Missing Arguments:', value='Do ``help <command>`` to get more info for a command')
        elif isinstance(error, err.NoPrivateMessage):
            embed.add_field(name='No DMs!:', value='The bot can\'t access that from a DM, try from the server!')
        elif isinstance(error, err.errors.EmojiNotFound):
            embed.add_field(name='Emote not found!:', value='Use the emote directly or its ID!')
        elif isinstance(error, err.errors.RoleNotFound):
            embed.add_field(name='Role not found!:', value='Use the role\'s name, ID, or just mention it')
        elif isinstance(error, err.errors.BadInviteArgument):
            embed.add_field(name='Invite not found!:',
                            value='Use the invite URL, or its code (If you want the bot\'s invite link, use the '
                                  '``info`` command!)')
        elif isinstance(error, err.CheckAnyFailure):
            embed.add_field(name='You don\'t have permissions for this command!:',
                            value='You need the `Manage Server` permission!')
        elif isinstance(error, err.errors.NotOwner):
            return await ctx.send(
                content='https://cdn.discordapp.com/attachments/559455534965850142/821118783929974784/realopeneval.mp4')
        elif isinstance(error, err.CommandOnCooldown):
            embed.add_field(name='Cooldown!:', value=str(error))
        elif isinstance(error, discord.Forbidden):
            try:
                await ctx.send(f'This bot needs the ``Embed Links`` permission to function!')
            except discord.Forbidden:
                pass
        elif isinstance(error, CannotPunish):
            embed.add_field(name='Couldn\'t punish users!', value=f'The bot wasn\'t able to {error.punish} any users!')
            pass
        else:
            return print(f'Unresolved error, {error}')

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ErrorCog(bot))
