import discord.ext.commands as err

import discord
import traceback
from custom_funcs import *


class ErrorCog(err.Cog):
    def __init__(self, bot):
        self.bot = bot
        print('ErrorCog init')

    @err.Cog.listener()
    async def on_command_error(self, ctx, error):
        embed = embed_create(ctx.author, title=f'Error!', color=0xeb4034)
        if isinstance(error, err.errors.CommandNotFound):
            embed.add_field(name='Command not found!:',
                            value='You should use the ``help`` command for a list of commands!')
        elif isinstance(error, err.MissingRequiredArgument):
            embed.add_field(name='Missing Arguments:', value='Do ``help <command>`` to get more info for a command')
        elif isinstance(error, err.NoPrivateMessage):
            embed.add_field(name='No DMs!:', value='You can\'t use this command in DMS!')
        elif isinstance(error, err.CheckAnyFailure):
            embed.add_field(name='You don\'t have permissions for this command!:',
                            value='You need the `Manage Messages` permission!')
        elif isinstance(error, err.errors.NotOwner):
            return await ctx.send(
                content='no')
        elif isinstance(error, err.CommandOnCooldown):
            embed.add_field(name='Cooldown!:', value=str(error))
        elif isinstance(error, CannotPunish):
            embed.add_field(name='Couldn\'t punish users!', value=f'The bot wasn\'t able to {error.punish} any users!\n'
                                                                  f'Maybe their role is higher than yours. or higher '
                                                                  f'than this bot\'s roles')
        elif isinstance(error, err.BotMissingPermissions):
            embed.add_field(name='Bot is missing permissions!',
                            value=f'The bot needs `' +
                                  ', '.join([str(e).capitalize().replace('_', ' ') for e in error.missing_perms]) +
                                  '` to use this command!!')
        elif isinstance(error, err.MissingPermissions):
            embed.add_field(name='You are missing permissions!',
                            value=f'You need `' +
                                  ', '.join([str(e).capitalize().replace('_', ' ') for e in error.missing_perms]) +
                                  '` to use this command!')
        elif isinstance(error, err.errors.MaxConcurrencyReached):
            return
        else:
            owner = self.bot.get_user(203161760297910273)
            embed = discord.Embed(title="Unhandled Error!",
                                  description=f"```py\n{traceback.format_tb(error.__traceback__)[0].strip()}\n```")
            embed.add_field(name="Error:", value=f"{error.original.__class__.__name__}: "
                                                 f"{error.original}", inline=False)
            embed.add_field(name="Message content:", value=ctx.message.content, inline=False)
            embed.add_field(name="Extra Info:", value=f"Guild: {ctx.guild}: {ctx.guild.id if ctx.guild else 'None'}\n"
                                                      f"Channel: {ctx.channel}:", inline=False)
            return await owner.send(embed=embed)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ErrorCog(bot))
