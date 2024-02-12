import hashlib

import perlin_noise
# from PIL import Image, ImageOps
import random

import swearfilter

# import utils

# clrshiftSize = 2
# alpha = 0.2
# def genZone(sizes):
#     # x1, y1 = random.randint(0, sizes[0]), random.randint(1, sizes[1])
#     # x2, y2 = random.randint(0, sizes[0]), random.randint(1, sizes[1])
#     # if x2<x1 and y2<y1:
#     #     temp1, temp2 = x2, y2
#     #     x2,y2=x1,y1
#     #     x1,y1=temp1,temp2
#     x1 = random.randint(0, sizes[0])
#     y1 = random.randint(0, sizes[1])
#     x2 = random.randint(x1, sizes[0])
#     y2 = random.randint(y1, sizes[1])
#     if y2-y1 > sizes[1]/10:
#         t = random.randint(1,3)
#         y2 = int(y2/t)
#         if y2 < y1:
#             y2 = y1+random.randint(5,16)
#     return (x1, y1, x2, y2)
#
# def transperent(image):
#     image = image.convert("RGBA")
#     image_with_alpha = image.copy()
#
#     # Получение объекта изображения с альфа-каналом
#     pixels = image_with_alpha.convert("RGBA").load()
#     image_tr = Image.new("RGBA",image.size, (0,0,0,0))
#     # Изменение прозрачности пикселей
#     for y in range(image_with_alpha.size[1]):
#         for x in range(image_with_alpha.size[0]):
#             r, g, b, a = pixels[x, y]
#             # pixels[x, y] = (r, g, b, int(a * 0.5))  # Установка прозрачности (50%)
#             image_tr.putpixel((x, y),(r, g, b, int(a * alpha)))
#     return image_tr
#
# # Загрузка изображения
# image = Image.open("../image_buffer.png")
# sizes = image.size
# for i in range(random.randint(10,20)):
#     # Определение координат и размеров прямоугольника
#     # x1, y1 = random.randint(0,sizes[0]), random.randint(1,sizes[1])
#     # x2, y2 = random.randint(0,sizes[0]), random.randint(1,sizes[1])
#
#     # width = x2 - x1
#     # height = y2 - y1
#
#     box = genZone(sizes)
#     width = box[2]-box[0]
#     height = box[3]-box[1]
#
#     # Выбор случайных координат для сдвига
#     new_x = random.randint(0, image.width - width)
#     new_y = random.randint(0, image.height - height)
#
#     # Выделение и копирование прямоугольника
#     cropped = image.crop(box)
#     image.paste(cropped, box)
#     # Вставка скопированного прямоугольника на новые координаты
#     image.paste(cropped, (new_x, new_y))
#
#
#
# def genNoiseMap(seed, sizes):
#     noise1 = perlin_noise.PerlinNoise(octaves=1, seed=seed)
#     noise2 = perlin_noise.PerlinNoise(octaves=2, seed=seed)
#     noise3 = perlin_noise.PerlinNoise(octaves=3, seed=seed)
#     noise4 = perlin_noise.PerlinNoise(octaves=4, seed=seed)
#
#
#     image = Image.new("RGBA", sizes, (1, 1, 1, 1))
#     for x in range(sizes[0]):
#         for y in range(sizes[1]):
#             cVal = noise1([x*0.1, utils.invertY(y, sizes[1])*0.1])
#             cVal += noise2([x * 0.1, utils.invertY(y, sizes[1]) * 0.1])
#             cVal += noise3([x * 0.1, utils.invertY(y, sizes[1]) * 0.1])
#             cVal += noise4([x * 0.1, utils.invertY(y, sizes[1]) * 0.1])
#             image.putpixel((x, y), (int(cVal*255), int(cVal*255), int(cVal*255), 255))
#     image.save("perlin.png")
# genNoiseMap(100, (128, 128))
# noise = perlin_noise.PerlinNoise(octaves=1, seed=1000)
# print(hashlib.md5(input("Строка для md5:")))
# print(swearfilter.findSwear(input("СТРОКА ДЛЯ ПРОВЕРКИ")))
def parseTagInStart(text:str, tag:str)->tuple:
    '''
    FINDS TAG ONLY IN START!!!
    Returns: [0] - Tag | [1] - tag content | [2] - text without tag
    Example text:
    <$DRAW prompt /$>

    Example tag:
    DRAW'''
    tagSize=len(tag)
    gentag = ""
    prompt = ""
    text+= " "

    if text.startswith(f"<${tag}"):

        i = text.find("/$>")
        if i > 0:
            gentag = text[:(len(text) - (i + 3)) * -1]
            text = text[i + 3:]
            if len(gentag)>10:
                prompt = gentag[tagSize+2:-3]
                # prompt = prompt[:]
                if prompt.startswith(" "):
                    prompt = prompt[1:]
                if prompt.endswith(" "):
                    prompt = prompt[:-1]
                if text.startswith(" "):
                    text = text[1:]
                if text.endswith(" "):
                    text = text[:-1]


    return (gentag, prompt, text)
print(parseTagInStart("<$DRAW тааа /$> gfbfhvfbfvfv", "DRAW"))
print("DRAW" == "DRAW")