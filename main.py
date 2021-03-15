from pyperclip import copy, paste, waitForNewPaste
from tkinter import *
from packages.latex_question import latex_question, latex_symbols, parse_assignment, latexify
from packages.book import raw_book
from time import sleep
from ctypes import windll
from threading import Thread

# fix blurry windows on high DPI displays
windll.shcore.SetProcessDpiAwareness(1) 

# somewhere through this code, line breaks do not get preserved. some major bs from python

def paste_latex_copy():  
    """Paste from clipboard, format, then copy to clipboard
    
    Format based on user wishes (Question/Equation/Section)
    """

    # paste from clipboard
    raw_block = paste() 

    # format based on fomatting option
    if formatting_option.get() == "Question":
        res = latex_question(raw_block)

    elif formatting_option.get() == "Equation":
        res = latex_symbols(raw_block)

    elif formatting_option.get() == "Section":
        res = parse_assignment(raw_block)
        exit_code = res[0]
        parsed_assignment = res[1]
        if not exit_code:
            res = latexify(parsed_assignment)


    exit_code = res[0]
    latex_block = str(res[1])

    if exit_code == 0:
        copy(latex_block) # copy formatted text to clipboard
        return raw_block, latex_block # for display purposes
    else:
        copy('\\')
        return raw_block, latex_block

def close_root(): 
    # defind what happens when you click X

    print("root closed")
    root.destroy()

def open_log():
    log = Toplevel(root)

def toggle_pause():
    global paused
    paused = not paused
#---------------------------




#----------------------------
bgcolor = "gray93"

paused  = False
#---------------------------------------------------------------#
root = Tk()
root.title("Latex Question")
root.minsize(710,170) # minimum size of root
menu_bar = Menu(root) 
root.configure(background=bgcolor, menu = menu_bar) # background color
root.protocol("WM_DELETE_WINDOW", close_root) # call close_root on exit
root.attributes('-topmost', True) # keep root on top
root.grid_rowconfigure(0,weight=1)
root.grid_rowconfigure(1,weight=1)
root.grid_columnconfigure(0,weight=1)
#---------------------------------------------------------------#
formatting_option = StringVar(root, "Section")

# file Menu and commands 
menu_bar_latex = Menu(menu_bar, tearoff = 0) 
menu_bar.add_cascade(label ='Latex', menu = menu_bar_latex) 
menu_bar_latex.add_command(label='Log', command=open_log)
menu_bar_latex.add_separator()
menu_bar_latex.add_command(label ='Exit', command = close_root)

# format menu
menu_bar_format = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label='Format', menu=menu_bar_format)
menu_bar_format.add_checkbutton(label ='Pause',command=toggle_pause)  
menu_bar_format.add_separator()
menu_bar_format.add_radiobutton(label ='Question',variable=formatting_option, command = None)
menu_bar_format.add_radiobutton(label ='Equation',variable=formatting_option, command = None)
menu_bar_format.add_radiobutton(label ='Section',variable=formatting_option, command = None)

# help menu 
menu_bar_help = Menu(menu_bar, tearoff = 0) 
menu_bar.add_cascade(label ='Help', menu = menu_bar_help) 
menu_bar_help.add_command(label ='Tk Help', command = None) 
menu_bar_help.add_command(label ='Demo', command = None) 
menu_bar_help.add_separator() 
menu_bar_help.add_command(label ='About Tk', command = None) 


class CodeSpace():
    def __init__(self, master, grid, **kwargs):
        self.frame = LabelFrame(master, **kwargs)
        self.frame.grid(row=grid[0], column=grid[1])
        
        self.scrollbar = Scrollbar(self.frame)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        
        self.code = Text(self.frame, bg="gray15", fg="white", font=("consolas", 10), yscrollcommand=self.scrollbar.set, wrap=WORD)
        self.code.pack(fill='both', expand=True)

        self.scrollbar.config(command=self.code.yview)

raw = CodeSpace(root, (0,0), text=' Input ')
output = CodeSpace(root, (1,0), text=' Output ')



def update_text(text): 
    raw_text = text[0]
    latex_text = text[1]

    raw.code.delete("1.0", END)
    raw.code.insert(INSERT, raw_text)

    output.code.delete("1.0", END)
    output.code.insert(INSERT, latex_text)


def update():
    while waitForNewPaste():
        if paused:
            update_text(('Paused.', 'Error'))
            while paused:
                sleep(0.01)
        update_text(paste_latex_copy())

# seperate thread to keep checking for new paste
Thread(target=update, daemon=True).start() # checking for new input is done separately

root.mainloop()

