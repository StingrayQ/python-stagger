import math
from tkinter import *
from tkinter import ttk

root = Tk()
root.title("Stagger Calculator")


############## Functions that get info############
def track_width():
    # gets the track width from center line of left wheel to the center line of the right wheel
    numTw = int(entry.get())
    return numTw


def rad_turn():
    # distance the inside tire travels through corner
    numRi = int(entry2.get())
    return numRi


def circ_in():
    # circumference of inside tire (measure tire)
    circInside = float(entry3.get())
    return circInside


# calculates the stagger by subtracting the outside tire from the inside tire size
def disp_stagger():
    # turns feet to inches
    calc_rad_turn = rad_turn() * 12
    outside_tire_rad = track_width() + calc_rad_turn
    # distance outside tire travels through turn
    dist_out_travel = (outside_tire_rad * 2) * (math.pi / 2)
    # distance inside tire travels through turn
    dist_in_travel = (calc_rad_turn * 2) * (math.pi / 2)
    circ_out = circ_in() * dist_out_travel / dist_in_travel
    stagger = (circ_out - circ_in())
    CalcstaggerLabel.config(text=f"{stagger:.2f}")
    CalcOutterTireLabel.config(text=f"{circ_out:.2f}")
    return stagger, circ_out



# Creating Menubar
menubar = Menu(root)
file = Menu(menubar, tearoff=0)
menubar.add_cascade(label='File', menu=file)
file.add_command(label='Tracks (Coming Soon)', command=None)
file.add_command(label='Vehicles (Coming Soon)', command=None)
file.add_separator()
file.add_command(label='Exit', command=root.destroy)

trackWidthLabel = Label(root, text="Track Width")
trackWidthLabel.grid(row=0, column=0)
entry = ttk.Entry(root, width=20)
entry.grid(row=0, column=1)
entry2 = ttk.Entry(root, width=20)
entry2.grid(row=1, column=1)
entry3 = ttk.Entry(root, width=20)
entry3.grid(row=2, column=1)
CalcstaggerLabel = Label(root, font="ariel 15 bold")  # f"{disp_stagger():.2f}"
CalcstaggerLabel.grid(row=4, column=1)
CalcOutterTireLabel = Label(root, font="ariel 15 bold")
CalcOutterTireLabel.grid(row=5, column=1)  # entry.insert(0,str(result))
CornerlgthLabel = Label(root, text="Corner length ")
CornerlgthLabel.grid(row=1, column=0)
CircumferenceInsideLabel = Label(root, text="Circumference of inside tire (inches) ")
CircumferenceInsideLabel.grid(row=2, column=0)
OutsideTireSizeLabel = Label(root, text="The outside tire size should be ")
OutsideTireSizeLabel.grid(row=5, column=0)
StaggerLabel = Label(root, text="Calculated Stagger ")
StaggerLabel.grid(row=4, column=0)
calcButton = ttk.Button(root, text="Calculate", command=disp_stagger)
calcButton.grid(row=3, column=1)

root.geometry("600x300")
root.config(menu=menubar)
root.mainloop()

# run = True
#
# while run == True:

# gets the track width from center line of left wheel to the center line of the right wheel


# # numTw = int(input("Enter the track width of the vehicle: "))
# # if numTw == "" or numTw == " ":
# #     print("Please enter a value")
# # elif numTw == "q" or numTw == "quit":
# #     run = False
# # else: continue
# # gets the radius of the turn in relation to the inside tire
# #numRi = int(input("Enter the length of the corner in feet: "))
#
# # converts feet to inches
# numRi = numRi * 12
#
# # returns the outside tire radius
# numRo = numRi + numTw
# # def getRadius(numRi):
# # # gets the radius of the turn in relation to the inside tire
# #     numRi = int(input("Enter the length of the corner in feet: "))
# #     numRi = numRi * 12
# #     return numRi
# #
# # # converts feet to inches
#
#
# # returns the outside tire radius
# numRo = numRi + numTw
#
# # distance inside tire travels through turn
# distanceInside = numRi * 2 * math.pi / 2
#
# # distance outside tire travels through turn
# distanceOutside = (numRo * 2) * math.pi / 2
#
# # circumference of inside tire (measure tire)
# circInside = float(input("Enter the size of the inside tire in inches: "))
#
# # circumference of outside tire
# circOutside = circInside * distanceOutside / distanceInside
#
# # calculates the stagger by subtracting the outside tire from the inside tire size
# stagger = circOutside - circInside
# print(f"Stagger should be {stagger:.2f}")
# print(f"The outside tire size should be {circOutside:.2f}" )
#
# # gets input if the user wants to get the stagger based on track banking
# bankQuest = input("Do you want to calculate stagger for banking? ")
# if bankQuest == "yes" or bankQuest == "y":
#     bank = float(input("What is the banking of the track? "))
# else:
#     bankQuest == "n" or bankQuest == "no"
#     print("Thanks for using the program!")
#     break
#
# # calculates stagger based on the bank of the racetrack by taking banking and converting it from
# # radian to degrees then multiplying by stagger number
# bankStagger = math.cos(math.radians(bank)) * stagger
# print("The stagger on " + str(bank) + " degrees of banking is " + f"{bankStagger:.2f}")
#
# finish = input("Would you like to calculate different stagger? ")
# if finish == "yes" or finish == "y":
#     continue
# else:
#     print("Thanks for using the program!")
#     run = False
#
#
