# Name: Mohammed Elsayed
# AndrewID: mohammee
import requests
import pickle
import uuid
import os
import tkinter as tk
from tkinter import DISABLED, NORMAL, messagebox
import customtkinter
from functions import *
from PIL import Image,ImageTk
import enchant #only used to check if an entered word is a valid english word or not
class InstagramAccount:
    def __init__(self,username,password):
        """Initialises the values of username and password to the values passed,
           initialises the headers dictionary sent with the HTTP requests, starts
           a new network session, and creates a DM Handler object

        Args:
            username (String): the username of the instagram account
            password (String): the password of the instagram account
        """
        self.__username=username
        self.__password=password
        self.__headers={"X-IG-Capabilities": "3wI=",
                        "User-Agent": "Instagram 109.0.0.18.124 Android (28/9; 420dpi; 1080x2324; samsung; SM-A705FN; a70q; qcom; en_GB; 170693940)",
                        "Accept-Language": "en-Qa",
                        "content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
        self.__session=requests.session()
        self.__DMHandler=DMHandler(self.__headers,self.__session)
    def login(self):
        """Updates the network session cookies if a cookies.dat file exists in
           the current working directory and sends a login request if not

        Returns:
            Boolean: True if updating the session cookies from an existing cookies file
                     was successful or if the login attempt was successful and false
                     otherwise
        """
        #if there is already a cookies.dat file in the current working directory
        #we can update the session cookies instead of logging in again
        if("cookies.dat" in os.listdir()):
            with open("cookies.dat","rb") as cookiesFile:
                #load the cookies object from the cookies.dat file using pickle
                self.__session.cookies.update(pickle.load(cookiesFile))
                return True
        #generate a random uuid4 to send with the login HTTP request
        uID=str(uuid.uuid4())
        #the post data sent with the post login HTTP request
        postData = {"_csrftoken":"missing",
                    "username":self.__username,
                    "password":self.__password,
                    "login_attempt_count":"0",
                    "device_id":uID}
        #send the loginRequest to the instagram server with the appropriate 
        #headers and post data
        loginRequest=self.__session.post("https://i.instagram.com/api/v1/accounts/login/",headers=self.__headers,data=postData)
        #if our login attempt was successful
        if '{"logged_in_user":{"' in loginRequest.text:
            #create a new cookies.dat file
            with open("cookies.dat","wb") as cookiesFile:
                #save the session cookies to the created cookies.dat file 
                pickle.dump(loginRequest.cookies,cookiesFile)
            return True
        return False
    def getUsername(self):
        """getter method that gets self.__username

        Returns:
            String: self.__username
        """
        return self.__username
    def getPassword(self):
        """getter method that gets self.__password

        Returns:
            String: self.__password
        """
        return self.__username
    def getHeaders(self):
        """getter method that gets self.__headers

        Returns:
            Dicionary: self.__headers
        """
        return self.__headers
    def getSession(self):
        """getter method that gets self.__session

        Returns:
            Session Object: self.__session
        """
        return self.__session
    def getDMHandler(self):
        """getter method that gets self.__DMHandler

        Returns:
            DMHandler Object: self.__DMHandler
        """
        return self.__DMHandler
    def __str__(self):
        """Magic function to return the state of the object

        Returns:
            String: a message that has the values (states) of the username and 
                    password attributes
        """
        return f"Username: {self.__username} Password: {self.__password}"
class DMHandler:
    def __init__(self,headers,session):
        """an initialiser that initialises the values of headers and session to
           the values provided to be able to use them in sending HTTP DM requests

        Args:
            headers (dictionary): a dictionary of the headers to be sent with the 
                                  DM requests
            session (session object): the active network session to be used in 
                                      sending the HTTP DM requests
        """
        self.__headers=headers
        self.__session=session
    def getPendingDMRequests(self):
        """Gets the pending DM requests 

        Returns:
            List: a list of all the pending DM requests
        """
        #a list of all the pending DM requests (stores the thread IDs of the pending chats)
        pendingDMRequests=[]
        #send the get pending DM requests to the instagram server with the appropriate headers
        getPendingDMRequestsRequest=self.__session.get("https://i.instagram.com/api/v1/direct_v2/pending_inbox/?use_unified_inbox=true",headers=self.__headers)
        #for every pending request in the response
        for i in range(0,len(getPendingDMRequestsRequest.json()["inbox"]["threads"])):
            #append the thread ID of the pending chat to the list of pendingDMRequests
            pendingDMRequests.append(getPendingDMRequestsRequest.json()["inbox"]["threads"][i]["thread_id"])
        #return the list of the thread IDs of the pending chats
        return pendingDMRequests
    def approvePendingDMRequest(self,threadID):
        """Approves the pending DM request by threadID

        Args:
            threadID (String): the thread ID of the pending chat to be accepted
        Returns:
            Boolean: true if the DM request was approved successfully and false
                     otherwise 
        """
        #send a request to approve the pending chat request
        approvePendingRequest=self.__session.post(f"https://i.instagram.com/api/v1/direct_v2/threads/{threadID}/approve/",headers=self.__headers)
        #if the chat request was approved successfully
        if '"status":"ok"' in approvePendingRequest.text: return True
        else: return False
    def getDMThreads(self,processedUsernames=[]):
        """gets the DM chats (threads) in the chat page

        Args:
            processedUsernames (list, optional): a list of the usernames we already
                                                 processed (used to avoid processing the 
                                                 same thread multiple times). Defaults to [].

        Returns:
            List: a list of tuples of the form (username,threadID)
        """
        #a list of the usernames and thread IDs of the DM chats that has the form 
        #(username,threadID)
        DMThreads=[]
        #send a request to get the DM chats
        getDMRequests=self.__session.get("https://i.instagram.com/api/v1/direct_v2/inbox/?use_unified_inbox=true&persistentBadging=true",headers=self.__headers)
        #for every thread (chat) in the response
        for i in range(0,len(getDMRequests.json()["inbox"]["threads"])):
            #get the username,threadID,and message type
            username=getDMRequests.json()["inbox"]["threads"][i]["users"][0]["username"]
            threadID=getDMRequests.json()["inbox"]["threads"][i]["thread_id"]
            messageType=getDMRequests.json()["inbox"]["threads"][i]["items"][0]["item_type"]
            #if the username is in the usernames we already processed (added to the list of players)
            if(username in processedUsernames):
                #skip this username
                continue
            #if the message sent is not a text message
            if(messageType!="text"):
                #send a clarifying message to the player
                self.sendMessage(threadID,f'Unrecognized command {username}! entered message should be text')
                #delete the thread
                self.deleteThread(threadID)
                continue
            #get the text message sent
            message=getDMRequests.json()["inbox"]["threads"][i]["items"][0]["text"]
            #if the message is hey or hi
            if(message.lower()=="hey" or message.lower()=="hi"):
                #append the username and thread ID of the chat to the list of DMThreads
                DMThreads.append((username,threadID))
            else:
                #send a clarifying message to the player
                self.sendMessage(threadID,f'Unrecognized command {username}! please send "hi" or "hey" to join the game session')
                #delete the thread
                self.deleteThread(threadID)
        #return the list of the usernames and thread IDs of the DM chats
        return DMThreads
    def getThreadItems(self,threadID):
        """Gets the new messages (thread items) in a certain chat by threadID

        Args:
            threadID (String): the threadID of the chat we wish to get the thread
                               items of

        Returns:
            List: a list of the messages (thread items) in the chat with the threadID passed
        """
        #a list of the messages (thread items) in the chat with the passed thread ID
        #of the form (threadID,Sender,message)
        threadItems=[]
        #send a request to get the thread items in the chat with the passed thread ID
        getThreadItemsRequest=self.__session.get(f"https://i.instagram.com/api/v1/direct_v2/threads/{threadID}/?use_unified_inbox=true",headers=self.__headers)
        #the username of the sender who sent the message
        sender=getThreadItemsRequest.json()["thread"]["users"][0]["username"]
        #for every message (thread item) in the chat 
        for i in range(0, len(getThreadItemsRequest.json()["thread"]["items"])):
            #the type of the message (can be text,image,or video)
            type=getThreadItemsRequest.json()["thread"]["items"][i]["item_type"]
            #if the message is a text message
            if type=="text":
                #get the content of the message
                query=getThreadItemsRequest.json()["thread"]["items"][i]["text"]
                #add the tuple of (threadID,sender,query) to the list
                threadItems.append((threadID,sender,query))
        return threadItems
    def sendMessage(self,threadID,message):
        """Sends the passed message in the chat with the passed threadID  

        Args:
            threadID (String): the thread ID of the chat the message will be sent in
            message (String): the message to be sent

        Returns:
            Boolean: True if the message was sent successfully and false otherwise
        """
        #generate a random uuid4 to send with the sendMessage request
        uID=str(uuid.uuid4())
        #post data to send with the sendMessage request
        postData={"action": "send_item",
                  "thread_id": threadID,
                  "text": message,
                  "device_id": uID}
        #send a request to send a message
        sendMessageRequest = self.__session.post("https://i.instagram.com/api/v1/direct_v2/threads/broadcast/text/",headers=self.__headers,data=postData)
        #if the message was sent successfully
        if '"status_code":"200"' in sendMessageRequest.text: return True
        else: return False
    def deleteThread(self,threadID):
        """Delete the chat with the threadID passed

        Args:
            threadID (String): the thread ID of the chat that will be deleted

        Returns:
            Boolean: True if the chat was deleted successfully and false otherwise
        """
        #send a request to delete the chat with the passed threadID
        deleteThreadRequest=self.__session.post(f"https://i.instagram.com/api/v1/direct_v2/threads/{threadID}/hide/",headers=self.__headers)
        #if the chat was deleted successfully
        if '"status":"ok"' in deleteThreadRequest.text: return True
        else: return False
class QRCodeWindow:
    def __init__(self,dmHandler):
        """Shows the window that has the QR code that redirects the players to 
           the instagram bot's profile
        Args:
            dmHandler (dmHandler object): the dmHandler object of the instagram account
        """
        #a dictionary of the form {username: [thread ID]}
        self.__players={}
        #a list to hold the indivdual game objects
        self.__individualGames=[]
        #a dm handler object
        self.__dmHandler=dmHandler
        self.__randomWord=""
        #initialise the QR code window
        windowWidth,windowHeight=[500,500]
        #set the default apperance mode (light, dark, or system)
        customtkinter.set_appearance_mode("dark")
        #set the default color theme
        customtkinter.set_default_color_theme("dark-blue")
        #create a new window object
        self.__QRCodeWindow=customtkinter.CTk()
        #set properties...
        self.__QRCodeWindow.title("QR Code")
        self.__QRCodeWindow.iconbitmap("icon.ico")
        self.__QRCodeWindow.geometry(f"{str(windowWidth)}x{str(windowHeight)}")
        self.__QRCodeWindow.resizable(False, False)
        #the backgroundImage of the QR Code window
        image=Image.open("QRCodeWindowImage.png").resize((windowWidth*2, int(windowHeight*1.8)))
        self.backgroundImage=ImageTk.PhotoImage(image)
        self.imageLabel=tk.Label(self.__QRCodeWindow,image=self.backgroundImage)
        self.imageLabel.place(relx=0.5,rely=0.49,anchor=tk.CENTER)
        self.checkWhoJoined()
        self.__QRCodeWindow.mainloop()
    def checkWhoJoined(self):
        """Periodic method that checks who joined the game session
        """
        #accept the pending DM requests
        acceptPendingRequests(self.__dmHandler)
        #call the getDMThreads function with the processed usernames as argument
        dmThreads=self.__dmHandler.getDMThreads(self.__players.keys())
        #for every thread (chat) in the chat page
        for thread in dmThreads:
            username=thread[0]
            threadID=thread[1]
            #if the username is not in the players dictionary
            if(username not in self.__players):
                #add the username:[threadID] pair to the dictionary
                self.__players[username]=[threadID]
                #send the new player the instructions on instagram
                self.__dmHandler.sendMessage(self.__players[username][0],"""
                    Welcome to the group wordle game!
                    As you wait for the other players to join, please read the following instructions
                    Instructions for the GUI game:
                    When the game starts, you and your teammates will have to guess a random 5-letter word in ONE ATTEMPT!.
                    Now how on earth are you going to guess a random 5-letter word in one attempt? i gotcha.
                    Each one of you has been assigned another random 5-letter word that they will have to guess individually.
                    If you guess the word correctly, you and your teammates get a (super helpful) clue that will (greatly) help you guess the original word.
                    Your guesses should be entered here on instagram (enter your first guess here when the game starts). Good luck!
                    Instructions for the individual game:
                    🟩: the random word you have been assigned contains this letter and it is in the right spot
                    🟨: the random word you have been assigned contains this letter but it is in the wrong spot
                    ⬛: the random word you have been assigned does not contain this letter""")
                #delete the player's chat
                self.__dmHandler.deleteThread(self.__players[username][0])
                #the remaining number of players is 5-the number of players we 
                #have in the dictionary
                remainingPlayers=5-len(self.__players)
                #if there are no remaining players
                if(remainingPlayers==0):
                    #generate a random 5 letter word
                    self.__randomWord=generate5LetterWord()
                    #assign each player another random 5 letter word based on the 
                    #random word generated
                    assignIndivdualWords(self.__randomWord,self.__players)
                    for player in self.__players:
                        #create individual game objects and append them to the 
                        #individualGames list
                        self.__individualGames.append(IndividualGame(self.__dmHandler,(player,self.__players[player][0]),self.__players[player][2],self.__players[player][1]))
                    #since we have 5 players in the game session, start the game
                    messagebox.showinfo("Starting the Game!",f"{thread[0]} joined the game! Let's start playing!")
                    self.__QRCodeWindow.destroy()
                else:
                    messagebox.showinfo("New Player Joined!",f"{thread[0]} joined the game! {remainingPlayers} more to go")
        self.__QRCodeWindow.after(10000,self.checkWhoJoined)
    def getPlayers(self):
        """Gets the players dictionary

        Returns:
            Dictionary: the players dictionary
        """
        return self.__players
    def getRandomWord(self):
        """Gets the random word generated

        Returns:
            String: the random word generated
        """
        return self.__randomWord
    def getIndividualGames(self):
        """Gets the individual games list

        Returns:
            List: the individual games list
        """
        return self.__individualGames
class IndividualGame:
    def __init__(self,dmHandler,chat,randomWord,indexOfLetterInOriginalWord):
        """initialises attributes

        Args:
            dmHandler (DMHandler Object): DMHandler Object used to handle DM 
                                          HTTP requests
            chat (tuple): tuple of the form (username,threadID)
            randomWord (String): the random word
            indexOfLetterInOriginalWord (String): the index of the letter in the
                                                  original word that the player
                                                  will be given as a hint 
                                                  
        """
        self.__dmHandler=dmHandler
        self.__username=chat[0]
        self.__threadID=chat[1]
        self.__randomWord=randomWord
        self.__indexOfLetterInOriginalLetter=indexOfLetterInOriginalWord
        #set the number of attempts for each indivdual game
        self.__attempts=6
        #two boolean variables to check if the player has guessed the word and 
        #if the game is done
        self.__guessed=False
        self.__gameDone=False
        #english dictionary (used to check if entered guess is an english word)
        self.__englishDictionary=enchant.Dict("en_US")
    def getGuess(self):
        """gets the player's guess

        Returns:
            String: the player's guess
        """
        try:
            threadItems=self.__dmHandler.getThreadItems(self.__threadID)
            guess=threadItems[0][2]
            return guess.lower()
        except:
            return None
    def processOneGuess(self):
        """Processes one entered guess on instagram
        """
        self.__guess=self.getGuess()
        if(self.__guess!=None):
            message=self.checkGuess()
            self.sendResult(message)
            self.__dmHandler.deleteThread(self.__threadID)
    def getAllOccurances(self,word,ch):
        """Gets all the indices at which ch occurs in word

        Args:
            word (String): the word we are looking for occurances of ch in
            ch (String): the ch we are searching for in the word

        Returns:
            List: the indices of word at which ch occurs
        """
        indices = []
        pos = word.find(ch)
        while pos != -1:
            indices.append(pos)
            pos = word.find(ch, pos + 1)
        return indices
    def checkGuess(self):
        """Checks an entered guess on instagram

        Returns:
            String: a message to be sent to the player based on his guess
        """
        message=["⬛"]*5
        messageSet=set()
        if(len(self.__guess)!=5):
            message="Invalid Guess! Your guess has to be a 5 letter word"
        elif(not self.__englishDictionary.check(self.__guess)):
            message="Invalid Guess! Your guess is not an english word"
        else:
            #the following code is adapted from the article https://www.practicepython.org/blog/2022/02/12/wordle.html with slight modifications
            for i,(randomWordCh,guessCh) in enumerate(zip(self.__randomWord,self.__guess)):
                if randomWordCh==guessCh:
                    message[i]="🟩"
                    messageSet.add(i)
            for i,guessCh in enumerate(self.__guess):
                if guessCh in self.__randomWord and message[i]!="🟩":
                    positions=self.getAllOccurances(self.__randomWord,guessCh)
                    for position in positions:
                        if position not in messageSet:
                            message[i]="🟨"
                            messageSet.add(position)
                            break
            self.__attempts-=1
        return ''.join(message)
    def sendResult(self,message):
        """Sends a message to the player based on his entered guess

        Args:
            message (String): the message to be sent to the player
        """
        self.__dmHandler.sendMessage(self.__threadID,message)
        if(message=="🟩🟩🟩🟩🟩"):
            suffixes={1:"st",
                      2:"nd",
                      3:"rd",
                      4:"th",
                      5:"th"}
            self.__guessed=True
            self.__gameDone=True
            self.__dmHandler.sendMessage(self.__threadID,f"Congrats. You guessed the word.")
            self.__dmHandler.sendMessage(self.__threadID,f'Hint: the {self.__indexOfLetterInOriginalLetter+1}{suffixes[self.__indexOfLetterInOriginalLetter+1]} letter of the word you and your teammates have to guess is "{self.__randomWord[self.__indexOfLetterInOriginalLetter]}"')
        else:
            if(self.__attempts==0):
                self.__gameDone=True
                self.__dmHandler.sendMessage(self.__threadID,f'You are out of attempts. The word was {self.__randomWord}')
            else:
                self.__dmHandler.sendMessage(self.__threadID,f"attempts left: {self.__attempts}")
    def getResult(self):
        """Gets the individual game result

        Returns:
            Boolean: the individual game result
        """
        return self.__guessed
    def isGameDone(self):
        """Gets the state of the individual game (done/not done)

        Returns:
            Boolean: the state of the individual game (done/not done)
        """
        return self.__gameDone
    def returnGuess(self):
        """Gets the player's guess

        Returns:
            String: the player's guess
        """
        return self.__guess
    def getUsername(self):
        """Gets the player's username

        Returns:
            String: the player's username
        """
        return self.__username
class MainWindow:
    def __init__(self,dmHandler,randomWord,individualGames,players):
        """initialise the values of the attributes and initialise the main 
           window
           

        Args:
            dmHandler (DMHandler object): the dmHandler object of the instagram account
            randomWord (String): the random word the players have to guess together
            individualGames (list): a list of individualGame objects
            players (dictionary): the players dictionary which has their threadIDs
                                  and their randomly generated words
        """
        #initialise attributes...
        self.__dmHandler=dmHandler
        self.__players=players
        self.__randomWord=randomWord
        self.__keepGettingUpdates=True
        self.__individualGames=individualGames
        print(self.__players)
        self.initialiseMainWindow()
    def initialiseMainWindow(self):
        """Initialises the main window with all its properties
        """
        #set the main window width and height
        windowWidth,windowHeight=[1000,700]
        #set the default apperance mode (light, dark, or system)
        customtkinter.set_appearance_mode("dark")
        #set the default color theme
        customtkinter.set_default_color_theme("dark-blue")
        #create a new window object
        self.__mainWindow=customtkinter.CTk()
        #set properties...
        self.__mainWindow.title("Group Wordle")
        self.__mainWindow.iconbitmap("icon.ico")
        #set the size of the main window
        self.__mainWindow.geometry(f"{str(windowWidth)}x{str(windowHeight)}")
        self.__mainWindow.resizable(False, False)
        #set the background image (by placing it inside a label)
        backgroundImageFile=Image.open("mainWindowBackgroundImage.png").resize((int(windowWidth*1.8), int(windowHeight*1.8)))
        backgroundImage=ImageTk.PhotoImage(backgroundImageFile)
        imageLabel=tk.Label(self.__mainWindow,image=backgroundImage)
        imageLabel.place(relx=0.5,rely=0.5,anchor=tk.CENTER)
        #create the left frame and "grid" it
        self.leftFrame=customtkinter.CTkFrame(self.__mainWindow,width=450,height=625,border_width=0)        
        self.leftFrame.grid(row=0, column=0, sticky="nswe",padx=25,pady=40)
        #open the "guess" image and place it inside the left frame
        guessImageFile=Image.open("guess.png").resize((int(self.leftFrame.winfo_width()*800),int(self.leftFrame.winfo_height()*800)))
        guessImage=ImageTk.PhotoImage(guessImageFile)
        guessImageLabel=tk.Label(self.leftFrame,image=guessImage,borderwidth=0)
        guessImageLabel.place(relx=0.6,rely=0.15,anchor=tk.CENTER)
        #create the guess text box and place it inside the left frame
        self.__enteredWord=customtkinter.CTkEntry(self.leftFrame,width=300,height=70,
                                                 placeholder_text="Enter Guess",
                                                 justify=tk.CENTER,
                                                 text_font=("comic sans SF",30))
        self.__enteredWord.place(relx=0.5,rely=0.45,anchor=tk.CENTER)
        #create the guess button and place it inside the left frame
        self.__guessButton=customtkinter.CTkButton(self.leftFrame,
                                                text="guess",
                                                border_width=1,
                                                width=180,
                                                height=50,
                                                text_font=("comic sans SF",25),
                                                state=DISABLED,
                                                command=self.checkGuess
                                                )
        self.__guessButton.place(relx=0.5,rely=0.7,anchor=tk.CENTER)
        #create the right frame and "grid" it
        self.rightFrame=customtkinter.CTkFrame(self.__mainWindow,width=450,height=625)
        self.rightFrame.grid(row=0, column=1, sticky="nswe", padx=20, pady=40)
        #open the "updates" image and place it inside the right frame
        updatesImageFile=Image.open("updates.png").resize((int(self.rightFrame.winfo_width()*850), int(self.rightFrame.winfo_height()*850)))
        updatesImage=ImageTk.PhotoImage(updatesImageFile)
        updatesImageLabel=tk.Label(self.rightFrame,image=updatesImage,borderwidth=0)
        updatesImageLabel.place(relx=0.57,rely=0.2,anchor=tk.CENTER)
        #create the updates text box and place it inside the right frame
        self.__updatesTextbox=customtkinter.CTkTextbox(self.rightFrame,width=420,height=440,text_font=("comic Sans SF",15,"bold"),state=DISABLED)
        self.__updatesTextbox.place(relx=0.5,rely=0.62,anchor=tk.CENTER)
        #add a hello message to the updates textbox and inform the players they
        #can enter their first guess on instagram
        self.__updatesTextbox.configure(state="normal")
        self.__updatesTextbox.insert("end",f'Hello {", ".join(self.__players.keys())}\n')
        self.__updatesTextbox.insert("end",f'Enter your first guess on Instagram!\n')
        self.__updatesTextbox.configure(state=DISABLED)
        self.getUpdates()
        self.__mainWindow.mainloop()
    def getRandomWord(self):
        """gets the random word the program generated

        Returns:
            String: self.__randomWord
        """
        return self.__randomWord
    def getIndividualWords(self):
        """gets the list of individual words 

        Returns:
            list: list of tuples of the form
                  (player,index of the original word assigned, random word assigned)
        """
        return [(player,self.__players[1],self.__players[2]) for player in self.__players]
    def getUpdates(self):
        """gets updates (guesses) on individual games
        """
        #if we still have an indivdual game going
        if(not self.__individualGames[0].isGameDone() or\
              not self.__individualGames[1].isGameDone() or\
              not self.__individualGames[2].isGameDone() or\
              not self.__individualGames[3].isGameDone() or\
              not self.__individualGames[4].isGameDone()):
            #for every individual game
            for individualGame in self.__individualGames:
                #if this game is not done
                if(not individualGame.isGameDone()):
                    #process the guess and store it
                    individualGame.processOneGuess()
                    guess=individualGame.returnGuess()
                    guessed=individualGame.getResult()
                    #if the user entered a guess but it is not the right word
                    if(guess!=None and not guessed):
                        self.__updatesTextbox.configure(state="normal")
                        self.__updatesTextbox.insert("end",f'{individualGame.getUsername()} guessed: {individualGame.returnGuess()}\n')
                        self.__updatesTextbox.configure(state=DISABLED)
                    #if the user entered a guess and it is the right word
                    elif(guess!=None and guessed):
                        self.__updatesTextbox.configure(state="normal")
                        self.__updatesTextbox.insert("end",f'{individualGame.getUsername()} guessed: {individualGame.returnGuess()} (Correct Guess!)\n')
                        self.__updatesTextbox.configure(state=DISABLED)
            self.__keepGettingUpdates=self.__mainWindow.after(10000,self.getUpdates)
        #if we are done with all the games
        else:
            self.__guessButton.configure(state=NORMAL)
            messagebox.showinfo("Guess the word","You are ready to guess the word!")
            self.__mainWindow.after_cancel(self.__keepGettingUpdates)
    def checkGuess(self):
        """Checks if the entered word in the GUI is the right word
        """
        guess=self.__enteredWord.get()
        if(guess.lower()==self.__randomWord):
            #show a congrats msg
            messagebox.showinfo("Congratulations","Congrats! You guessed the word correctly")
            #destroy the window 
            self.__mainWindow.destroy()
            #delete all the dm threads
            for player in self.__players:
                try:
                    self.__dmHandler.deleteThread(player[0])
                except:
                    pass
        else:
            messagebox.showinfo("sorry :(",f'sorry :( you did not guess the word correctly. The word was "{self.__randomWord}"')
            self.__mainWindow.destroy()
            for player in self.__players:
                try:
                    self.__dmHandler.deleteThread(player[0])
                except:
                    pass