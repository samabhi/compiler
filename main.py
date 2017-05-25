from pascal_scanner import Scanner
from pascal_simulator import Simulator
from pascal_parser import Parser
import tkinter
from tkinter.filedialog import FileDialog, askopenfilename

if __name__ == '__main__':

    root = tkinter.Tk()
    root.withdraw()
    filename = askopenfilename(initialdir='pascal_testFunctions',
                               filetypes=[("Pascal File","*.pas")],
                               title='Choose a pascal file'
                            )

    token_list = Scanner(filename).scan()
    instruction_list = Parser(token_list).start_parser()
    Simulator(instruction_list).simulator()
