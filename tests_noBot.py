from PIL import Image, ImageOps
import random

clrshiftSize = 2
alpha = 0.2
def genZone(sizes):
    # x1, y1 = random.randint(0, sizes[0]), random.randint(1, sizes[1])
    # x2, y2 = random.randint(0, sizes[0]), random.randint(1, sizes[1])
    # if x2<x1 and y2<y1:
    #     temp1, temp2 = x2, y2
    #     x2,y2=x1,y1
    #     x1,y1=temp1,temp2
    x1 = random.randint(0, sizes[0])
    y1 = random.randint(0, sizes[1])
    x2 = random.randint(x1, sizes[0])
    y2 = random.randint(y1, sizes[1])
    if y2-y1 > sizes[1]/10:
        t = random.randint(1,3)
        y2 = int(y2/t)
        if y2 < y1:
            y2 = y1+random.randint(5,16)
    return (x1, y1, x2, y2)

def transperent(image):
    image = image.convert("RGBA")
    image_with_alpha = image.copy()

    # Получение объекта изображения с альфа-каналом
    pixels = image_with_alpha.convert("RGBA").load()
    image_tr = Image.new("RGBA",image.size, (0,0,0,0))
    # Изменение прозрачности пикселей
    for y in range(image_with_alpha.size[1]):
        for x in range(image_with_alpha.size[0]):
            r, g, b, a = pixels[x, y]
            # pixels[x, y] = (r, g, b, int(a * 0.5))  # Установка прозрачности (50%)
            image_tr.putpixel((x, y),(r, g, b, int(a * alpha)))
    return image_tr

# Загрузка изображения
image = Image.open("image_buffer.png")
sizes = image.size
for i in range(random.randint(10,20)):
    # Определение координат и размеров прямоугольника
    # x1, y1 = random.randint(0,sizes[0]), random.randint(1,sizes[1])
    # x2, y2 = random.randint(0,sizes[0]), random.randint(1,sizes[1])

    # width = x2 - x1
    # height = y2 - y1

    box = genZone(sizes)
    width = box[2]-box[0]
    height = box[3]-box[1]

    # Выбор случайных координат для сдвига
    new_x = random.randint(0, image.width - width)
    new_y = random.randint(0, image.height - height)

    # Выделение и копирование прямоугольника
    cropped = image.crop(box)
    image.paste(cropped, box)
    # Вставка скопированного прямоугольника на новые координаты
    image.paste(cropped, (new_x, new_y))

    # Сохранение измененного изображения
image.save("edited_image.png")
image1 = Image.new('RGBA', (sizes[0]+clrshiftSize*2, sizes[1]+clrshiftSize*2), (0, 0, 0, 0))
img_g = image.convert("L")

img_cyan=ImageOps.colorize(img_g, '#00b3ff', '#b8eaff')
img_pink=ImageOps.colorize(img_g, '#fb00ff', '#fed1ff')
img_cyan = transperent(img_cyan)
img_pink = transperent(img_pink)

image2 = image1.copy()
image3 = image1.copy()
image4 = image1.copy()
image1.paste(image, (int(clrshiftSize*0.5), int(clrshiftSize*0.5)))
image3.paste(img_cyan, (0,0))
image2.paste(img_pink, (clrshiftSize, clrshiftSize))
image1.alpha_composite(image2)
image1.alpha_composite(image3)
image1.save("glitch.png")