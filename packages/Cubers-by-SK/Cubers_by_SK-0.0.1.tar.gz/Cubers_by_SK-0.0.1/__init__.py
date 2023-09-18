import random
import keyboard
import time
def generatescramblethreebbythree():
    x=0
    print("Scramble:")
    moves=["U", "U'", "R", "R'", "L", "L'", "D", "D'", "F", "F'", "B", "B'"]
    for x in range(10):
        move=random.choice(moves)
        print(move)
    x=0
def generatescramblefourbyfour():
    x=0
    print("Scramble:")
    moves=["U", "U'", "R", "R'", "L", "L'", "D", "D'", "F", "F'", "B", "B'", "u", "u'", "r", "r'", "l", "l'", "d", "d'", "f", "f'", "b", "b'"]
    for x in range(15):
        move=random.choice(moves)
        print(move)
    x=0
def timer(nameofkey:str):
    y=0
    while True:
        time.sleep(1)
        y+=1
        print(y)
        if keyboard.is_pressed(nameofkey):
            break
        
        
    