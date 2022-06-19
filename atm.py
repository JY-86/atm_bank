# import necessary modules
from argparse import Action
import time, os, sys, colorama
from urllib import request
from colorama import Fore, Back, Style
import json
import datetime
import hashlib

# initialise modules
colorama.init(autoreset=True)

# global variables to store active user
loaded_username = ""
loaded_user = {}
RECEIPT_FILE = "receipt.txt"

def cls():
    """
    Clears terminal screen by issuing the correct command for current OS
    """
    os.system('cls' if os.name=='nt' else 'clear')
    
def slowType(str, interval):
    """
    Prints out terminal text with a delay between printing each letter 

    @param str: the string to print
    @param interval: time to wait before printing next letter
    """

    for letter in str:
        sys.stdout.write(letter)
        sys.stdout.flush()
        time.sleep(interval)

def showTitleScreen():
    """
    Prints out welcome logo
    """

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

    # print bank logo line by line with a small delay between each line
    for line in BANK_LOGO:
        print(f"{line}")
        time.sleep(0.05)
    
    # sleep to allow the user to observe the sheer beauty of the logo.
    time.sleep(0.5)

def printReceipt(username, transactionType, amount, balance): 
    """
    Prints out a receipt to a file

    @param username: the name of the user to put on the receipt
    @param transactionType: type of transaction that has occurred
    @param amount: the amount deposited or withdrawn from the user's account
    @param balance: current balance of the user's account
    """

    # get info to show in the receipt
    date = datetime.datetime.now().strftime("%d/%m/%Y")
    time = datetime.datetime.now().strftime("%H:%M:%S")
    address = "419A Windsor Rd, Baulkham Hills NSW 2153"

    
    # generate basic receipt template
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

    # close the receipt box by appending '|' to the end of each line
    newReceipt = [receipt[0]]
    for line in receipt[1:]:
        # pad the line with empty spaces to the correct length, add ending character, and append to receipt array
        newReceipt.append(line.ljust(61, " ") + "|")

    # convert receipt from array back into string
    newReceipt = "\n" + "\n".join(newReceipt)

    # write receipt to file
    with open(RECEIPT_FILE, "w", encoding="utf-8") as f:
        f.write(newReceipt)

# a short function that takes an input from user and makes it all lowercase if we do not care about case
def getInput(message, case_sensitive):
    """
    Takes an input from user and makes it all lowercase if case insensitive

    @param message: message to print when requesting input
    @param case_sensitive: if True, leaves input as is. if False, converts text to all lowercase.
    @return: user response with case adjusted
    """

    answer = input(message)
    return answer if case_sensitive else answer.lower()

def askQuestion(message, answer_validator,  case_sensitive=True):
    """
    Repeatedly asks user for an input until input meets the correct requirements, and quits program if
    too many incorrect inputs entered

    @param message: the message to print when asking user for input
    @param answer_validator: a boolean function that returns whether an input is valid or not
    @param case_sensitive: whether input should be treated as case sensitive
    @return: user's (valid) answer
    """

    # number of incorrect inputs before program quits
    LOCKOUT_NUM = 5
    
    user_input = getInput(message, case_sensitive)
    
    i = 0
    while(not answer_validator(user_input)): # continues running while answer not valid
        i += 1

        # print message saying that user's answer was invalid. If user fails too many times, the program quits.
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
    Will only accept answer if the correct string is generated by the validator, otherwise prints the validated message.
    Can also cancel the question.

    @param message: the message to print when asking user for input
    @param answer_validator: a function that returns whether a string indicating message to print, or whether to cancel or accept an answer
    @param correct_response: validator response which should return given input
    @param cancel_response: validator response which should quit the question loop
    @param case_sensitive: whether input should be treated as case sensitive
    @return: user's (valid) answer, or None if question cancelled
    """

    user_input = getInput(message, case_sensitive)
    i = 0
    response = answer_validator(user_input)

    while(response != correct_response and response != cancel_response): # continues running while answer not valid and not cancelled
        i += 1
        print(response) # print validator response

        # get new input and generate validator response
        user_input = getInput(message, case_sensitive)
        response = answer_validator(user_input)

    # return appropriate message based on whether user cancelled or input a valid answer
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
    username = ""
    while True:
        # enter username, with the message being adjusted based on whether user is new or not
        username = askQuestion(f"Please enter {'a' if (isNew) else 'your'} username to {'register' if (isNew) else 'login'} (username must be alphanumeric and longer than 3 characters): ", 
            lambda x: x.isalnum() and len(x) >= 3, # username is only allowed if alphanumeric and longer than 3 characters
            case_sensitive=True)
        
        # if user is new, check that username not already taken
        if (isNew and isUserPresent(username)):
            print("USERNAME ALREADY IN USE. PLEASE SELECT ANOTHER USERNAME.")
        elif (not isNew and not isUserPresent(username)): # if user is not new, check that username exists
            print("NO SUCH USERNAME FOUND. PLEASE ENTER ANOTHER USERNAME.")
        else: # valid username
            break 
    
    ## get user to input a pin

    global loaded_user, loaded_username
    loaded_username = username

    # variables to track how many times pin has been inputted incorrectly. If MAX_INCORRECT reached, program quits.
    incorrect_count = 0
    MAX_INCORRECT = 5

    while True:
        # ask for a valid pin
        pin = int(askQuestion("Please enter a PIN (your 4 digit numeric identifier): ", lambda x: x.isnumeric() and len(x) == 4))

        if (isNew): 
            # add user
            res = addUser(username, pin)
            print("Username and PIN registered successfully!\n")

            # load user into global variables
            loaded_user = loadUser(username)
            break
        else:
            res = loadUser(username) # load given user

            if (res['pin'] != hashSha256(str(pin))): # inputted pin hash does not match with the hashed pin in the file.

                # print appropriate response based on number of attempts to input pin
                if (incorrect_count == MAX_INCORRECT):
                    print(f"INCORRECT PIN ENTERED {MAX_INCORRECT} TIMES. MALICIOUS ACTIVITY SUSPECTED. COMMENCING LOCKOUT...")
                    quitProgram()
                elif (incorrect_count >= MAX_INCORRECT - 3):
                    print(f"INCORRECT PIN. YOU WILL BE LOCKED OUT OF THE SYSTEM IN {MAX_INCORRECT - incorrect_count} ATTEMPT{'' if MAX_INCORRECT - incorrect_count == 1 else 'S'}. PLEASE RETRY")
                else:
                    print("INCORRECT PIN. PLEASE RETRY.")

                # update number of incorrect attempts
                incorrect_count += 1

            else: # pin correct, and login successful
                print(f"Login successful!\n")

                # assign user to global variables so other parts of program can use data.
                loaded_user = res
                break


def mainMenu():
    """
    Operates the main menu screen
    """

    # make sure user is ready to enter menu
    input("Press ENTER to proceed to the menu screen...")

    # main menu loop
    while True:
        # clear screen
        cls()

        MainMenuMessage = f"""
Please enter the number of the corresponding action you would like to execute:
    (1) Check Balance
    (2) Withdraw
    (3) Deposit 
    (4) Exit 
"""
        print(MainMenuMessage)

        # get the wanted action from the user
        action = int(askQuestion("Input wanted action (1, 2, 3, 4): ", lambda x: x in ['1', '2', '3', '4']))
        
        # call appropriate function based on wanted action
        if (action == 1):
            checkBalance()
        elif (action == 2):
            withdraw()
        elif (action == 3):
            deposit()
        elif (action == 4):
            # break the loop so program can quit.
            print("\nYOU HAVE REQUESTED TO QUIT. SHUTTING DOWN")
            time.sleep(2)
            break
        
        # this runs after an operation (other than exit) has finished, allowing the user to input another action
        input("\nPress any key to return to menu... ")
    
    # if loop is broken, the program quits.
    quitProgram()

def checkBalance():
    """
    Prints balance of currently loaded user
    """

    print("Your current balance is: " + formatBalance(loaded_user['balance']))

def withdraw():
    """
    Withdraws funds from the loaded user's account
    """

    # check if balance if zero. If it is, user cannot withdraw funds.
    if loaded_user['balance'] == 0:
        print("\nYour balance is currently $0.00. You must have funds in your account to begin a withdrawal transaction")
        return
    
    # print instructions for user
    print(f"\nInitiating withdrawal. To cancel the transaction, please enter 'CANCEL' into the input bar. Please note:")
    print(f"   • Your withdrawal amount must be a multiple of 5 in order for the ATM to provide you with bank notes. \n   • You may not withdraw an amount greater than your current balance ({formatBalance(loaded_user['balance'])})\n")
    
    # define the answer validator that determines whether a user input is valid, and if not what message to print to user.
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

    # ask user for amount to withdraw, ensuring answer is valid
    amount = askQuestionAdvanced("Enter withdrawal amount: ", answer_validator)

    if (amount == None):
        # user wishes to cancel, exit transaction 
        print("\nTransaction has been cancelled.")
        return
    else:
        # convert amount to integer
        amount = int(amount)

    # do transaction and save user data to file.
    loaded_user['balance'] -= amount
    saveCurrentUserState()

    # print acknowledgement of transaction and receipt
    print(f"\nYour funds have been withdrawn. Your new balance is: {formatBalance(loaded_user['balance'])}. A receipt is available for you to view.")
    print("Thank you for using the BBC ATM!")
    printReceipt(loaded_username, 'WITHDRAWAL', formatBalance(amount), formatBalance(loaded_user['balance']))

def deposit():
    """
    Deposits funds into the loaded user's account
    """

    # print deposit instructions
    print(f"\nInitiating deposit. To cancel the transaction, please enter 'CANCEL' into the input bar. Please note:")
    print(f"   • Only bank notes are accepted for deposit, and so your deposit amount must be a multiple of 5. \n   • Your current balance is: {formatBalance(loaded_user['balance'])}\n")

    # define the answer validator that determines whether a user input is valid, and if not what message to print to user.
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

    # ask user for amount to deposit, ensuring answer is valid
    amount = askQuestionAdvanced("Enter deposit amount: ", answer_validator)

    if (amount == None):
        # user wishes to cancel, exit transaction 
        print("\nTransaction has been cancelled.")
        return
    else:
        amount = int(amount)

    # do transaction and write to file
    loaded_user['balance'] += amount
    saveCurrentUserState()

    # print acknowledgement message to user, and the receipt
    print(f"\nYour funds have been deposited. Your new balance is: {formatBalance(loaded_user['balance'])}. A receipt is available for you to view.")
    print("Thank you for using the BBC ATM!")
    printReceipt(loaded_username, 'DEPOSIT', formatBalance(amount), formatBalance(loaded_user['balance']))

def loadUser(username):
    """
    Returns data associated with a given user
    """

    with open('users.json') as file:
        # load users from file into dictionary
        users = json.load(file)

        # return data if user is present
        if username in users:
            return users[username]
        else:
            return None
        
def addUser(username, pin, balance=0):
    """
    Adds a new user to user file
    
    @param username: username to register
    @param pin: pin to register
    @param balance: balance user starts with
    @return: whether registration successful
    """

    # hash the pin
    hashed_pin = hashSha256(str(pin))

    with open('users.json', 'r+') as file:
        # load users into dictionary
        users = json.load(file)

        if username in users: # if username already present, cannot register and so return False
            return False
        else:
            # add new user to dictionary and create JSON representation
            users[username] = {'pin': hashed_pin, 'balance':balance}
            person_json = json.dumps(users)

            # overwrite previous file
            file.seek(0)
            file.write(person_json)
            file.truncate()

            # return that write was successful
            return True

def isUserPresent(username):
    """
    Checks if user is present in user file
    
    @param username: username to check
    @return: whether user is present in file
    """

    with open('users.json', 'r+') as file:
        # load all users into dictionary
        users = json.load(file)

        # check if username is in dictionary
        if username in users:
            return True

def hashSha256(string):
    """
    Hashes a string

    @param string: the string to be hashed
    @return: the sha256 hash of the string
    """

    return hashlib.sha256(string.encode('utf-8')).hexdigest()

def saveCurrentUserState():
    """
    Records the data of the currently loaded user to a file.
    """

    with open('users.json', 'r+') as file:
        # load all users into dictionary
        users = json.load(file)

        # either update current user or create new user in dictionary
        users[loaded_username] = loaded_user
        #print("SAVING STATE: ", loaded_user, loaded_username, json.dumps(users))

        # overwrite the previous file with new user dictionary
        file.seek(0)
        file.write(json.dumps(users))
        file.truncate()

def formatBalance(balance):
    """
    Converts a number into a string in money format, with two decimal places and a dollar sign
    """
    return "$" + "{:.2f}".format(int(balance))

def main():
    """
    Main control flow of program
    """

    cls()
    
    # show logo and print welcome
    showTitleScreen()
    print(f"\nWelcome to the Big Bank Corporation ATM!")
    time.sleep(0.5)
    print("\n")

    # make user login or register
    requestLogin()

    # once user is loaded, enter main menu of program
    mainMenu()

main()