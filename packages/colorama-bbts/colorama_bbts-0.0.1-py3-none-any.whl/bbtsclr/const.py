from colorama import Fore as f
from colorama import Back as b

class rs:
    back = b.RESET
    fore = f.RESET

backclr = {
    'black': b.BLACK,
    'red': b.RED,
    'green': b.GREEN,
    'blue': b.BLUE,
    'yellow': b.YELLOW,
    'magneta': b.MAGENTA,
    'cyan': b.CYAN,
    'white': b.WHITE,

    'light-black': b.LIGHTBLACK_EX,
    'light-red': b.LIGHTRED_EX,
    'light-green': b.LIGHTGREEN_EX,
    'light-yellow': b.LIGHTYELLOW_EX,
    'light-blue': b.LIGHTBLUE_EX,
    'light-magenta': b.LIGHTMAGENTA_EX,
    'light-cyan': b.LIGHTCYAN_EX,
    'light-white': b.LIGHTWHITE_EX,
}

foreclr = {
    'black': f.BLACK,
    'red': f.RED,
    'green': f.GREEN,
    'blue': f.BLUE,
    'yellow': f.YELLOW,
    'magneta': f.MAGENTA,
    'cyan': f.CYAN,
    'white': f.WHITE,
    'reset': f.RESET,

    'light-black': f.LIGHTBLACK_EX,
    'light-red': f.LIGHTRED_EX,
    'light-green': f.LIGHTGREEN_EX,
    'light-yellow': f.LIGHTYELLOW_EX,
    'light-blue': f.LIGHTBLUE_EX,
    'light-magenta': f.LIGHTMAGENTA_EX,
    'light-cyan': f.LIGHTCYAN_EX,
    'light-white': f.LIGHTWHITE_EX,
}