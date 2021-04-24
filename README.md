# Mini Mod
Moderation bot with easy to use commands, but still quite useful for any server. To see a list of commands, use `mod.help`

## Moderation Commands
***Note:** In order to prevent accidental punishments, most of these commands require either the mention, ID, or full tag of users to specify to be punished, so nicknames wont work. You also won't be able to punish users with a higher role than you, or if they have a higher role than the bot*

### ban <users> [reason]
This command will ban the users specified. If a reason is given, it will show up on the audit log. You can ban users not in the server with their User ID. Multiple users are able to be specified.

***Note:** You need the `Ban Members` permission in order to use this command*

### kick <members> [reason]
This command will kick the members specified. If a reason is given, it will show up on the audit log. Multiple members are able to be specified.

***Note:** You need the `Kick Members` permission in order to use this command*

### softban <members> [reason]
This command will "softban" the members specified. This bans then unbans the user, serving as a kick but with their messages deleted. If a reason is given, it will show up on the audit log. Multiple members are able to be specified.

***Note:** You need the `Ban Members` permission in order to use this command*

### unban <users> [reason]
This command will unban the banned users specified. If a reason is given, it will show up on the audit log. Multiple members are able to be specified.

***Note:** You need the `Ban Members` permission in order to use this command*

### purge [users] [amount]
This command will mass delete messages. If users are specified, only their messages will be deleted. Note that the amount is the number of messages checked, not the amount that will be deleted. The default amount is 20 messages.

***Note:** You need the `Manage Messages` permission in order to use this command*

### snipe [user]
This command will show deleted messages. If an user is specified, it will only show messages from them. Note that messages are only stored in cache, so they wont last forever.

***Note:** You need the `Manage Messages` permission in order to use this command, because deleted messages may have private info*

### mute <members> [reason]
This command will mute the members specified. If a reason is given, it will show up on the audit log. Multiple members are able to be specified. Note that the mute role needs to be set first before using this command.

***Note:** You need the `Manage Roles` permission in order to use this command*

### unmute <members> [reason]
This command will unmute the members specified. If a reason is given, it will show up on the audit log. Multiple members are able to be specified. Note that the mute role needs to be set first before using this command.

***Note:** You need the `Manage Roles` permission in order to use this command*

## Utility Commands
These commands are able to be used by anyone
### user <user>
Displays some information about the user specified, like their creation date, and the date they joined the server.

### recentjoins
Displays the members who recently joined the server, and when they joined and created their accounts.
## Configuration Commands
You need the `Manage Server` permission to use these commands

### config log_channel <channel>
Sets the log channel for the bot to send moderator actions to, such as bans and kicks.

### config mute_role <role>
Sets the role that the bot will give to users with the `mute` command
### config prefix <prefix>
Sets the prefix that will be used when using the bots, instead of `.mod`. You can ping the bot to show the current prefix
