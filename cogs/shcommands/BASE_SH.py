class BASE_SH():
    command_name = "EXECUTE_BASE_SH"
    require_sudo = True
    require_whitelist = False

    def __init__(self):
        ...
    async def execute(self, channel):
        await channel.send("А вот это выводить не надо.")