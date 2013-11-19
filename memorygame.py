import random
import Tkinter as tk


class Card:
    def __init__(self, canvas, number, value):
        self.canvas = canvas
        self.number = number
        self.value = value
        # Draw cards on the screen and grab their canvas reference
        self.valueReference = self.drawValue()
        self.coverReference = self.drawCover()

    def calcXPosition(self, offset):
        return self.number * 50 + offset

    def drawValue(self):
        return self.canvas.create_text(
            self.calcXPosition(30),         # x position
            50,                             # y position
            text=self.value,
            font='-*-new century schoolbook-bold-r-normal-*-35-*-*-*-*-*-*-*',
            fill="#880000"                  # color
        )

    def drawCover(self):
        return self.canvas.create_rectangle(
            self.calcXPosition(5),          # start x
            5,                              # start y
            self.calcXPosition(5) + 50,     # finish x
            100,                            # finish y
            fill="#008800",                 # color
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
        # Initialise the frame
        tk.Frame.__init__(self, master)
        self.columnconfigure(0, minsize="100")
        self.columnconfigure(1, minsize="850")
        self.grid()
        # Create some widgets
        self.controls = tk.LabelFrame(self)
        self.controls.columnconfigure(0, minsize="90")
        self.controls.grid(column=0)
        self.turnsLabel = tk.Label(self.controls, text="Turns: 0")
        self.turnsLabel.grid()
        tk.Button(self.controls, text='Reset', command=self.newGame).grid()
        tk.Button(self.controls, text='Quit', command=self.quit).grid()
        # Create the game canvas
        self.game = tk.Canvas(self, width=905, height=100)

    def newGame(self):
        '''
        New Game Method
        Resets all game variables, draws up new cards on the game canvas
        '''
        # Need to start fresh and make sure there are no elements on canvas
        self.game.delete(tk.ALL)
        self.turnsLabel.configure(text="Turns: 0")
        self.guesses = []
        # Create a new deck of numbers
        numbers = range(1, 10) * 2
        random.shuffle(numbers)
        self.deck = []
        for card in range(0, 18):
            # Create an instance of every playing card
            self.deck.append(Card(self.game, card, numbers.pop()))
        # Attach canvas to the grid.
        self.game.grid(column=1, row=0, ipadx=0, ipady=0)
        self.game.bind("<Button-1>", self.click)

    def click(self, event):
        '''
        Click Handler Method
        This is where the behaviour of the game is coded
        '''
        # Find out which card has been clicked
        card = (event.x - 5) / 50
        # Ignore clicks that aren't on a card
        if not 0 <= card <= 17:
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
            if self.deck[self.guesses[-3]].value != self.deck[self.guesses[-2]].value:
                # Make them not visible
                self.deck[self.guesses[-3]].setVisible(False)
                self.deck[self.guesses[-2]].setVisible(False)
        else:  # even guess, check for equal
            if self.deck[self.guesses[-2]].value == self.deck[card].value:
                # change color of text after a little bit of time
                self.after(500, self.deck[card].changeTextColor, "#000000")
                self.after(500, self.deck[self.guesses[-2]].changeTextColor, "#000000")


app = Application()
app.master.title('Memory Game')
app.newGame()
app.mainloop()
