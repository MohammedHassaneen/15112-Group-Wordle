import requests
import pickle
import uuid
import os
import sqlite3
#class WordGenerator:
#class gameSession:
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
    def approvePendingDMRequests(self,threadID):
        """Approves the pending DM request by threadID

        Args:
            threadID (String): the thread ID of the pending chat to be accepted
        """
        #send a request to approve the pending chat request
        approvePendingRequest=self.__session.post(f"https://i.instagram.com/api/v1/direct_v2/threads/{threadID}/approve/",headers=self.__headers)
        #if the chat request was approved successfully
        if '"status":"ok"' in approvePendingRequest.text: return True
        else: return False
    def getDMThreads(self):
        """gets the DM chats (threads) in the chat page

        Returns:
            List: a list of the thread IDs of the DM chats
        """
        #a list of the thread IDs of the DM chats
        DMThreads=[]
        #send a request to get the DM chats
        getDMRequests=self.__session.get("https://i.instagram.com/api/v1/direct_v2/inbox/?use_unified_inbox=true&persistentBadging=true",headers=self.__headers)
        #for every thread (chat) in the response
        for i in range(0,len(getDMRequests.json()["inbox"]["threads"])):
            #append the thread ID of the chat to the list of DMThreads
            DMThreads.append(getDMRequests.json()["inbox"]["threads"][i]["thread_id"])
        #return the list of the thread IDs of the DM chats
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
#class GUI: