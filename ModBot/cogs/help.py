from discord.ext import commands

from custom_funcs import *


class HelpCog(commands.Cog):
    def __init__(self, _bot):
        self.bot = _bot
        help_attributes = {
            'help': 'Displays help for the bot\'s commands... duh',
            'hidden': True,
            'aliases': ['h', 'command', 'commands', 'cmd', 'cmds']
        }
        help_obj = MyHelp(command_attrs=help_attributes, verify_checks=False)
        _bot.help_command = help_obj
        print('HelpCog init')


class MyHelp(commands.HelpCommand):
    def get_command_signature(self, command):
        return '%s %s' % (command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        embed = embed_create(self.context.author, title='Help:',
                             description=f'The current prefixes are '
                                         f'`{self.context.bot._get_prefix(self.context.bot, self.context.message)[0]}` '
                                         f'and {self.context.bot.user.mention}\n\n'
                                         f'`{self.clean_prefix}help [command]` for command info\n'
                                         f'`<arg>` - Required argument\n'
                                         f'`[arg]` - Optional argument\n'
                                         f'`[arg=10]` - Optional argument, `10` is default\n'
                                         f'`<users>...` - You can specify multiple users')
        for cog, command in mapping.items():
            _filtered = []
            for c in command:
                _filtered.append(c)
                if isinstance(c, commands.Group):
                    [_filtered.append(subc) for subc in c.commands]

            filtered = await self.filter_commands(_filtered, sort=True)
            command_signatures = [self.get_command_signature(c) for c in filtered]
            if command_signatures:
                cog_name = getattr(cog, 'qualified_name', 'Other')
                embed.add_field(name=cog_name, value='\n'.join(command_signatures), inline=False)

        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = embed_create(self.context.author, title=self.get_command_signature(command))
        embed.add_field(name='Command Help:', value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(name='Aliases', value=', '.join(alias), inline=False)

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_group_help(self, group):
        embed = embed_create(self.context.author, title=self.get_command_signature(group))
        embed.add_field(name='Help:', value=f'{group.short_doc}\n', inline=False)
        embed.add_field(name='Subcommand Help:', value='᲼', inline=False)
        for command in group.commands:
            embed.add_field(name=self.get_command_signature(command), value=command.help, inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_error_message(self, error):
        embed = embed_create(self.context.author, title='Help command error!', description=error, color=0xeb4034)
        channel = self.get_destination()
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(HelpCog(bot))
