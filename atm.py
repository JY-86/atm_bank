import time, os, sys, colorama
from urllib import request
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

username == ""

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def printTitleScreen():
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

#Receipt needs 
"""
- User's full name
- Date / Time of the transaction taken place
- Address of the ATM (School's address --> 419A Windsor Rd, Baulkham Hills NSW 2153) 
- Type of transaction (Withdrawal or Deposit)
- Amount being withdrawn / deposited
- Current Balance
"""

def PrintReceipt(UserFirstName, UserLastName, TransactionType, TransactionAmount, UserBalance): 
    
    ## Info needed to be shown in receipt 
    DateTime = datetime.now() #Returns the date and time of the transaction
    DateTimeString = DateTime.strftime("%d/%m/%Y %H:%M:%S")
    Address = "419A Windsor Rd, Baulkham Hills NSW 2153"

    ## Receipt components 
    ReceiptHeader = """
    ############################################
    #           (INSERT A BANK NAME)           #
    ############################################
    """
    ReceiptBody = f"""
    User: {UserFirstName} {UserLastName}
    
    Date and Time of Transaction: {DateTimeString}
    Address: {Address}

    Transaction Type: {TransactionType}
    Transaction Amount: {TransactionAmount}

    Current Balance: {UserBalance}

    Thank you for using the {BankName} ATM!
    """
   
    with open("receipt.txt", "w+") as f:
        pass


def askQuestion(message, answer_validator,  case_sensitive=True):
    """
    Repeatedly asks user for an input until input meets the correct requirements

    @param message: the message to print when asking user for input
    @param answer_validator: a function that returns whether an input is valid or not 
    @param case_sensitive: whether input should be treated as case sensitive
    @return: user's (valid) answer
    """

    # a short function that takes an input from user and makes it all lowercase if we do not care about case
    def getInput():
        answer = input(message)
        return answer if case_sensitive else answer.lower()
  
    user_input = getInput()

    # check if user wants to quit
    if (user_input == "q"):
        quitProgram()
    
    i = 0
    while(not answer_validator(user_input)): # continues running while answer not valid
        i += 1

        # print message saying that user's answer was invalid. If user fails more than 3 times, the message becomes more aggressive.
        if (i > 3):
            print("Please take this program seriously. Enter a correctly formatted response.")
        else:
            print("Response not recognised. Enter a correctly formatted response")

        # get new input
        user_input = getInput()

        # check if user wants to quit
        if (user_input == 'q'):
            quitProgram()

    # the answer is valid, return it
    return user_input

def quitProgram():
    """
    Quits the program (gracefully)
    """

    print("\nYou have requested to quit. Shutting down...")
    time.sleep(2)
    quit()

def requestLogin():
    """
    Handles the login and registration sequence
    """
    
    # ask whether student is new, only accepting 'yes'/'no' answers
    answer = askQuestion("Are you a new user (please input yes/no): ", lambda x: x in ["yes", "no"])

    while True:
        global username

        # enter username, with the message being adjusted based on whether user is new or not
        username = askQuestion(f"Please enter {'a' if (answer == 'yes') else 'your'} username to {'register' if (answer == 'yes') else 'login'} (username must be alphanumeric and longer than 3 characters): ", 
            lambda x: x.isalnum() and len(x) >= 3, # username is only allowed if alphanumeric and longer than 3 characters
            case_sensitive=True)

        if (answer == "yes"):
            global isNew
            isNew = True

            # send post request to server attempting to register the username
            res = requests.post(getRouteUrl("/register"), json={"username":username})

            if res.status_code == 200: # username is valid
                print("Username registered successfully.")
                break
            elif res.status_code == 400: # username in use
                print("This username is already in use. Please pick another one.")
            else: # some other server error, like an internal error
                print("Unfortunately the request to register the username failed. Please try again.")
        else:
            # send post request to server to check whether user with this username exists
            res = requests.post(getRouteUrl("/login"), json={"username":username})

            if (res.status_code == 200): # user exists
                print(f"Username found!")
                break
            elif (res.status_code == 400): # user does not exist
                print("No username with that name is found. Please try again.")
            else: # server encountered some other error
                print("We counld not log you in at this time. Please try again.")


def main():
    
    requestLogin()


main()