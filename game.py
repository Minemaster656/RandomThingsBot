import random
import numpy as np
import matplotlib.pyplot as plt
import discord
from discord.ext import commands

class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
