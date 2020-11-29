from tkinter import *

def onclick():
   pass

root = Tk()
root.title('A secret message app')
text = Text(root)
text.insert(END, "Welcome to the secrete world.....")
text.pack()
root.mainloop()