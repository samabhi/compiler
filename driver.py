from pascal_scanner import Scanner
from pascal_simulator import Simulator
from pascal_parser import Parser
import tkinter
from tkinter.filedialog import FileDialog, askopenfilename

#main method calls everything
if __name__ == '__main__':
    # To view various examples of what this compiler is capable of,
    # uncomment one of the lines below AT A TIME

    #Run the scanner
    root = tkinter.Tk()
    root.withdraw()
    filename = askopenfilename(initialdir='pascal_testFunctions',
                               filetypes=[("Pascal File","*.pas")],
                               title='Choose a pascal file'
                            )
    scn = Scanner(filename)

    clues = scn.scan()

    # Parser
    pascal_parser = Parser(clues)
    byte_list = pascal_parser.start_parser()

    #Simulator
    simulator = Simulator(byte_list)
    simulator.start_simulator()







