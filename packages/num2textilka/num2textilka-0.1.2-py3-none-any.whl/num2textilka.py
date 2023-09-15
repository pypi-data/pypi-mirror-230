from os import system
from packages import *


def num2text(num: int = None, language: str = None):
    """Number to Text convertor.

    Args:
        num (int): The number you want to translate. Will be asked if not given.

        language (str): The language you want to translate to. Will be asked if not given.
        Available languages are "english" and "persian".
    """

    if num == None:
        num = input("What's Your Number ==> ")

    if not str(num).isdecimal():
        print(f"{num} is not a number. Exitting.")
        return None
    else:
        num = int(num)
    if not 0 <= num < 10**105:
        print(f"{num} is not in range 0 - 10^105")
        return None

    if language == None:
        language = input("""1- English
2- Persian
Select a language ==> """)

    if language == "1" | "english":
        language = "english"
    elif language == "2" | "persian" | "farsi":
        language = "persian"
    else:
        print(f"{language} is not a valid language. Exitting.")
        return None

    # region Main Code

    if num == 0:
        if language == "english":
            print("Zero")
        elif language == "persian":
            print("صفر")

    # Complex numbers
    else:
        num = str(num)
        slice_index = len(num)
        numbers_list = []

        if slice_index < 3:
            num = num.zfill(3)
            slice_index = len(num)

        while slice_index > 0:
            sliced_number = num[slice_index-3:slice_index]
            numbers_list.insert(0, sliced_number)
            slice_index -= 3

            if 0 < slice_index < 3:
                sliced_number = num[0:slice_index]
                numbers_list.insert(0, sliced_number)
                break

        final_format = []
        big_number_index = len(numbers_list) - 1

        for item in numbers_list:
            item_converted = convertor(int(item), language)

            if item_converted != 0:
                final_format.append(
                    item_converted + " " + languages[language]["big_number_format"][big_number_index])

            big_number_index -= 1

        system("cls")
        print(f"Number {int(num)} in {language} language is:")
        print(languages[language]["add_text"].join(final_format))
    # endregion
