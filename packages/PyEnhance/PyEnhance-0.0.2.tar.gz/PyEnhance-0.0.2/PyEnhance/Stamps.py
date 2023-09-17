from colorama import init, Fore, Back, Style
from enum import Enum

#global CG, CR, CY, CW, CC, CM, TB
#global Info, Warn, Output, Input, Error

class Color(Enum):

    init(autoreset=True)
    Green = Fore.GREEN
    Red = Fore.RED
    Yellow = Fore.YELLOW
    White = Fore.WHITE
    Cyan = Fore.CYAN
    Magenta = Fore.MAGENTA

    def __str__(self):
        return self.value
class Type(Enum):
    Bright = Style.BRIGHT

    def __str__(self):
        return self.value
class Stamp(Enum):

    Info = f'{Color.Green}{Type.Bright}[INFO]{Fore.RESET}'
    Warn = f'{Color.Yellow}{Type.Bright}[WARRING]{Fore.RESET}'
    Output = f'{Color.Cyan}{Type.Bright}[OUTPUT]{Fore.RESET}'
    Input = f'{Color.Magenta}{Type.Bright}[INPUT]{Fore.RESET}'
    Error = f'{Color.Red}{Type.Bright}[ERROR]{Fore.RESET}'

    def __str__(self):
        return self.value

