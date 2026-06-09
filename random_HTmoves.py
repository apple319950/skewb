import random

number = random.randint(10, 15)
replacements = {"4": "U2", "8": "D2", "7": "F2", "5": "B2", "3": "L2", "9": "R2"}
moves = ""
c = 0
b = 0
for i in range(number):
    while True:
        a = random.randint(3, 9)
        if (a != b) and (a !=6):
            d = (a+b)/2-6
            if d != 0 or a != c:
                break
    

    a = str(a)
    moves += " " + replacements.get(a, a)
    a = int(a)
    c = b
    b = a 

print(moves)

