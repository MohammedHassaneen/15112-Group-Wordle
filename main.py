# Name: Mohammed Elsayed
# AndrewID: mohammee
from functions import *
from classes import *
def main():
    """main function that runs the game
    """
    #create a new InstagramAccount object 
    account=InstagramAccount("USERNAME","PASSWORD")
    #IMPORTANT NOTE!!! the login function does not handle challenges (2fa), so
    #the account we are trying to login to must have 2fa disabled
    account.login()
    dmHandler=account.getDMHandler()
    qrCodeWindow=QRCodeWindow(dmHandler)
    randomWord=qrCodeWindow.getRandomWord()
    individualGames=qrCodeWindow.getIndividualGames()
    players=qrCodeWindow.getPlayers()
    MainWindow(dmHandler,randomWord,individualGames,players)
main()