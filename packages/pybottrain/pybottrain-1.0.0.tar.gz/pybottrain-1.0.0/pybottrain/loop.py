import time
from random import *

def learn_loop(num1, num2, num3, code):
    while True:
        aleatorio = randint(num1, num2)
        objetivo = num3
        if aleatorio == objetivo:
            eval(code)
        return False

def learn_wait_loop(num1, num2, num3, tempo, code):
    while True:
        time.sleep(tempo)
        aleatorio = randint(num1, num2)
        objetivo = num3
        if aleatorio == objetivo:
            eval(code)