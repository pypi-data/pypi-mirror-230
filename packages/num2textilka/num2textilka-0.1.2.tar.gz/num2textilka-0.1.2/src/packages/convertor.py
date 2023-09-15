from .lang import *

def convertor(num: int, language) -> str:
    """Gets upto 3 digit integers and returns persian format of it.
    If input is 0 returns 0.

    Args:
        num (int): Upto 3 digit number. (Data type must be integer.)
        language(str): Target language dictionary.

    Raises:
        TypeError: If input's data type is not int.

    Returns:
        str: Persian format of the given input.
    """

    if not isinstance(num, int):
        raise TypeError("Given input is not an integer!")

    if num == 0:
        return 0

    res = []

    if num >= 100:
        if str(num) in languages[language]["small_number_format"]:
            hundreds = num
            num = 0

        else:
            hundreds = num // 100 * 100
            
        res.append(languages[language]["small_number_format"][str(hundreds)])
        num -= hundreds

    if num >= 10:
        if str(num) in languages[language]["small_number_format"]:
            tens = num
            num = 0

        else:
            tens = num // 10 * 10

        res.append(languages[language]["small_number_format"][str(tens)])
        num -= tens

    if num >= 1:
        res.append(languages[language]["small_number_format"][str(num)])

    return languages[language]["add_text"].join(res)
