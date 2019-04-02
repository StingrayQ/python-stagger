import math

run = True

while run == True:

    # gets the track width from center line of left wheel to the center line of the right wheel
    numTw = int(input("Enter the track width of the vehicle: "))
    # if numTw == "" or numTw == " ":
    #     print("Please enter a value")
    # elif numTw == "q" or numTw == "quit":
    #     run = False
    # else: continue

    # gets the radius of the turn in relation to the inside tire
    numRi = int(input("Enter the length of the corner in feet: "))

    # converts feet to inches
    numRi = numRi * 12

    # returns the outside tire radius
    numRo = numRi + numTw

    # distance inside tire travels through turn
    distanceInside = numRi * 2 * math.pi / 2

    # distance outside tire travels through turn
    distanceOutside = (numRo * 2) * math.pi / 2

    # circumference of inside tire (measure tire)
    circInside = float(input("Enter the size of the inside tire in inches: "))

    # circumference of outside tire
    circOutside = circInside * distanceOutside / distanceInside

    # calculates the stagger by subtracting the outside tire from the inside tire size
    stagger = circOutside - circInside
    print(f"Stagger should be {stagger:.2f}")
    print(f"The outside tire size should be {circOutside:.2f}" )

    # gets input if the user wants to get the stagger based on track banking
    bankQuest = input("Do you want to calculate stagger for banking? ")
    if bankQuest == "yes" or bankQuest == "y":
        bank = float(input("What is the banking of the track? "))
    else:
        bankQuest == "n" or bankQuest == "no"
        print("Thanks for using the program!")
        break

    # calculates stagger based on the bank of the racetrack by taking banking and converting it from
    # radian to degrees then multiplying by stagger number
    bankStagger = math.cos(math.radians(bank)) * stagger
    print("The stagger on " + str(bank) + " degrees of banking is " + f"{bankStagger:.2f}")

    finish = input("Would you like to calculate different stagger? ")
    if finish == "yes" or finish == "y":
        continue
    else:
        print("Thanks for using the program!")
        run = False


