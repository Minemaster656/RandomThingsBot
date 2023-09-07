import random
symbols = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
while True:
    lng = int(input("Длина: "))
    for i in range(lng):
        print(random.choice(symbols), end="")
    print()