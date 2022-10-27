import requests
import pickle
import uuid
import os
import tkinter as tk
from tkinter import DISABLED, messagebox
from functions import *
import time
import enchant #only used to check if an entered word is a valid english word or not
class IndividualGame:
    def __init__(self,dmHandler,chat,randomWord,indexOfLetterInOriginalWord):
        """initialises attributes

        Args:
            dmHandler (DMHandler Object): an object to handle DM
            chat (tuple): tuple of the form (username,threadID)
            randomWord (String): the random word 
        """
        self.__dmHandler=dmHandler
        self.__username=chat[0]
        self.__threadID=chat[1]
        self.__randomWord=randomWord
        self.__indexOfLetterInOriginalLetter=indexOfLetterInOriginalWord
        self.__attempts=6
        self.__guessed=False
        self.__gameDone=False
        self.__englishDictionary=enchant.Dict("en_US")
    def processOneGuess(self):
        self.__guess=self.getGuess()
        if(self.__guess!=None):
            message=self.checkGuess()
            self.sendResult(message)
            self.__dmHandler.deleteThread(self.__threadID)
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
    def getAllOccurances(self,word,ch):
        indices = []
        pos = word.find(ch)
        while pos != -1:
            indices.append(pos)
            pos = word.find(ch, pos + 1)
        return indices
    def checkGuess(self):
        message=["⬛"]*5
        messageSet=set()
        if(len(self.__guess)!=5):
            message="Invalid Guess! Your guess has to be a 5 letter word"
        elif(not self.__englishDictionary.check(self.__guess)):
            message="Invalid Guess! Your guess is not an english word"
        else:
            #the following code is adapted from the article https://www.practicepython.org/blog/2022/02/12/wordle.html
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
        return self.__guessed
    def isGameDone(self):
        return self.__gameDone
    def returnGuess(self):
        return self.__guess
    def getUsername(self):
        return self.__username
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
        #Send the get pending DM requests to the instagream server  
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
        #a list of the usernames and thread IDs of the DM chats
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
            threadID (String): the thread of the chat we wish to get the thread
                               items of

        Returns:
            List: a list of the messages (thread items) in the chat with the threadID passed
        """
        #a list of the messages (thread items) in the chat with the passed thread ID
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
class InstagramAccount:
    def __init__(self,username,password):
        """Initialises the values of username and password to the values passed,
           initialises the headers dictionary sent with the HTTP requests, and 
           starts a new network session

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
        """Update the session cookies if a cookies.dat file exists in the current
           working directory or send a login request

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
    def getDMHandler(self):
        """getter method that gets self.__DMHandler

        Returns:
            DMHandler Object: self.__DMHandler
        """
        return self.__DMHandler
    def __str__(self):
        return f"Username: {self.__username} Password: {self.__password}"
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
        self.__QRCodeWindow=tk.Tk()
        self.__QRCodeWindow.title("QR Code")
        self.__QRCodeWindow.iconbitmap("icon.ico")
        #the width and height of the QR code window
        windowWidth,windowHeight=[500,500]
        #get the current screen's width and height in pixels
        screenWidth,screenHeight=[self.__QRCodeWindow.winfo_screenwidth(),
                                  self.__QRCodeWindow.winfo_screenheight()]
        #calculate the x and y coordinates of the center of the screen
        xCenter=(screenWidth//2)-(windowWidth//2)
        yCenter=(screenHeight//2)-(windowHeight//2)
        #set the size and where the window should open
        self.__QRCodeWindow.geometry(f"{str(windowWidth)}x{str(windowHeight)}+{str(xCenter)}+{str(yCenter)}")
        #variable to hold the background image
        backgroundImage=tk.PhotoImage(file="backgroundImageQRCodeWindow.png")
        #canvas that will hold the background image, text, and QR code
        canvas=tk.Canvas(self.__QRCodeWindow,width=windowWidth,height=windowHeight,highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0,0,image=backgroundImage,anchor="nw")
        canvas.create_text(windowWidth//1.95,windowHeight//12,text="Scan the following QR Code ",font=("Comic Sans MS",25,"bold"))
        QRCodeImage=tk.PhotoImage(file="botQRCode.png")
        canvas.create_image(windowWidth//10,windowHeight//6.5,image=QRCodeImage,anchor="nw")
        #handle what would happen if the user closed the QR code window
        self.__QRCodeWindow.protocol("WM_DELETE_WINDOW",lambda:exit())
        self.checkWhoJoined()
        tk.mainloop()
    def checkWhoJoined(self):
        """Checks who joined the game session
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
                #the remaining number of players is 5-the number of players we 
                #have in the dictionary
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
                self.__dmHandler.deleteThread(self.__players[username][0])
                remainingPlayers=5-len(self.__players)
                #if there are no remaining players
                if(remainingPlayers==0):
                    self.__randomWord=generate5LetterWord()
                    assignIndivdualWords(self.__randomWord,self.__players)
                    for player in self.__players:
                        self.__individualGames.append(IndividualGame(self.__dmHandler,(player,self.__players[player][0]),self.__players[player][2],self.__players[player][1]))
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
        return self.__randomWord
    def getIndividualGames(self):
        return self.__individualGames
class MainWindow:
    def __init__(self,dmHandler,randomWord,individualGames,players):
        self.__dmHandler=dmHandler
        self.__players=players
        self.__randomWord=randomWord
        self.__keepGettingUpdates=True
        self.__individualGames=individualGames
        print(self.__randomWord)
        print(players)
        self.initialiseMainWindow()
    def initialiseMainWindow(self):
        self.__MainWindow=tk.Tk()
        self.__MainWindow.title("Main Window")
        self.__MainWindow.iconbitmap("icon.ico")
        #the width and height of the QR code window
        windowWidth,windowHeight=[1200,650]
        #get the current screen's width and height in pixels
        screenWidth,screenHeight=[self.__MainWindow.winfo_screenwidth(),
                                  self.__MainWindow.winfo_screenheight()]
        #calculate the x and y coordinates of the center of the screen
        xCenter=(screenWidth//2)-(windowWidth//2)
        yCenter=(screenHeight//2)-(windowHeight//2)
        #set the size and where the window should open
        self.__MainWindow.geometry(f"{str(windowWidth)}x{str(windowHeight)}+{str(xCenter)}+{str(yCenter)}")
        #variable to hold the background image
        backgroundImage=tk.PhotoImage(file="backgroundImageMainWindow.png")
        #canvas that will hold the background image, text, and entry box
        canvas=tk.Canvas(self.__MainWindow,width=windowWidth,height=windowHeight,highlightthickness=0)
        #set the backgrounImage as an attribute of the canvas object to prevent 
        #python from "garbage collecting" it
        canvas.backgroundImage=backgroundImage
        canvas.pack(fill="both",expand=True)
        canvas.create_image(0,0,image=backgroundImage,anchor="nw")
        canvas.create_text(windowWidth//3.75,windowHeight//8,text="Guess The Word",font=("Comic Sans MS",50,"bold"))
        self.__enteredWord=tk.Entry(canvas,font=("MS Sans Serif",30,"bold"))
        canvas.create_window(windowWidth//3.75,windowHeight//2.5,window=self.__enteredWord)
        guessButton=tk.Button(canvas,text="guess",font=("MS Sans Serif",30,"bold"),command=self.checkGuess)
        canvas.create_window(windowWidth//3.75,windowHeight//1.75,window=guessButton)
        self.__textBox=tk.Text(self.__MainWindow,width=45,height=21,font=("MS Sans Serif",15,"bold"),state=DISABLED)
        canvas.create_window(windowWidth//1.3,windowHeight//2,window=self.__textBox)
        self.__textBox.configure(state="normal")
        self.__textBox.insert("end",f'Hello {", ".join(self.__players.keys())}\n')
        self.__textBox.configure(state=DISABLED)
        messagebox.showinfo("Game started!","Enter your first guess on instagram")
        self.getUpdates()
        tk.mainloop()
    def getRandomWord(self):
        return self.__randomWord
    def getIndividualWords(self):
        return [(player,self.__players[1],self.__players[2]) for player in self.__players]
    def getUpdates(self):
        if(not self.__individualGames[0].isGameDone() or\
              not self.__individualGames[1].isGameDone() or\
              not self.__individualGames[2].isGameDone() or\
              not self.__individualGames[3].isGameDone() or\
              not self.__individualGames[4].isGameDone()):
            for individualGame in self.__individualGames:
                if(not individualGame.isGameDone()):
                    individualGame.processOneGuess()
                    guess=individualGame.returnGuess()
                    if(guess!=None):
                        self.__textBox.configure(state="normal")
                        self.__textBox.insert("end",f'{individualGame.getUsername()} guessed: {individualGame.returnGuess()}\n')
                        self.__textBox.configure(state=DISABLED)
            self.__keepGettingUpdates=self.__MainWindow.after(10000,self.getUpdates)
        else:
            messagebox.showinfo("Guess the word","You are ready to guess the word!")
            self.__MainWindow.after_cancel(self.__keepGettingUpdates)
    def checkGuess(self):
        guess=self.__enteredWord.get()
        if(guess.lower()==self.__randomWord):
            messagebox.showinfo("Congratulations","Congrats! You guessed the word correctly")
            self.__MainWindow.destroy()
            for player in self.__players:
                try:
                    self.__dmHandler.deleteThread(player[0])
                except:
                    pass
        else:
            messagebox.showinfo("sorry :(",f'sorry :( you did not guess the word correctly. The word was "{self.__randomWord}"')
            self.__MainWindow.destroy()
            for player in self.__players:
                try:
                    self.__dmHandler.deleteThread(player[0])
                except:
                    pass