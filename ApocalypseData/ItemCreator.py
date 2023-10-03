import asyncio
import sqlite3
from googletrans import Translator #TODO: requirements: googletrans
translator = Translator()

# # Перевод с английского на русский
# result = translator.translate("Hello", dest="ru")
# print(result.text)  # Привет
# # Перевод с русского на английский
# result = translator.translate("Привет", dest="en")
# print(result.text)  # Hello

items = sqlite3.connect("ApocalypseItems.db")
itemsCursor = items.cursor()
itemsCursor.execute("CREATE TABLE IF NOT EXISTS items (ItemIDInt INTEGER UNIQUE NOT NULL DEFAULT (0), ItemIDString UNIQUE NOT NULL DEFAULT none, ItemNameEn TEXT, ItemNameRu TEXT, ItemSpecialData TEXT)")
items.commit()
from win10toast import ToastNotifier #TODO: requirements: win10toast
toaster = ToastNotifier()
toastLoop = asyncio.new_event_loop()

import tkinter as tk
toaster.show_toast("Apocalypse Item Creator", "Item Creator запущен!", threaded=True,duration=2)
def sendToast(title, text, duration):
     toaster.show_toast(title, text, threaded=True, duration=duration)
# def sendToast(title, text):
#     asyncio.run_coroutine_threadsafe(sendToastAsync(title, text), toastLoop)

def check_item_id(item_id):

    itemsCursor.execute("SELECT COUNT(*) FROM items WHERE ItemIDString=?", (item_id,))
    result = itemsCursor.fetchone()
    count = result[0]
    if count > 0:
        return True
    else:
        return False
def checkforNoneContent(string : str):
    if string.isspace() or string is None or string == "":
        return True
    else:
        return False
def save_data():
    item_name_ru = entry_name_ru.get()
    item_special_data = entry_special_data.get()
    item_id = entry_id.get()
    item_name_en = entry_name_en.get()

    # Проверка наличия содержимого в поле
    # itemsCursor.execute("SELECT COUNT(*) FROM items WHERE ItemIDString IS NOT NULL")
    # result = itemsCursor.fetchone()
    # if result[0] > 0:
    #     print("Поле содержит данные")
    # else:
    #     print("Поле пустое")
    # Получение максимального значения в колонке ID
    itemsCursor.execute("SELECT MAX(ItemIDInt) FROM items")
    result = itemsCursor.fetchone()
    max_id = result[0]
    print("Максимальное значение ID:", max_id)
    isSIDNotUnique = check_item_id(item_id)
    if max_id is None:
        max_id=-1
    item_name_ru=item_name_ru.capitalize()

    item_name_en=item_name_en.capitalize()

    if not isSIDNotUnique:
        if checkforNoneContent(item_id):
            if not checkforNoneContent(item_name_en):
                item_id = str.lower(item_name_en.replace(" ","_"))

            # elif not checkforNoneContent(item_name_ru):
            else:
                # tr = translator.translate(item_name_ru, dest="en", src="ru")
                # st = tr.text
                # item_id = str.lower(tr.text.replace(" ","_"))


                sendToast("Item Creator Error", "No correct names and ids provided!", 3)
                return


        sendToast("Item Created!", f"ID: {max_id+1}, sID: {item_id}, nameEn: {item_name_en}, nameRu: {item_name_ru}, spec: {item_special_data}", 2+len(item_id)/10)
        print(f"ID: {max_id+1}, sID: {item_id}, nameEn: {item_name_en}, nameRu: {item_name_ru}, spec: {item_special_data}")
        itemsCursor.execute("INSERT INTO items (ItemIDInt, ItemIDString, ItemNameEN, ItemNameRu, ItemSpecialData) VALUES (?, ?, ?, ?, ?)", (max_id+1, item_id, item_name_en, item_name_ru, ""))
        # itemsCursor.execute("")
    else:
        sendToast("String ID is not unique!", item_id, 3)



    # Здесь можно добавить код для сохранения данных в словарь или другое хранилище

def clear_fields():
    entry_name_ru.delete(0, tk.END)
    entry_special_data.delete(0, tk.END)
    entry_id.delete(0, tk.END)
    entry_name_en.delete(0, tk.END)

root = tk.Tk()
root.title("Apocalypse Item Creator")

label_name_ru = tk.Label(root, text="Имя предмета на русском:")
label_name_ru.pack()
entry_name_ru = tk.Entry(root)
entry_name_ru.pack()

label_special_data = tk.Label(root, text="Особенности предмета:")
label_special_data.pack()
entry_special_data = tk.Entry(root)
entry_special_data.pack()

label_id = tk.Label(root, text="Текстовый ID предмета:")
label_id.pack()
entry_id = tk.Entry(root)
entry_id.pack()

label_name_en = tk.Label(root, text="Имя предмета на английском:")
label_name_en.pack()
entry_name_en = tk.Entry(root)
entry_name_en.pack()

button_save = tk.Button(root, text="Записать", command=save_data)
button_save.pack()

button_clear = tk.Button(root, text="Очистить", command=clear_fields)
button_clear.pack()

root.mainloop()