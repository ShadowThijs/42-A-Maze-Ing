"""Return Terminal colors."""


def unicode_color(cur: int) -> str:
    """Returns colors unicode color."""

    if (cur == 0):
        return u"\u001b[40m"
    elif (cur == 1):
        return u"\u001b[41m"
    elif (cur == 2):
        return u"\u001b[42m"
    elif (cur == 3):
        return u"\u001b[43m"
    elif (cur == 4):
        return u"\u001b[44m"
    elif (cur == 5):
        return u"\u001b[45m"
    elif (cur == 6):
        return u"\u001b[46m"
    else:
        return u"\u001b[47m"
