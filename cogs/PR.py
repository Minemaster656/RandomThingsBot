import random
# import numpy as np
# import matplotlib.pyplot as plt
import discord
from discord.ext import commands
# import perlin_noise
from discord import Option
from random import *

import Data
from Data import cursor
from Data import conn

class Pr(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # cursor.execute("CREATE TABLE IF NOT EXISTS partners (serverid INTEGER, servername TEXT, ownerid INTEGER, link TEXT,text       TEXT,color      TEXT)")
        # conn.commit()


def setup(bot):
    bot.add_cog(Pr(bot))