# Функція для додавання
def add(x, y):
    return x + y


# Функція для віднімання
def sub(x, y):
    return x - y


# Функція для множення
def multiply(x, y):
    return x * y


# Функція для ділення
def div(x, y):
    if y == 0:
        return "На нуль ділити не можна"
    return x / y


# Основний цикл програми
def calc():
    while True:

        choice = input("Введіть операцію ('+', '-', '*', '/',     Для виходу -> 'q'): ")

        if choice == 'q':
            print("Програма завершена.")
            break

        num1 = float(input("Введіть перше число: "))
        num2 = float(input("Введіть друге число: "))

        if choice == '+':
            print("Результат:", add(num1, num2))
        elif choice == '-':
            print("Результат:", sub(num1, num2))
        elif choice == '*':
            print("Результат:", multiply(num1, num2))
        elif choice == '/':
            print("Результат:", div(num1, num2))
        else:
            print("Невірний ввід. Спробуйте ще раз.")
    return ('Повернення в попереднє Меню')

if __name__ == "__main__":
    calc()
