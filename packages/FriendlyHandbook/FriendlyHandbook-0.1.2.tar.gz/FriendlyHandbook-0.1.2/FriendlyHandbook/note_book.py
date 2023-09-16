import os
import pickle
from collections import UserDict
from .prompt_tool import Completer, RainbowLexer
from prompt_toolkit import prompt


SAVE_FILENAME = "notebook.pkl"  # Ім'я файлу для запису данних


class Field_NOTEBOOK:
    def __init__(self, value):
        self.value = value


class Tag(Field_NOTEBOOK):
    def __eq__(self, other):
        return isinstance(other, Tag) and self.value == other.value


class Name(Field_NOTEBOOK):
    pass


class Record:
    def __init__(self, name: Name, tags: list, text: str):
        self.name = name
        self.tags = [Tag(tag) for tag in tags]
        self.text = text

    def add_tag(self, tag):
        hashtag = Tag(tag)
        if hashtag not in self.tags:
            self.tags.append(hashtag)

    def find_tag(self, value):
        for tag in self.tags:
            if tag.value == value:
                return tag
        return None

    def delete_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)

    def edit_text(self, new_text):
        self.text = new_text


class Notebook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def save_to_file(self):  # збереження файлу
        with open(SAVE_FILENAME, "wb") as file:
            pickle.dump(self.data, file)

    def load_from_file(self):  # завантаження файлу
        if os.path.exists(SAVE_FILENAME):
            try:
                with open(SAVE_FILENAME, "rb") as file:
                    self.data = pickle.load(file)
            except FileNotFoundError:
                print(f"Файл '{SAVE_FILENAME}' не знайдений.")
        else:
            # Не видаляти дані, якщо файл не існує
            print(f"Файл '{SAVE_FILENAME}' не існує. Дані не завантажено.")

    def find_record(self, value):
        return self.data.get(value)

    def edit_record(self, name, new_tags, new_text):
        if name in self.data:
            record = self.data[name]
            record.tags = [Tag(tag) for tag in new_tags]
            record.text = new_text
            self.data[name] = record
            print(f"Нотатка {name} була змінена.")
        else:
            print(f"Нотатка '{name}' не знайдена.")

    def search_by_tag(self, tag):
        matching_records = []
        for record in self.data.values():
            if any(tag == t.value for t in record.tags):
                matching_records.append(record)
        return matching_records


def run_notebook():
    note_book = Notebook()
    note_book.load_from_file()

    while True:
        print("\nOptions:")
        print("1. Додати нотатку           (add note)")
        print("2. Знайти нотатку за назвою (find note)")
        print("3. Пошук за тегами          (find by tag)")
        print("4. Вивести всі нотатки      (show all notes)")
        print("5. Редагувати нотатку       (change note)")
        print("6. Редагувати текст нотатки (change text)")
        print("7. Редагувати теги нотатки  (change tag)")
        print("8. Видалити нотатку         (delete note)")
        print("9. Додати теги до нотатки   (add tag)")
        print("0. Вихід з записника        (close)")

        # choice = input("Виберіть опцію: ")
        choice = prompt(
            "Виберіть опцію: ",
            completer=Completer,
            lexer=RainbowLexer(),
        ).strip()

        if choice == "1" or choice == "add note":
            name = input("Вкажіть ім'я нотатки: ")
            hashtags = input(
                "Вкажіть теги нотатки (Якщо кілька, то вказати через кому): "
            ).split(", ")
            text = input("Введіть текст нотатки: ")

            name_field = Name(name.strip())
            record = Record(name_field, hashtags, text)
            note_book.add_record(record)
            print(f"Нотатка {name} добавлена до записника.")
            pass

        elif choice == "2" or choice == "find note":
            search_term = input("Вкажіть ім'я нотатки для пошук: ")
            record = note_book.find_record(search_term)
            if record:
                print(f"Name: {record.name.value}")
                print("Tags:")
                for tag in record.tags:
                    print(tag.value)
                print("Text:")
                print(record.text)
            else:
                print(f"Нотатку з ім'ям '{search_term}' не було знайдено.")
            pass

        elif choice == "3" or choice == "find by tag":
            tag_to_search = input("Введіть тег для пошуку: ")
            matching_records = note_book.search_by_tag(tag_to_search)
            if matching_records:
                print("Matching Records:")
                for record in matching_records:
                    print(f"Name: {record.name.value}")
                    print("Tags:")
                    for tag in record.tags:
                        print(tag.value)
                    print("Text:")
                    print(record.text)
            else:
                print(f"Нотаток з тегом '{tag_to_search}' не знайдено.")
            pass

        elif choice == "4" or choice == "show all notes":  # Виведення всіх нотаток
            print("Список всіх нотаток:")
            for name, record in note_book.data.items():
                print(f"Name: {record.name.value}")
                for tag in record.tags:
                    print(f"Tags:{tag.value}")
                print(f"Text: {record.text}")

            pass

        elif choice == "5" or choice == "change note":
            edit_name = input("Вкажіть ім'я нотатки для редагування: ")
            new_tags = input(
                "Вкажіть нові теги (Якщо кілька, то вказати через кому): "
            ).split(", ")
            new_text = input("Введіть новий текст: ")
            note_book.edit_record(edit_name.strip(), new_tags, new_text)
            pass

        elif choice == "6" or choice == "change text":
            edit_name = input("Вкажіть ім'я нотатки для редагування тексту: ")
            record = note_book.find_record(edit_name.strip())
            if record:
                new_text = input("Введіть новий текст: ")
                record.edit_text(new_text)
                print(f"Текст нотатки {edit_name} був змінений.")
            else:
                print(f"Нотатку з ім'ям '{edit_name}' не було знайдено.")

        elif choice == "7" or choice == "change tag":
            edit_tags_name = input("Вкажіть ім'я нотатки для редагування тегів: ")
            record = note_book.find_record(edit_tags_name.strip())
            if record:
                new_tags = input(
                    "Вкажіть нові теги для нотатки (Якщо кілька, то вказати через кому): "
                ).split(", ")
                record.tags = [Tag(tag.strip()) for tag in new_tags]
                print(f"Теги для нотатки {edit_tags_name} були змінені.")
            else:
                print(f"Нотатку з ім'ям '{edit_tags_name}' не було знайдено.")

        elif choice == "8" or choice == "delete note":
            delete_term = input("Вкажіть ім'я нотатки для видалення: ")
            record = note_book.find_record(delete_term)
            if record:
                del note_book.data[delete_term]
                print(f"Нотатка {delete_term} була видалена з записника.")
            else:
                print(f"Нотатку з ім'ям '{delete_term}' не було знайдено.")
            pass

        elif choice == "9" or choice == "add tag":
            edit_tags_name = input(
                "Вкажіть ім'я нотатки, до якої потрібно додати теги: "
            )
            record = note_book.find_record(edit_tags_name)
            if record:
                new_tags = input(
                    "Вкажіть нові теги для нотатки (Якщо кілька, то вказати через кому): "
                ).split(", ")
                for tag in new_tags:
                    record.add_tag(tag.strip())
                print(f"Теги для нотатки {edit_tags_name} були додані.")
            else:
                print(f"Нотатку з ім'ям '{edit_tags_name}' не було знайдено.")
            pass

        elif choice == "0" or choice == "close":
            # Зберегти дані перед виходом з програми
            note_book.save_to_file()
            print(f"Дані збережено в файлі '{SAVE_FILENAME}'")
            print("До побачення!")
            from main import assistant_bot

            assistant_bot()
            break

        else:
            print("Не коректний вибір. Виберіть опцію.")

        # Завершуємо пункт меню і чекаємо Enter перед поверненням до головного меню.
        input("Для продовження, натисніть Enter: ")


if __name__ == "__main__":
    run_notebook()

# Kovaleno Oleksandr
