import random
import numpy as np
import matplotlib.pyplot as plt

try:
    import discord
    from discord import Option, Webhook, Forbidden
    from discord.ext import commands
except:
    import pycord as discord
    from pycord import Option, Webhook, Forbidden
    from discord.ext import commands

import perlin_noise
from random import *


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.slash_command(name="сгенерировать-карту",description="Генерирует мир")
    # async def genmap(self, ctx, x : Option(float, description="Координата x",required=True), y : Option(float, description="Координата x",required=True),
    #                  seed : Option(float, description="Сид",required=True),octaves : Option(float, description="Октавы",required=True),iterations : Option(int, description="Итерации добавления для отладки",required=True),add : Option(float, description="Добавление за итерацию для отладки",required=True),):
    #     async with ctx.typing():
    #         noise = perlin_noise.PerlinNoise(octaves=octaves, seed=seed)
    #         x-=0.0001
    #         y-=0.0001
    #         # buffer = ""
    #         # for i in range(5):
    #         #     for j in range(5):
    #         #         a = noise(i, j)
    #         #         if (a<)
    #
    #         await ctx.respond(f"Значение шума на {x} {y} с сидом {seed} и октавой {octaves}: {str(noise([x, y]))}")
    #         await ctx.send(f"Так же {iterations} выводов шума с + {add} к каждой координате за вызов: ")
    #         o = ""
    #         for i in range(iterations):
    #             o+=f"{i} "+str(noise([x+add*iterations, y+add*iterations]))
    #         await ctx.send(o)

    @commands.slash_command(name="сгенерировать-карту", description="Генерирует мир")
    async def genmap(self, ctx, size: Option(int, description="Размер", required=True),
                     rd: Option(int, description="Дистанция прорисовки", required=True),
                     cx: Option(int, description="Позиция камеры по x", required=True),
                     cy: Option(int, description="Позиция камеры по y", required=True),
                     seed: Option(float, description="Сид. Оставьте пустым для случайного.", required=False) = None,
                     scale: Option(float, description="Умножение результата шума", required=False) = 2.0,
                     octaves: Option(float, description="Октавы шума", required=False) = 1):

        octaves = octaves

        shift = 0.2
        async with ctx.typing():
            if seed == None:
                seed = randint(0, 100000)

            noise = perlin_noise.PerlinNoise(octaves=octaves, seed=seed)
            noises = {"height": perlin_noise.PerlinNoise(octaves=octaves, seed=seed + 1000),
                      "humidity": perlin_noise.PerlinNoise(octaves=octaves, seed=seed + 5000),
                      "temperature": perlin_noise.PerlinNoise(octaves=octaves, seed=seed + 9000)}

            def fill_array(size):

                array_hgh = np.empty(size, dtype=object)
                array_hum = np.empty(size, dtype=object)
                array_tmp = np.empty(size, dtype=object)
                for i in range(size[0]):
                    for j in range(size[1]):
                        array_hgh[i, j] = gen_cell(j, i, "height")
                        array_hum[i, j] = gen_cell(j, i, "humidity")
                        array_tmp[i, j] = gen_cell(j, i, "temperature")

                return (array_hgh, array_hum, array_tmp)

            def gen_cell(x, y, noise):
                # Здесь можно добавить логику для генерации значения ячейки
                # return noise([x*shift, y*shift])
                return noises[noise]([x, y])

            def print_array_with_emoji(array0, array1, array2):
                # temp_array = np.copy(array)
                # temp_array[temp_array < 0.5] = '⬛'
                # temp_array[temp_array >= 0.5] = '⬜'
                out = ""
                for i in range(array0.shape[0]):
                    for j in range(array0.shape[1]):
                        output_hgh = False
                        output_hum = False
                        output_tmp = False
                        if array0[i, j] * scale <= 0:  # abs(array[i, j])*scale<0.5:
                            out += "⬛"
                        else:
                            out += "⬜"
                        # if array0[i, j]*scale<=0:#abs(array[i, j])*scale<0.5:
                        #     output_hgh=True
                        # else:
                        #     output_hgh = False
                        #
                        # if array1[i, j]*scale<=0:#abs(array[i, j])*scale<0.5:
                        #     ...
                        # else:
                        #     output_hum=True
                        #
                        # if array2[i, j]*scale<=0:#abs(array[i, j])*scale<0.5:
                        #     ...
                        # else:
                        #     output_tmp=True
                        #
                        # if not output_hgh:
                        #     out+= "🪨"
                        # else:
                        #     if output_hum==True and output_tmp==True:
                        #         out+="🌴"
                        #     elif output_hum==True and output_tmp==False:
                        #         out+="❄️"
                        #     elif output_hum==False and output_tmp==True:
                        #         out+="🏜️"
                        #     #elif output_hum==False and output_tmp==False:
                        #     else:
                        #         out+="🧊"

                        # abs(array[i, j])*100

                    out += "\n"

                return (out)

            arrays = fill_array((size, size))
            arr0 = arrays[0]
            arr1 = arrays[1]
            arr2 = arrays[2]
            await ctx.respond(print_array_with_emoji(arr0, arr1, arr2))


def setup(bot):
    bot.add_cog(Game(bot))
