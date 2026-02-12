import win32api
import mouse
from time import sleep
import random
from random import randint             
         
# Recoil
runter =[13,13,13,13,13,13,13,13,13,13,13,14,14,14,14,14,14,14,14,14,14,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13]
         
# vars
count = 0
EinAus = False
jaornein = randint(0,1)
     
         
         
# Loop
count = 0
while True:
        if win32api.GetAsyncKeyState(ord('0')):
                EinAus = not EinAus
                sleep(0.2)
                print('On')
        sleep(0.2)
        while EinAus is True:
                count = 0
                while mouse.is_pressed(button='left'):
                    if count < 40:
                        jaornein = randint(0,1)
                        if jaornein == 1:
                            randomized = randint(0,5)
                        elif jaornein == 0:
                            randomized = random.uniform(0,-5)    
                        print(randomized)
                        ammount = runter[count]
                        if jaornein == 1:
                            ammount = ammount + randomized
                        elif jaornein == 0:
                            ammount = ammount - randomized
                        ammountFinal = int(round(ammount))
                        win32api.mouse_event(0x0001,0,ammountFinal)
                        sleep(0.10)    
                    count = count + 1
                    if count > 40:
                        count = 0
                        ammount = 0   
                                               
                if win32api.GetAsyncKeyState(ord('0')):
                        print('Out')
                        EinAus = not EinAus
                        sleep(0.2)
                        break
                sleep(0.1)
