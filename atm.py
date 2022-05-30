import time, os, sys, colorama
from colorama import Fore, Back, Style
colorama.init(autoreset=True)

BankLogo = """
 ______   _______  _        _          _        _______  _______  _______   
(  ___ \ (  ___  )( (    /|| \    /\  ( (    /|(  ___  )(       )(  ____ \  
| (   ) )| (   ) ||  \  ( ||  \  / /  |  \  ( || (   ) || () () || (    \/  
| (__/ / | (___) ||   \ | ||  (_/ /   |   \ | || (___) || || || || (__      
|  __ (  |  ___  || (\ \) ||   _ (    | (\ \) ||  ___  || |(_)| ||  __)     
| (  \ \ | (   ) || | \   ||  ( \ \   | | \   || (   ) || |   | || (        
| )___) )| )   ( || )  \  ||  /  \ \  | )  \  || )   ( || )   ( || (____/\  
|/ \___/ |/     \||/    )_)|_/    \/  |/    )_)|/     \||/     \|(_______/"""

LogoRows = 9


def SlowType(str, speed):
    for letter in str:
        sys.stdout.write(letter)
        sys.stdout.flush()
        time.sleep(speed ** -1)

def AnimatedLogo(Logo, rows):
    for line in range(rows):
        print(f"{Fore.YELLOW}{Logo.splitlines()[line]}")
        time.sleep(0.2)

def ClearCMD():
    os.system('cls')


class LoginSystem:
    def __init__(self):
        self.LogoAnimation()
        self.Login()

    def LogoAnimation(self):
        ClearCMD()
        AnimatedLogo(BankLogo, LogoRows)
        SlowType(
        """\nHello! Welcome to the (BANK NAME) ATM.\n""", 100)

    def Login(self):
        username = str(input("Username: "))
        pin = int(input("PIN: "))

    def ValidateCredentials(self):
        pass ## Reading json file logic will go here

class MainMenu:
    def __init__(self):
        pass


if __name__ == "__main__":
    LoginSystem()