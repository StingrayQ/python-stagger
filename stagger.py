import math
from tkinter import *
from tkinter import ttk

root = Tk()
root.title("Stagger Calculator")


############## Functions that get info############
def track_width():
    # gets the track width from center line of left wheel to the center line of the right wheel
    numTw = int(TWentry.get())
    return numTw


def rad_turn():
    # distance the inside tire travels through corner
    numRi = int(Cornerlengthentry.get())
    return numRi


def circ_in():
    # circumference of inside tire (measure tire)
    circInside = float(CircumferenceInsideentry.get())
    return circInside

def track_bank():
    # gets track banking
    banking = float(banking_entry.get())
    return banking

def showBank():
    if Bank.get() == 1:
        banking_entry.config(state=NORMAL)
    elif Bank.get() == 0:
        # deletes any info in the banking entry box before disabling the field
        banking_entry.delete(0, END)
        banking_entry.config(state=DISABLED)
###########################Calculation########################

# calculates the stagger by subtracting the outside tire from the inside tire size
def disp_stagger():
    if Bank.get() == 0:
        # turns feet to inches
        calc_rad_turn = rad_turn() * 12
        outside_tire_rad = track_width() + calc_rad_turn
        # distance outside tire travels through turn
        dist_out_travel = (outside_tire_rad * 2) * (math.pi / 2)
        # distance inside tire travels through turn
        dist_in_travel = (calc_rad_turn * 2) * (math.pi / 2)
        circ_out = circ_in() * dist_out_travel / dist_in_travel
        stagger = (circ_out - circ_in())
        CalcstaggerLabel.config(text=f"{stagger:.2f}" + '"')
        CalcOutterTireLabel.config(text=f"{circ_out:.2f}" + '"')
    elif Bank.get() == 1:
        # turns feet to inches
        calc_rad_turn = rad_turn() * 12
        outside_tire_rad = track_width() + calc_rad_turn
        # distance outside tire travels through turn
        dist_out_travel = (outside_tire_rad * 2) * (math.pi / 2)
        # distance inside tire travels through turn
        dist_in_travel = (calc_rad_turn * 2) * (math.pi / 2)
        circ_out = circ_in() * dist_out_travel / dist_in_travel
        stagger = (circ_out - circ_in())
        bankStagger = (math.cos(math.radians(track_bank())) * stagger)
        bank_circ_out = circ_in() + bankStagger
        CalcstaggerLabel.config(text=f"{bankStagger:.2f}" + '"')
        CalcOutterTireLabel.config(text=f"{bank_circ_out:.2f}" + '"')

    return stagger, circ_out







trackWidthLabel = Label(root, text="Track Width")
trackWidthLabel.grid(row=0, column=0)
TWentry = ttk.Entry(root, width=10)
TWentry.grid(row=0, column=1)
CornerlgthLabel = Label(root, text="Corner length (in feet)")
CornerlgthLabel.grid(row=1, column=0)
Cornerlengthentry = ttk.Entry(root, width=10)
Cornerlengthentry.grid(row=1, column=1)
CircumferenceInsideLabel = Label(root, text="Circumference of inside tire (in inches) ")
CircumferenceInsideLabel.grid(row=2, column=0)
CircumferenceInsideentry = ttk.Entry(root, width=10)
CircumferenceInsideentry.grid(row=2, column=1)
CalcstaggerLabel = Label(root, font="ariel 15 bold")
CalcstaggerLabel.grid(row=5, column=1)
CalcOutterTireLabel = Label(root, font="ariel 15 bold")
CalcOutterTireLabel.grid(row=6, column=1)
calcButton = ttk.Button(root, text="Calculate", command=disp_stagger)
calcButton.grid(row=4, column=1, pady=(30, 0))
StaggerLabel = Label(root, text="Stagger ")
StaggerLabel.grid(row=5, column=0)
OutsideTireSizeLabel = Label(root, text="Outside Tire Size ")
OutsideTireSizeLabel.grid(row=6, column=0)
Bank = IntVar()
Bank.set(0)
Bankingbutton = Checkbutton(root, text="Yes", var=Bank, command=showBank)
Bankingbutton.grid(row=3, column=3)
bankingLabel = Label(root, text="Track Banking (in degrees) ")
bankingLabel.grid(row=3, column=0)
banking_entry = ttk.Entry(root, width=10, state=DISABLED)
banking_entry.grid(row=3, column=1)


root.geometry("400x300")
root.mainloop()

