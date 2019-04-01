import math


run = True

while run == True:

# gets the track width in relation to width of car to center of vehicle
    numTw = int(input("Enter the track width of the vehicle: "))

# gets the radius of the turn in relation to the inside tire
    numRi = int(input("Enter the length of the corner in feet: "))
    numRi = numRi * 12
# returns the outside tire radius
    numRo = numRi + numTw

 # distance inside tire travels through turn
    distanceInside = numRi * 2 * math.pi / 2

# distance outside tire travels through turn
    distanceOutside = (numRo * 2) * math.pi / 2

# circumference of inside tire (measure tire)
    circInside = float(input("Enter the size of the inside tire in inches: "))

# circumference of outside tire (Ci * (Do/Di))
    circOutside = circInside * distanceOutside / distanceInside

# calculates the stagger by subtracting the outside tire from the inside tire size
    stagger = circOutside - circInside
    print(f"Stagger should be {stagger:.2f}")
    print(f"The outside tire size should be {circOutside:.2f}" )

# calculates stagger based on the bank of the racetrack
    bankQuest = input("Do you want to calculate stagger for banking? ")
    if bankQuest == "yes" or bankQuest == "y":
        bank = float(input("What is the banking of the track? "))
    else:
        bankQuest == "n" or bankQuest == "no"
        print("Thanks for using the program")
        break

    bankStagger = math.cos(math.radians(bank)) * stagger
    print("The stagger on " + str(bank) + " degrees of banking is " + f"{bankStagger:.2f}")

    finish = input("Would you like to calculate different stagger?")
    if finish == "yes" or finish == "y":
        continue
    else:
        print("Thanks for using the program")
        run = False












# Radius of inside tire=200 feet or 2400 inches ( 12" x 200')
# Radius of outside tire= 2465 inches ( 2400 + 65" track width )
# Outside tire travels 2465 x 2 x pi (3.1416) Divided by 2 =7744 inches
# Inside tire travels 2400x 2 x pi Divided by 2 = 7540 inches
# outside tire= 85inches in circumference
# inside tire = 85 x ( 7540 divided 7744 ) = 82.75
# Correct stagger =85 minus 82.75 or 2 1/4

# Pi = 3.1416…
# T = track (width) of car at tire center lines
# Ri = radius of turn to inside tire
# Ro = radius of turn to outside tire (Ri + T)
# Di = distance inside tire travels through turn (Ri * 2 * Pi / 2)
# Do = distance outside tire travels through turn (Ro * 2 * Pi / 2)
# Ci = circumference of inside tire (measure tire)
# Co = circumference of outside tire (Ci * (Do/Di))
# Stagger = Co - Ci


# Another wrinkle is taking into account the tracks banking.
# Banking will reduce the effective radius of a turn, so the more banking a track has,
# the less stagger you need. Multiply the stagger value by the cosine of the bank angle.
# For Stafford, turns 1 & 2 are 9º, while turns 3 & 4 are 7.5º Since we can only tune for one angle,
# we use the average of 8.25º.
# COS 8.25º = 0.9897
# 2" * 0.989 = 1.979"

