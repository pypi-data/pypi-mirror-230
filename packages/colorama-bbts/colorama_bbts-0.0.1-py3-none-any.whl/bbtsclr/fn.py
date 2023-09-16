from .const import foreclr, backclr, rs

def printclr(msg, fore="", back=""):
    if fore != "":
        fore = foreclr[fore]
    if back != "":
        back = backclr[back]

    print(fore + back + msg + rs.fore + rs.back)

def error(msg, start="ERROR: ", fore="light-red", back=""):
    if fore != "":
        fore = foreclr[fore]
    if back != "":
        back = backclr[back]

    print(fore + back + start + msg + rs.fore + rs.back)

def warn(msg, start="WARNING: ", fore="light-yellow", back=""):
    if fore != "":
        fore = foreclr[fore]
    if back != "":
        back = backclr[back]

    print(fore + back + start + msg + rs.fore + rs.back)

def success(msg, start="", fore="light-green", back=""):
    if fore != "":
        fore = foreclr[fore]
    if back != "":
        back = backclr[back]

    print(fore + back + start + msg + rs.fore + rs.back)

def log(msg, start="LOG: ", fore="magneta", back=""):
    if fore != "":
        fore = foreclr[fore]
    if back != "":
        back = backclr[back]

    print(fore + back + start + msg + rs.fore + rs.back)