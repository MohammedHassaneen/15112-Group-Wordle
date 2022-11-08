# Name: Mohammed Elsayed
# AndrewID: mohammee
from functions import *
from classes import *
def main():
    """main function that runs the game
    """
    #create a new InstagramAccount object 
    #username and password go here
    account=InstagramAccount("USERNAME","PASSWORD")
    account.login()
    dmHandler=account.getDMHandler()
    qrCodeWindow=QRCodeWindow(dmHandler)
    randomWord=qrCodeWindow.getRandomWord()
    individualGames=qrCodeWindow.getIndividualGames()
    players=qrCodeWindow.getPlayers()
    MainWindow(dmHandler,randomWord,individualGames,players)
main()