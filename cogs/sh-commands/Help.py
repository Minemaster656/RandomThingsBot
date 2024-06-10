class Help():
    command_name = "help"
    require_sudo = False
    require_whitelist = False
    def __init__(self):
        ...
    async def execute(self, channel):
        await channel.send("-")