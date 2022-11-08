Group Wordle

A word-guessing game where 5 players have to guess a randomly generated 5-letter word in one attempt 
by playing 5 individual word-guessing games on instagram

How to run the project:
1) ensure that you have all the required libraries installed. This can be done by running the command "pip install -r requirements.txt" in CMD
2) open the main.py file and type the username and password of the instagram account you will use for the individual games
3) run main.py

IMPORTANT NOTE: THE LOGIN FUNCTION DOES NOT HANDLE CHALLENGES (2FA), SO MAKE SURE THE ACCOUNT YOU ARE USING HAS 2FA DISABLED. it is better if you create a new 
instagram account and use it rather than use an existing instagram account.

if you face issues with logging in, you have two options:
1) use the default instagram account for the game (username: groupwordle password: Bot1223)
2) move the cookies.dat file from the optional cookies folder to the directory classes.py,functions.py, and main.py are in to skip the login step
