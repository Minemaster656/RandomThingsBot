# импортируем необходимые библиотеки
import discord
from discord.ext import commands, tasks
import socket
import select


class PingCog(commands.Cog):
    # инициализируем cog
    def __init__(self, bot):
        self.bot = bot
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(("", 3002))
        self.s.listen()
        self.listen_ping.start()

    # создаем задачу для прослушивания пингов
    @tasks.loop(seconds=1)
    async def listen_ping(self):
        # проверяем, есть ли ожидающие соединения
        ready, _, _ = select.select([self.s], [], [], 0)
        # если есть, то принимаем их
        if ready:
            conn, addr = self.s.accept()
            data = conn.recv(1024)
            # отправляем ответ "pong"
            conn.send(b"pong")
            conn.close()

    def cog_unload(self):
        self.listen_ping.cancel()
        self.s.close()


def setup(bot):
    bot.add_cog(PingCog(bot))
