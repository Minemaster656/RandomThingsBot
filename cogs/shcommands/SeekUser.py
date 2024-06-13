class SeekUser():
    command_name = "seekuser"
    require_sudo = True
    require_whitelist = False

    def __init__(self):
        ...
    async def execute(self, channel, agrs, argflags, flags):

        await channel.send("А вот это выводить не надо.")