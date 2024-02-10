lines = []
with open('swears_ru.txt', 'r', encoding='utf-8') as file:
    current_line = ''
    for line in file:
        if line.strip():  # если строка не пустая
            current_line = f"{line.strip()}"
        elif current_line:
            lines.append(current_line)
            current_line = ''
    if current_line:  # добавляем последнюю строку, если она не пустая
        lines.append(current_line)

print(lines)