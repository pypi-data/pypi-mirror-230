from collections import UserDict
from datetime import datetime
from .prompt_tool import Completer, RainbowLexer
from prompt_toolkit import prompt
import pickle
import re


class PhoneException(Exception):
    pass


class EmailException(Exception):
    pass


class BDException(Exception):
    pass


class Field:
    def __init__(self, value) -> None:
        self.__private_value = None
        self.value = value

    @property
    def value(self):
        return self.__private_value

    @value.setter
    def value(self, value):
        self.__private_value = value


class Name(Field):
    pass


class Address(Field):
    pass


class Phone(Field):
    def __init__(self, value) -> None:
        super().__init__(value)

    @Field.value.setter
    def value(self, value: str):
        value = value.strip()
        # перевірка довжини номера та чи всі введені значення є  цифрами
        right_len = len(value) == 10 or len(value) == 12
        if value.isdigit() and right_len:
            Field.value.fset(self, value)
        else:
            raise PhoneException


class Email(Field):
    def __init__(self, value) -> None:
        super().__init__(value)

    @Field.value.setter
    def value(self, value: str):
        result = re.findall(r"[a-zA-z]{1}[\w\.]+@[a-zA-z]+\.[a-zA-z]{2,}", value)
        if result:
            Field.value.fset(self, value)
        else:
            raise EmailException


class Birthday(Field):
    def __init__(self, value) -> None:
        super().__init__(value)

    @Field.value.setter
    def value(self, value: str):
        value.strip()
        # перевірка чи вік є в діавзоні 0 - 150 р
        delta = datetime.now() - datetime.strptime(value, "%d.%m.%Y")
        if (delta.days < 0) or (delta.days > 53000):
            raise BDException
        else:
            Field.value.fset(self, value)


class Record:
    def __init__(
        self,
        name: Name,
        addres: Address = None,
        phone: Phone = None,
        email: Email = None,
        birthday: Birthday = None,
    ):
        self.name = name
        self.addres = addres
        self.phones = list()
        if phone:
            self.phones.append(phone.value)

        self.email = email
        self.birthday = birthday

    def add_email(self, email: Email):
        self.email = email

    def add_bd(self, birthday: Birthday):
        self.birthday = birthday

    def add_phone(self, phone: Phone):
        self.phones.append(phone.value)

    def change_phone(self, old_phone, new_phone):
        index = self.phones.index(old_phone)
        self.phones[index] = new_phone

    def is_birthday_next_days(self, n: int) -> bool:
        if self.birthday.value:
            birthday_date = datetime.strptime(self.birthday.value, "%d.%m.%Y")
            current_date = datetime.now()
            birthday_date = birthday_date.replace(year=current_date.year)
            if current_date > birthday_date:
                birthday_date = birthday_date.replace(year=current_date.year + 1)

            delta_days = birthday_date - current_date

            if 0 <= delta_days.days < n:
                return True
            return False

    def __repr__(self) -> str:
        if self.birthday == None:
            bd = "_"
        else:
            bd = self.birthday.value

        if self.email == None:
            em = "_"
        else:
            em = self.email.value

        if self.phones == list():
            ph = "_"
        else:
            ph = str(self.phones)

        return "|{:^20}|{:^20}|{:^20}|".format(ph, bd, em)


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record
        return self.data

    def save_ab(self):
        with open("addressbook.pkl", "wb") as file:
            pickle.dump(self.data, file)

    def open_ab(self):
        with open("addressbook.pkl", "rb") as file:
            self.data = pickle.load(file)


# функція для обробки винятків
def input_error(func):
    def inner(*args):
        try:
            return func(*args)
        except IndexError:
            return "Будь ласка, введіть всю необхідну інформацію!"
        except KeyError:
            return "Даний контакт відсутній у книзі контактів!"
        except PhoneException:
            return "Не правильний формат номеру телефона. Очікується - 0961010100 або 380961010100"

        except EmailException:
            return "Не правильний формат електронної пошти. Очікується - test@test.com"
        except BDException:
            return "Дата народження вказано не правильно, вік виходить за межі діапазону 0-150"

        except ValueError:
            return "Не правильний формат дати народження. Повинен бути дд.мм.рррр"

    return inner


AB = AddressBook()
try:
    AB.open_ab()
except FileNotFoundError:
    AB = AddressBook()


@input_error
def add_handler(user_info: str):
    name = user_info[0].lstrip()
    rec = Record(Name(name))
    AB.add_record(rec)
    return f"Користувач{user_info[0]} доданий"


@input_error
def add_number(user_input: str):
    name = user_input[0].lstrip()
    phone = user_input[1]
    rec = AB[name]
    rec.add_phone(Phone(phone))
    return f"Номер {phone} додано до контакту {name}"


@input_error
def add_email(user_input: str):
    name = user_input[0].lstrip()
    email = user_input[1]
    rec = AB[name]
    rec.add_email(Email(email))
    return f"Електронна пошта {email} додано до контакту {name}"


@input_error
def add_birthday(user_input: str):
    name = user_input[0].lstrip()
    bd = user_input[1].lstrip()
    rec = AB[name]
    rec.add_bd(Birthday(bd))
    return f"Дата народження {bd} додано до контакту {name}"


def help_handler(*args):
    print("add contact, name - Додати новий контакт до Книги контактів")
    print("add phone, name, phone - Додати номер телефону до існуючого контакту ")
    print("add email, name, email - Додати електронну пошту до існуючого контакту")
    print(
        "add birthday, name, birthday	- Додати  день народження до існуючого контакту"
    )
    print(
        "change phone, name, old phone, new phone - Змінити номер телефону вказаного контакту"
    )
    print(
        "change birthday, name, birthday - Змінити день народження вказаного контакту"
    )
    print(
        "delete contact, name - 	Видалити контакт за вказаним ім’ям з Книги контактів"
    )
    print(
        "delete phone, name, phone - Видалити номер телефону контакту з Книги контактів"
    )
    print(
        "delete email, name, email - Видалити електронну пошту контакту з Книги контактів"
    )
    print(
        "delete birthday, name, birthday - Видалити день народження контакту з Книги контактів"
    )
    print(
        "get birthday, days - Показати в кого день народження через введену кількість днів"
    )
    print("show all - Показати всі контакти з Книги контактів")
    print("find name, name - Знайти контакт")
    print(
        "exit, close, goodbye	(одна команда на вибір)- Закінчити роботу або повернутися в головне меню"
    )

    return " "


@input_error
def ch_phone(user_input: str):
    name = user_input[0].lstrip()
    old_phone = Phone(user_input[1].lstrip())
    new_phone = Phone(user_input[2].lstrip())
    rec = AB[name]
    if old_phone.value in rec.phones:
        rec.change_phone(old_phone.value, new_phone.value)
        return f"Номер телефону користувача {name} змінено на {new_phone.value}"
    return f"Номер телефону {old_phone.value} не знайдено!"


@input_error
def change_email(user_input: str):
    name = user_input[0].lstrip()
    email = user_input[1]
    rec = AB[name]
    rec.add_email(Email(email))
    return f"Електронну пошту контакту {name} змінено на {email} "


@input_error
def change_birthday(user_input: str):
    name = user_input[0].lstrip()
    bd = user_input[1].lstrip()
    rec = AB[name]
    rec.add_bd(Birthday(bd))
    return f"День народження контакту {name} змінено на {bd} "


@input_error
def del_contact(user_input: str):
    name = user_input[0].lstrip()
    AB.pop(name)
    return f"Контакт {name} видалено"


def show_all(*args):
    print("|{:^20}|{:^20}|{:^20}|{:^20}|".format("Name", "Phone", "Birthday", "Email"))
    for k, v in AB.items():
        print("|{:^19}".format(k), v)
    return ""


@input_error
def del_phone(user_input: str):
    name = user_input[0].lstrip()
    phone = Phone(user_input[1].lstrip())
    rec = AB[name]
    if phone.value in rec.phones:
        rec.phones.remove(phone.value)
        # print(rec.phones)
        return f"Номер телефону {phone.value} користувача {name} видалено"
    return f"Номер телефону {phone.value} не знайдено!"


@input_error
def del_email(user_input: str):
    name = user_input[0].lstrip()
    rec = AB[name]
    rec.add_email(None)
    return f"Електронну пошту контакту {name} видалено "


@input_error
def del_birthday(user_input: str):
    name = user_input[0].lstrip()
    rec = AB[name]
    rec.add_bd(None)
    return f" Для контакту {name} дату народження видалено"


@input_error
def save_adbook(*args):
    AB.save_ab()
    return f"Книга контактів збережена"


@input_error
def find_name(user_input: str):
    name = user_input[0].lstrip()
    for key in AB.keys():
        if name == key:
            record = AB[name]
            return f"{name}: {record}"
    return f"Контакт {name} відсутній у книзі контактів"


def get_birthday(user_input: str):
    try:
        n = int(user_input[0])
    except ValueError:
        return "введіть число в діапазоні 1 - 354 "
    except IndexError:
        return "Будь ласка, введіть всю необхідну інформацію!"

    result = list()

    if n in range(1, 365):
        for name, record in AB.items():
            if record.birthday:
                if record.is_birthday_next_days(n):
                    result.append(name)
    else:
        return f"введіть число в діапазоні 1 - 364 "

    if result:
        return f"Через {n} днів день народження святкують {result}"
    return f"Через {n} днів день народження не святкує жоден з контактів"


COMMANDS = {
    add_handler: "add contact",
    add_number: "add phone",
    add_email: "add email",
    add_birthday: "add birthday",
    help_handler: "help",
    ch_phone: "change phone",
    change_email: "change email",
    change_birthday: "change birthday",
    del_contact: "delete contact",
    show_all: "show all",
    save_adbook: "save",
    del_phone: "delete phone",
    del_email: "delete email",
    del_birthday: "delete birthday",
    find_name: "find name",
    get_birthday: "get birthday",
}


def command_parser(user_input: str):
    user_info = user_input.split(",")
    command = user_info[0]

    for key, value in COMMANDS.items():
        if command.lower() == value:
            return key(user_info[1:])
    return "Не відома команда. Спробуйте ще раз! Команду та основні блоки розділіть комами!"


def main():
    print('Вас вітає книга контактів! Введіть команду чи "help" для допомоги')
    while True:
        user_input = prompt(
            ">>> ",
            completer=Completer,
            lexer=RainbowLexer(),
        ).strip()
        # user_input = input(">>> ")
        if user_input.lower() in ["good bye", "exit", "close"]:
            AB.save_ab()
            print("Good bye!")
            break

        result = command_parser(user_input)

        print(result)


if __name__ == "__main__":
    main()

# Ivan Markovskyi
