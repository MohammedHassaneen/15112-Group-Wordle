from functions import *
from classes import *
def main():
    account=InstagramAccount("USERNAME","PASSWORD")
    account.login()
    dmHandler=account.getDMHandler()
    qrCodeWindow=QRCodeWindow(dmHandler)
    randomWord=qrCodeWindow.getRandomWord()
    individualGames=qrCodeWindow.getIndividualGames()
    players=qrCodeWindow.getPlayers()
    MainWindow(dmHandler,randomWord,individualGames,players)
main()