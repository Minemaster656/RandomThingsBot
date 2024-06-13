class Help():
    command_name = "help"
    require_sudo = False
    require_whitelist = False
    def __init__(self):
        ...
    async def execute(self, channel, agrs, argflags, flags):
        await channel.send("RTB SH:\n"
                           "command_name = help\n"
                           "require_sudo = False\n"
                           "require_whitelist = False\n"
                           "\n"
                           "Учитесь пользоваться сами, помощи не будет.")