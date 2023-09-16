from .calculator import calc
from pathlib import Path
from .prompt_tool import Completer, RainbowLexer
from prompt_toolkit import prompt
from . import adbook, note_book, sort_folder


def run_folder():
    folder_path = input("Введіть шлях до теки для сортування: ")
    sort_folder.main(Path(folder_path))
    return "Сортування завершено успішно"


bot_command_dict = {
    "1": adbook.main,
    "2": note_book.run_notebook,
    "3": run_folder,
    "4": calc,
}


def assistant_bot():
    print("Вас вітає персональний помічник FriendlyHandbook")
    print(
        """
    Виберіть одну з наступних опцій:
    - Книга контактів (PhoneBook) -> Натисніть '1'
    - Нотатки (NoteBook) -> Натисніть '2'
    - Сортувач папок (CleanFolder) -> Натисніть '3'
    - Калькулятор (Calculator) -> Натисніть '4'
    - Вийти з помічника -> Натисніть '0'
    """
    )

    while True:
        command = prompt(
            "Введіть номер опції (від 0 до 4): ",
            completer=Completer,
            lexer=RainbowLexer(),
        ).strip()

        if command == "0":
            raise SystemExit("\nДо побачення!\n")

        elif command in bot_command_dict.keys():
            handler = bot_command_dict[command]
            answer = handler()
            print(answer)

        else:
            print("Некоректне число. Будь ласка, введіть число від 0 до 4")


if __name__ == "__main__":
    assistant_bot()


# Oleksandr Yukha
