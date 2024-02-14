# import tkinter as tk
# from tkinter import ttk, NW
# import json
#
# def add_new_object():
#     ...
#
#     count = int(count_entry.get())
#     items_keys = list(map(str.strip, keys_text.get("1.0", tk.END).splitlines()))
#     items_counts = list(map(int, values_text.get("1.0", tk.END).splitlines()))
#     items = {}
#     for i, k in enumerate(items_keys):
#         items[k]=items_counts[i]
#     byprod_keys = list(map(str.strip, byprod_keys_text.get("1.0", tk.END).splitlines()))
#     byprod_counts = list(map(int, byprod_values_text.get("1.0", tk.END).splitlines()))
#     byprods = {}
#     for i, k in enumerate(byprod_keys):
#         byprods[k] = byprod_counts[i]
#     print("ID:", _id.get())
#     print("Count:", count)
#     print("Dict Keys:", items_keys)
#     print("Dict Values:", items_counts)
#
#     print(items)
#     print(byprods)
#
#     new_object = {
#         "name": "loc.items.name"+_id.get(),
#         "desc": "loc.items.name"+_id.get(),
#         "image": image.get(),
#         "emoji": emoji.get(),
#         "recipes": [
#             {
#                 "crafter": crafter.get(),
#                 "crafter_level": int(crafter_level.get()),
#                 "skills": {
#                     "mining": int(skill_mining.get()),
#                     "production": int(skill_production.get()),
#                     "magic": int(skill_magic.get()),
#                     "oratory": int(skill_oratory.get()),
#                     "science": int(skill_science.get()),
#                     "calculations": int(skill_calculations.get())
#                 },
#                 "items": items,
#                 "result_value": int(entry_result_value.get()),
#                 "byproducts": byprods
#             }
#         ]
#     }
#
#     with open('your_json_file.json', 'r+') as file:
#         data = json.load(file)
#         data.update({data.items()[-1][0] + 1: new_object})
#         file.seek(0)
#         json.dump(data, file, indent=4)
#
# # Создание окна Tkinter
# root = tk.Tk()
# root.title("Добавление нового объекта в JSON")
#
# # Создание и размещение виджетов
# # Здесь нужно создать и разместить все необходимые Entry и другие виджеты для ввода данных
#
# id_label = tk.Label(root, text="ID")
# id_label.pack()
# _id = tk.Entry(root)
# _id.pack()
#
# label2 = tk.Label(root, text="Enter a number:")
# label2.pack()
# entry2 = tk.Entry(root)
# entry2.pack()
#
#
#
#
# count_label = tk.Label(root, text="Количество предмета на выходе")
# count_label.pack()
# count_entry = tk.Entry(root)
# count_entry.pack()
#
# items_frame = tk.Frame(root, borderwidth=2, relief="groove")
# items_frame.pack(side=tk.LEFT, padx=10, pady=10)
#
# keys_label = tk.Label(items_frame, text="ID предметов выхода:")
# keys_label.pack()
# keys_text = tk.Text(items_frame, height=5, width=30)
# keys_text.pack()
#
# values_label = tk.Label(items_frame, text="Количества предметов выхода:")
# values_label.pack()
# values_text = tk.Text(items_frame, height=5, width=30)
# values_text.pack()
#
# byprod_frame = tk.Frame(root, borderwidth=2, relief="groove")
# byprod_frame.pack(side=tk.LEFT, padx=10, pady=10)
#
# byprod_keys_label = tk.Label(byprod_frame, text="ID побочных продуктов:")
# byprod_keys_label.pack()
# byprod_keys_text = tk.Text(byprod_frame, height=5, width=30)
# byprod_keys_text.pack()
#
# byprod_values_label = tk.Label(byprod_frame, text="Количество побочных продуктов:")
# byprod_values_label.pack()
# byprod_values_text = tk.Text(byprod_frame, height=5, width=30)
# byprod_values_text.pack()
#
# # Кнопка для добавления нового объекта
# btn_add = tk.Button(root, text="Добавить", command=add_new_object)
# btn_add.pack()
#
# # Запуск главного цикла Tkinter
# root.mainloop()