from discord.ext import commands

import discord
from custom_funcs import *

message_on = """Deleted messages can be quickly retrieved with the ``snipe`` command!"""
message_off = """Deleted messages will no longer be available with the ``snipe`` command!"""


class ConfigCog(commands.Cog, name='Configuration Commands'):
    def __init__(self, bot):
        self.bot = bot
        print('ConfigCog init')

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def config(self, ctx):
        pass

    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @config.command()
    async def prefix(self, ctx, *, prefix):
        """Sets a custom prefix for the current server!"""
        if len(prefix) > 100:
            return
        await ctx.set_config(prefix=prefix)

        embed = embed_create(ctx.author, title="Prefix set!",
                             description=f"Prefix ``{prefix}`` has been set for {ctx.guild}!\n"
                                         f"You now use this prefix to use this bot's commands")
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @config.command()
    async def log_channel(self, ctx, channel: discord.TextChannel):
        """Sets the log channel that the bot will use to log mod events like bans and and kicks"""
        await ctx.set_config(logs=channel)
        embed = embed_create(ctx.author, title="Log channel set!",
                             description=f"Channel {channel.mention} has been set for {ctx.guild}!\n"
                                         f"Logs will be sent to that channel!")
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @config.command()
    async def mute_role(self, ctx, role: discord.Role):
        await ctx.set_config(mute=role)
        embed = embed_create(ctx.author, title="Mute role set!",
                             description=f"Mute role has been set to {role.mention} for {ctx.guild}!\n"
                                         f"This role will be added to members when the ``mute`` command is used!")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ConfigCog(bot))
