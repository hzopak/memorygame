'''
Simple basic memory game with selectable card sets.
'''

import random
import Tkinter as tk
import tkMessageBox


# Some settings
MAXCARDSPERROW = 10
MAXSETS = 20
# The card values and font values need to play nice with each other
# Careful when adjusting one, you may have to fiddle with another
CARDWIDTH = 50
CARDHEIGHT = 100
CARDCOLOR = "#0033AA"
FONTSIZE = 35
FONTCOLOR = "#AA3300"
DISPLAY_OFFSET = 3
DISPLAY_VALUE_OFFSET = 30


class Card:
    def __init__(self, canvas, number, value):
        self.canvas = canvas
        self.number = number
        self.value = value
        # Draw cards on the screen and grab their canvas reference
        self.valueReference = self.drawValue()
        self.coverReference = self.drawCover()

    def calcXPosition(self, offset):
        return self.number % MAXCARDSPERROW * CARDWIDTH + offset

    def calcYPosition(self, offset):
        return self.number / MAXCARDSPERROW * CARDHEIGHT + offset

    def drawValue(self):
        return self.canvas.create_text(
            self.calcXPosition(DISPLAY_VALUE_OFFSET),   # x position
            self.calcYPosition(CARDHEIGHT / 2),         # y position
            text=self.value,
            font='-*-new century schoolbook-bold-r-normal-*-%d-*-*-*-*-*-*-*'
            % FONTSIZE,
            fill=FONTCOLOR                 # color
        )

    def drawCover(self):
        return self.canvas.create_rectangle(
            self.calcXPosition(DISPLAY_OFFSET),          # start x
            self.calcYPosition(DISPLAY_OFFSET),          # start y
            self.calcXPosition(DISPLAY_OFFSET + CARDWIDTH),     # finish x
            self.calcYPosition(DISPLAY_OFFSET + CARDHEIGHT),    # finish y
            fill=CARDCOLOR,                 # color
            state=tk.NORMAL                 # normal means cover is visible
        )

    def isVisible(self):
        if self.canvas.itemcget(self.coverReference, 'state') == tk.HIDDEN:
            return True

    def setVisible(self, state):
        if state:
            self.canvas.itemconfigure(self.coverReference, state=tk.HIDDEN)
        else:
            self.canvas.itemconfigure(self.coverReference, state=tk.NORMAL)

    def changeTextColor(self, color):
        self.canvas.itemconfigure(self.valueReference, fill=color)


class Application(tk.Frame):
    def __init__(self, master=None):
        '''
        Init Method
        Establishes the frame of the GUI and sets up some buttons
        '''
        # Initialise the frame
        tk.Frame.__init__(self, master)
        self.columnconfigure(0, minsize="100")
        self.columnconfigure(1)
        self.grid()
        # Create some widgets
        self.controls = tk.LabelFrame(self)
        self.controls.columnconfigure(0, minsize="90")
        self.controls.grid(column=0)
        self.turnsLabel = tk.Label(self.controls, text="Turns: 0")
        self.turnsLabel.grid(column=0)
        tk.Label(self.controls, text="\nSet Card Sets:").grid()
        optionList = range(1, MAXSETS + 1)
        self.optvalue = tk.StringVar()
        self.optvalue.set(optionList[len(optionList) / 2 - 1])
        self.optfield = tk.OptionMenu(
            self.controls, self.optvalue, *optionList)
        self.optfield.grid()
        tk.Button(self.controls, text='New Game', command=self.newGame).grid()
        tk.Label(self.controls, text="\n").grid()
        tk.Button(self.controls, text='Quit', command=self.quit).grid()
        # Create the game canvas
        self.game = tk.Canvas(self)

    def newGame(self):
        '''
        New Game Method
        Resets all game variables, draws up new cards on the game canvas
        '''
        # Need to start fresh and make sure there are no elements on canvas
        self.game.delete(tk.ALL)
        self.turnsLabel.configure(text="Turns: 0")
        self.guesses = []
        # Fetch the current value of card sets the user has selected
        self.totalcardsets = int(self.optvalue.get())
        self.totalcards = self.totalcardsets * 2
        # Create a new deck of numbers
        numbers = range(self.totalcardsets) * 2
        random.shuffle(numbers)
        self.deck = []
        for card in range(0, self.totalcards):
            # Create an instance of every playing card
            self.deck.append(Card(self.game, card, numbers.pop()))
        # Attach canvas to the grid.
        # Calculate the size required for the canvas
        canvaswidth = MAXCARDSPERROW * CARDWIDTH + DISPLAY_OFFSET
        if self.totalcards < MAXCARDSPERROW:
            canvaswidth = self.totalcards * CARDWIDTH + DISPLAY_OFFSET
        canvasheight = (self.totalcards / MAXCARDSPERROW) * CARDHEIGHT +\
            DISPLAY_OFFSET
        if self.totalcards % MAXCARDSPERROW:
            canvasheight += CARDHEIGHT
        # Resize the canvas to fit the current playing cards
        self.game.configure(width=canvaswidth, height=canvasheight)
        self.game.grid(column=1, row=0, ipadx=0, ipady=0)
        self.game.bind("<ButtonRelease-1>", self.click)

    def click(self, event):
        '''
        Click Handler Method
        This is where the behaviour of the game is coded
        '''
        # Find out which card has been clicked
        card = ((event.x - DISPLAY_OFFSET) / CARDWIDTH) +\
               (MAXCARDSPERROW * ((event.y - DISPLAY_OFFSET) / CARDHEIGHT))
        # Ignore clicks that aren't on a card
        if not 0 <= card < self.totalcards:
            return
        # Ignore clicks on cards that are visible
        if self.deck[card].isVisible():
            return
        self.guesses.append(card)
        # Make the card they clicked visible
        self.deck[card].setVisible(True)
        # Only do checks after the first guess
        if len(self.guesses) < 2:
            return
        self.turnsLabel.configure(text="Turns: %s" % (len(self.guesses) / 2))
        if len(self.guesses) % 2:  # Odd guess, eliminate before guesses
            # Check if the previous two guesses are not equal
            if (self.deck[self.guesses[-3]].value !=
                    self.deck[self.guesses[-2]].value):
                # Make them not visible
                self.deck[self.guesses[-3]].setVisible(False)
                self.deck[self.guesses[-2]].setVisible(False)
        else:  # even guess, check for equal
            if self.deck[self.guesses[-2]].value == self.deck[card].value:
                # change color of text after a little bit of time
                self.after(500, self.deck[card].changeTextColor, "#000000")
                self.after(500, self.deck[self.guesses[-2]].changeTextColor,
                           "#000000")
        self.checkwin()

    def checkwin(self):
        viscards = [card for card in self.deck if card.isVisible()]
        if len(viscards) == self.totalcards:
            self.after(
                50,
                tkMessageBox.showinfo,
                'Memory Game',
                "Congratulations!\n\nYou've completed %d card sets in %d turns"
                % (self.totalcardsets, len(self.guesses) / 2)
                )


app = Application()
app.master.title('Memory Game')
app.newGame()
app.mainloop()
