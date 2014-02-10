
from colorama import Fore

def info(message):
    print(Fore.GREEN + 'INFO  ' + Fore.RESET + message)

def warn(message):
    print(Fore.GREEN + 'WARN  ' + Fore.RESET + message)

def error(message):
    print(Fore.RED +   'ERROR ' + Fore.RESET + message)


