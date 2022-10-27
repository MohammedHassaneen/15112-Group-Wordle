import requests
import re
import random
def acceptPendingRequests(dmHandler):
    """Accepts all the pending DM requests
    """
    pendingRequests=dmHandler.getPendingDMRequests()
    for pendingRequest in pendingRequests:
        dmHandler.approvePendingDMRequest(pendingRequest)
def generate5LetterWord(constraint=None):
    """Generates a random 5 letter word based on a given constraint. The 
       constraint is simply "The letter X should be at position i"

    Args:
        processedUsernames (tuple, optional): a tuple of the form (i,x) where i
                                              is the index the letter x should be
                                              at in the random word we will generate.
                                              Defaults to None.

    Returns:
        List: a list of the messages (thread items) in the chat with the threadID passed
    """
    #if no constraint is provided, then we do not need to specify a pattern
    #for the word we will generate
    if(constraint==None):
        pattern=""
    else:
        #specify the pattern the generated word should have based on the constraint
        pattern=["_"]*5
        pattern[constraint[0]]=constraint[1]
        pattern="".join(pattern)
    #headers for the generateWord request
    headers={"X-IG-Capabilities": "3wI=",
             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
             "Accept-Language": "en-Qa",
             "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
             "X-Requested-With": "XMLHttpRequest"}
    #postData for the generatedWord request
    postData={"word_count":1,
              "pattern":pattern,
              "word_len_operator":"=",
              "word_length":"5",
              "action":"generate"
            }
    generateWordRequest=requests.post("https://www.thewordfinder.com/random-word-generator/",headers=headers,data=postData)
    #try to get a random word and return it
    try:
        #get the random word from the HTML response we get after sending the 
        #generatedWord request using regex
        word=re.search("""</i>(.*?)</a></li>""",generateWordRequest.text).group(1)
        return word.lower()
    #if an exception occurs for some reason, return False instead of crashing
    except:
        return False
def assignIndivdualWords(randomWord,players):
    """assign a random word to players based on randomWord

    Args:
        randomWord (String): the random word we will base the gemeration of 
                             individual words on.
        players (dictionary): a dictionary of the form {username:[threadID]}
    """
    indices=list(range(5))
    for player in players:
        randomIndex=random.choice(indices)
        players[player].append(randomIndex)
        randomIndividualWord=generate5LetterWord((randomIndex,randomWord[randomIndex]))
        players[player].append(randomIndividualWord)
        indices.remove(randomIndex)
    return players