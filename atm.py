from argparse import Action
import time, os, sys, colorama
from urllib import request
from colorama import Fore, Back, Style
import json
import datetime
import hashlib

colorama.init(autoreset=True)

loaded_username = ""
loaded_user = {}

def cls():
    os.system('cls' if os.name=='nt' else 'clear')
    
def slowType(str, interval):
    for letter in str:
        sys.stdout.write(letter)
        sys.stdout.flush()
        time.sleep(interval)

def showTitleScreen():
    BANK_LOGO = """
    ____   _                                                           
    |  _ \ (_)                                                          
    | |_) | _   __ _                                                    
    |  _ < | | / _` |                                                   
    | |_) || || (_| |                                                   
    |____/ |_| \__, |     _                                             
    |  _ \      __/ |    | |                                            
    | |_) |  __|____ __  | | __                                         
    |  _ <  / _` || '_ \ | |/ /                                         
    | |_) || (_| || | | ||   <                                          
    |______ \__,_||_| |_||_|\_\                    _    _               
    / ____|                                      | |  (_)              
    | |      ___   _ __  _ __    ___   _ __  __ _ | |_  _   ___   _ __  
    | |     / _ \ | '__|| '_ \  / _ \ | '__|/ _` || __|| | / _ \ | '_ \ 
    | |____| (_) || |   | |_) || (_) || |  | (_| || |_ | || (_) || | | |
     \_____|\___/ |_|   | .__/  \___/ |_|   \__,_| \__||_| \___/ |_| |_|
                        | |                                             
                        |_|                                             
    """.splitlines()
    rows = 19

    for line in BANK_LOGO:
        print(f"{line}")
        time.sleep(0.05)
    time.sleep(0.5)



#Receipt needs 
"""
- User's full name
- Date / Time of the transaction taken place
- Address of the ATM (School's address --> 419A Windsor Rd, Baulkham Hills NSW 2153) 
- Type of transaction (Withdrawal or Deposit)
- Amount being withdrawn / deposited
- Current Balance
"""

def printReceipt(username, transactionType, amount, balance): 
    
    ## Info needed to be shown in receipt 
    date = datetime.datetime.now().strftime("%d/%m/%Y")
    time = datetime.datetime.now().strftime("%H:%M:%S")
    address = "419A Windsor Rd, Baulkham Hills NSW 2153"

    
    ## Receipt components 
    receipt = f"""______________________________________________________________
|                       ╔══╗╔══╗╔═══╗     
|                       ║╔╗║║╔╗║║╔═╗║  
|                       ║╚╝╚╣╚╝╚╣║─╚╝   
|                       ║╔═╗║╔═╗║║─╔╗                        
|                       ║╚═╝║╚═╝║╚═╝║ 
|                       ╚═══╩═══╩═══╝    
|    DATE: {date}
|    TIME: {time}
|    ADDRESS: {address.upper()}
|                    
|    {transactionType.upper()} FOR USER: {username.upper()}
|    AMOUNT: {amount}
|    CURRENT BALANCE: {balance}
|           
|         BANK FROM HOME, THE OFFICE, OR THE ROAD,
|                BBC MAKES BANKING EASIER!
|          
|____________________________________________________________""".splitlines()

    # go through and append ending line
    newReceipt = [receipt[0]]
    for i in receipt[1:]:
        newReceipt.append(i.ljust(61, " ") + "|")
    newReceipt = "\n" + "\n".join(newReceipt)

    with open("receipt.txt", "w", encoding="utf-8") as f:
        f.write(newReceipt)

# a short function that takes an input from user and makes it all lowercase if we do not care about case
def getInput(message, case_sensitive):
    answer = input(message)
    return answer if case_sensitive else answer.lower()

def askQuestion(message, answer_validator,  case_sensitive=True):
    """
    Repeatedly asks user for an input until input meets the correct requirements

    @param message: the message to print when asking user for input
    @param answer_validator: a function that returns whether an input is valid or not 
    @param case_sensitive: whether input should be treated as case sensitive
    @return: user's (valid) answer
    """

    LOCKOUT_NUM = 5
    
    user_input = getInput(message, case_sensitive)
    
    i = 0
    while(not answer_validator(user_input)): # continues running while answer not valid
        i += 1

        # print message saying that user's answer was invalid. If user fails more than 3 times, the message becomes more aggressive.
        if (i == LOCKOUT_NUM):
            print("ERROR: INCORRECT RESPONSE FORMAT. MALICIOUS ACTIVITY SUSPECTED. COMMENCING LOCKOUT...")
            quitProgram()
        elif (i >= 3):
            print(f"ERROR: INCORRECT RESPONSE FORMAT. YOU WILL BE LOCKED OUT OF THE SYSTEM IN {LOCKOUT_NUM - i} ATTEMPT{'S' if LOCKOUT_NUM - i >= 2 else ''}. PLEASE ENTER A VALID RESPONSE.")
        else:
            print("ERROR: INCORRECT RESPONSE FORMAT. PLEASE ENTER A VALID RESPONSE.")
        
        # get new input
        user_input = getInput(message, case_sensitive)

    # the answer is valid, return it
    return user_input

def askQuestionAdvanced(message, answer_validator, correct_response="", cancel_response="CANCEL", case_sensitive=True):
    """
    Similar to the askQuestion function, but accepts an answer validator which generates strings in response to input.
    Will only accept answer if the correct string is generated by the validator, otherwise prints the validated message
    """

    user_input = getInput(message, case_sensitive)
    i = 0
    response = answer_validator(user_input)

    while(response != correct_response and response != cancel_response): # continues running while answer not valid
        i += 1
        print(response)

        # get new input
        user_input = getInput(message, case_sensitive)
        response = answer_validator(user_input)

    if response == cancel_response:
        return None
    return user_input

def quitProgram():
    """
    Quits the program (gracefully)
    """

    print("\n.......................")
    time.sleep(1)
    print("..LOCKING ALL SYSTEMS..")
    time.sleep(3)
    print("...ATM HAS SHUT DOWN...")
    print(".......................")
    time.sleep(2)
    quit()

def requestLogin():
    """
    Handles the login and registration sequence
    """
    
    # ask whether student is new, only accepting 'yes'/'no' answers
    isNew = askQuestion("Are you a new user? (please enter yes/no): ", lambda x: x in ["yes", "no"]) == 'yes'

    # get user to input a correct username
    global username
    while True:
        # enter username, with the message being adjusted based on whether user is new or not
        username = askQuestion(f"Please enter {'a' if (isNew) else 'your'} username to {'register' if (isNew) else 'login'} (username must be alphanumeric and longer than 3 characters): ", 
            lambda x: x.isalnum() and len(x) >= 3, # username is only allowed if alphanumeric and longer than 3 characters
            case_sensitive=True)
        
        # if user is not new, check that the username exists.
        if (isNew and isUserPresent(username)):
            print("USERNAME ALREADY IN USE. PLEASE SELECT ANOTHER USERNAME.")
        elif (not isNew and not isUserPresent(username)):
            print("NO SUCH USERNAME FOUND. PLEASE ENTER ANOTHER USERNAME.")
        else:
            break
    
    # get user to input a pin
    global loaded_user, loaded_username
    loaded_username = username
    incorrect_count = 0
    MAX_INCORRECT = 5
    while True:
        pin = int(askQuestion("Please enter a PIN (your 4 digit numeric identifier): ", lambda x: x.isnumeric() and len(x) == 4))

        if (isNew):
            res = addUser(username, pin)
            print("Username and PIN registered successfully!\n")

            loaded_user = loadUser(username)
            break
        else:
            res = loadUser(username)
            if (res['pin'] != hashSha256(str(pin))):
                if (incorrect_count == MAX_INCORRECT):
                    print(f"INCORRECT PIN ENTERED {MAX_INCORRECT} TIMES. MALICIOUS ACTIVITY SUSPECTED. COMMENCING LOCKOUT...")
                    quitProgram()
                elif (incorrect_count >= MAX_INCORRECT - 3):
                    print(f"INCORRECT PIN. YOU WILL BE LOCKED OUT OF THE SYSTEM IN {MAX_INCORRECT - incorrect_count} ATTEMPT{'' if MAX_INCORRECT - incorrect_count == 1 else 'S'}. PLEASE RETRY")
                else:
                    print("INCORRECT PIN. PLEASE RETRY.")
                incorrect_count += 1

            else:
                print(f"Login successful!\n")
                loaded_user = res
                break


def mainMenu():
    input("Press ENTER to proceed to the menu screen...")

    while True:
        cls()
        MainMenuMessage = f"""
Please enter the number of the corresponding action you would like to execute:
    (1) Check Balance
    (2) Withdraw
    (3) Deposit 
    (4) Exit 
"""
        print(MainMenuMessage)

        action = int(askQuestion("Input wanted action (1, 2, 3, 4): ", lambda x: x in ['1', '2', '3', '4']))
        
        if (action == 1):
            checkBalance()
        elif (action == 2):
            withdraw()
        elif (action == 3):
            deposit()
        elif (action == 4):
            print("\nYOU HAVE REQUESTED TO QUIT. SHUTTING DOWN")
            time.sleep(2)
            break

        input("\nPress any key to return to menu... ")
    quitProgram()

def checkBalance():
    print("Your current balance is: " + formatBalance(loaded_user['balance']))

def withdraw():
    if loaded_user['balance'] == 0:
        print("\nYour balance is currently $0.00. You must have funds in your account to begin a withdrawal transaction")
        return
    
    # enter withdraw amount
    print(f"\nInitiating withdrawal. To cancel the transaction, please enter 'CANCEL' into the input bar. Please note:")
    print(f"   • Your withdrawal amount must be a multiple of 5 in order for the ATM to provide you with bank notes. \n   • You may not withdraw an amount greater than your current balance ({formatBalance(loaded_user['balance'])})\n")
    def answer_validator(input):
        if (input == "CANCEL"):
            return "CANCEL"
        if (not input.isnumeric()):
            return "ERROR: INPUT MUST CONSIST ONLY OF NUMERIC DIGITS. PLEASE ENTER A VALID SUM."
        input = int(input)
        if input % 5 != 0:
            return "ERROR: INPUT MUST BE A MULTIPLE OF 5. PLEASE ENTER A VALID SUM"
        elif input <= 0:
            return "ERROR: INPUT MUST BE ABOVE ZERO. PLEASE ENTER A VALID SUM."
        elif input > loaded_user['balance']:
            return "ERROR: INPUTTED SUM EXCEEDS BALANCE. PLEASE ENTER A LOWER SUM."
        return "" # correct

    amount = askQuestionAdvanced("Enter withdrawal amount: ", answer_validator)
    if (amount == None):
        # user wishes to cancel, exit transaction 
        print("Transaction has been cancelled.")
        return
    else:
        amount = int(amount)

    # do transaction and print receipt.
    loaded_user['balance'] -= amount
    saveCurrentUserState()

    # print acknowledgement
    print(f"\nYour funds have been withdrawn. Your new balance is: {formatBalance(loaded_user['balance'])}. A receipt is available for you to view. Thank you for using the BBC ATM!")
    printReceipt(loaded_username, 'WITHDRAWAL', formatBalance(amount), formatBalance(loaded_user['balance']))

def deposit():
    # enter deposit amount
    print(f"\nInitiating deposit. To cancel the transaction, please enter 'CANCEL' into the input bar. Please note:")
    print(f"   • Only bank notes are accepted for deposit, and so your deposit amount must be a multiple of 5. \n   • Your current balance is: {formatBalance(loaded_user['balance'])}\n")

    def answer_validator(input):
        if (input == "CANCEL"):
            return "CANCEL"
        if (not input.isnumeric()):
            return "ERROR: INPUT MUST BE NUMERIC. PLEASE ENTER A VALID SUM."
        input = int(input)
        if input <= 0:
            return "ERROR: INPUT MUST BE ABOVE ZERO. PLEASE ENTER A VALID SUM."
        elif input % 5 != 0:
            return "ERROR: INPUT MUST BE A MULTIPLE OF 5. PLEASE ENTER A VALID SUM."
        return "" # correct

    amount = askQuestionAdvanced("Enter deposit amount: ", answer_validator)
    if (amount == None):
        # user wishes to cancel, exit transaction 
        print("You have requested to cancel. Exiting to menu...")
        return
    else:
        amount = int(amount)
    # do transaction and print receipt.
    loaded_user['balance'] += amount
    saveCurrentUserState()

    print(f"\nYour funds have been deposited. Your new balance is: {formatBalance(loaded_user['balance'])}. A receipt is available for you to view.")
    printReceipt(loaded_username, 'DEPOSIT', formatBalance(amount), formatBalance(loaded_user['balance']))

def loadUser(username):
    with open('users.json') as file:
        users = json.load(file)
        if username in users:
            return users[username]
        else:
            return None
        
def addUser(username, pin, balance=0):
    # hash the pin
    hashed_pin = hashSha256(str(pin))
    with open('users.json', 'r+') as file:
        users = json.load(file)
        if username in users:
            return False
        else:
            users[username] = {'pin': hashed_pin, 'balance':balance}
            person_json = json.dumps(users)
            file.seek(0)
            file.write(person_json)
            file.truncate()
            return True

def isUserPresent(username):
    with open('users.json', 'r+') as file:
        users = json.load(file)
        if username in users:
            return True

def hashSha256(string):
    return hashlib.sha256(string.encode('utf-8')).hexdigest()

def saveCurrentUserState():
    """
    Records the data of the currently loaded user to a file.
    """
    with open('users.json', 'r+') as file:
        users = json.load(file)
        users[loaded_username] = loaded_user
        #print("SAVING STATE: ", loaded_user, loaded_username, json.dumps(users))
        file.seek(0)
        file.write(json.dumps(users))
        file.truncate()

def formatBalance(balance):
    return "$" + "{:.2f}".format(int(balance))

def main():
    showTitleScreen()
    print(f"\nWelcome to the Big Bank Corporation ATM!")
    time.sleep(0.5)
    
    # print line break
    print("\n")

    requestLogin()
    mainMenu()

main()




    # while True:
    #     global username

    #     # enter username, with the message being adjusted based on whether user is new or not
    #     username = askQuestion(f"Please enter {'a' if (answer == 'yes') else 'your'} username to {'register' if (answer == 'yes') else 'login'} (username must be alphanumeric and longer than 3 characters): ", 
    #         lambda x: x.isalnum() and len(x) >= 3, # username is only allowed if alphanumeric and longer than 3 characters
    #         case_sensitive=True)
        
    #     if (answer == "yes" and isUserPresent(username)):
    #         print("This username is already in use. Please pick another one.")
    #         continue
    #     else:
    #         pin = int(askQuestion("Please enter a PIN (your 4 digit numeric identifier): ", lambda x: x.isnumeric() and len(x) == 4))

    #     if (answer == "yes"):
    #         res = addUser(username, pin)

    #         if res == True: # username is valid
    #             print("Username and PIN registered successfully.")
    #             break
    #     else:
    #         res = loadUser(username)

    #         # check pin is correct
    #         if (res == None): # user doesnt exist
    #             print("No username with that name is found. Please try again.")
    #         elif (res['pin'] != pin):
    #             print("Incorrect pin. Please re-enter pin.")
    #         else:
    #             print(f"Username found!")
    #             global loaded_user, loaded_username
    #             loaded_user = res
    #             loaded_username = username
    #             break