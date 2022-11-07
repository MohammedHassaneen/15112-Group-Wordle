import tkinter as tk
from tkinter import messagebox,DISABLED
import customtkinter
from PIL import Image, ImageTk
import os

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

PATH = os.path.dirname(os.path.realpath(__file__))


class App(customtkinter.CTk):

    APP_NAME = "CustomTkinter example_background_image.py"
    WIDTH = 500
    HEIGHT = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title(App.APP_NAME)
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.minsize(App.WIDTH, App.HEIGHT)
        self.maxsize(App.WIDTH, App.HEIGHT)
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # load image with PIL and convert to PhotoImage
        image = Image.open(PATH + "\\botQRCode.png").resize((self.WIDTH, self.HEIGHT))
        self.bg_image = ImageTk.PhotoImage(image)
        self.image_label = tkinter.Label(master=self, image=self.bg_image)
        self.image_label.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
    def on_closing(self):
        self.destroy()

    def start(self):
        self.mainloop()

class QRCodeWindow:
    def __init__(self):
        windowWidth,windowHeight=[500,500]
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("dark-blue")
        self.__window=customtkinter.CTk()
        self.__window.title("QR Code")
        self.__window.iconbitmap("icon.ico")
        self.__window.geometry(f"{str(windowWidth)}x{str(windowHeight)}")
        self.__window.minsize(windowWidth,windowHeight)
        self.__window.maxsize(windowWidth,windowHeight)
        self.__window.resizable(False, False)
        image = Image.open("QRCodeWindowImage.png").resize((windowWidth*2, int(windowHeight*1.8)))
        self.bg_image = ImageTk.PhotoImage(image)
        self.image_label=tk.Label(self.__window, image=self.bg_image)
        self.image_label.place(relx=0.5, rely=0.49, anchor=tk.CENTER)
        self.__window.mainloop()
class MainWindow:
    def __init__(self):
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
                                                state=DISABLED
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
        self.updatesTextbox=customtkinter.CTkTextbox(self.rightFrame,width=420,height=440,text_font=("comic Sans SF",18,"bold"),state=DISABLED)
        self.updatesTextbox.place(relx=0.5,rely=0.62,anchor=tk.CENTER)
        #add a hello message to the updates textbox
        self.updatesTextbox.configure(state="normal")
        self.updatesTextbox.insert("end",f'Hello {", ".join(self.__players.keys())}\n')
        self.__mainWindow.mainloop()
MainWindow()
        # self.__MainWindow=tk.Tk()
        # self.__MainWindow.title("Main Window")
        # self.__MainWindow.iconbitmap("icon.ico")
        # #the width and height of the QR code window
        # windowWidth,windowHeight=[1200,650]
        # #get the current screen's width and height in pixels
        # screenWidth,screenHeight=[self.__MainWindow.winfo_screenwidth(),
        #                           self.__MainWindow.winfo_screenheight()]
        # #calculate the x and y coordinates of the center of the screen
        # xCenter=(screenWidth//2)-(windowWidth//2)
        # yCenter=(screenHeight//2)-(windowHeight//2)
        # #set the size and where the window should open
        # self.__MainWindow.geometry(f"{str(windowWidth)}x{str(windowHeight)}+{str(xCenter)}+{str(yCenter)}")
        # #variable to hold the background image
        # backgroundImage=tk.PhotoImage(file="backgroundImageMainWindow.png")
        # #canvas that will hold the background image, text, and entry box
        # canvas=tk.Canvas(self.__MainWindow,width=windowWidth,height=windowHeight,highlightthickness=0)
        # #set the backgrounImage as an attribute of the canvas object to prevent 
        # #python from "garbage collecting" it
        # canvas.backgroundImage=backgroundImage
        # canvas.pack(fill="both",expand=True)
        # canvas.create_image(0,0,image=backgroundImage,anchor="nw")
        # canvas.create_text(windowWidth//3.75,windowHeight//8,text="Guess The Word",font=("Comic Sans MS",50,"bold"))
        # self.__enteredWord=tk.Entry(canvas,font=("MS Sans Serif",30,"bold"))
        # canvas.create_window(windowWidth//3.75,windowHeight//2.5,window=self.__enteredWord)
        # self.__guessButton=tk.Button(canvas,text="guess",font=("MS Sans Serif",30,"bold"),command=self.checkGuess,state=DISABLED)
        # canvas.create_window(windowWidth//3.75,windowHeight//1.75,window=self.__guessButton)
        # self.__textBox=tk.Text(self.__MainWindow,width=45,height=21,font=("MS Sans Serif",15,"bold"),state=DISABLED)
        # canvas.create_window(windowWidth//1.3,windowHeight//2,window=self.__textBox)
        # self.__textBox.configure(state="normal")
        # self.__textBox.insert("end",f'Hello {", ".join(self.__players.keys())}\n')
        # self.__textBox.configure(state=DISABLED)
        # messagebox.showinfo("Game started!","Enter your first guess on instagram")
        # self.getUpdates()
        # tk.mainloop()