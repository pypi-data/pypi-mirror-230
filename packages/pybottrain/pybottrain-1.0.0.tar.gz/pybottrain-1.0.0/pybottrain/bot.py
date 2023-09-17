from random import *
import time

def learn(num1, num2, num3, code):
    aleatorio = randint(num1, num2)
    igual = num3
    if aleatorio == igual:
        eval(code)
        return True
    return False

def learn2(num1, num2, num3, code):
    alea = randint(num1, num2)
    objet = num3
    if alea <= objet:
        eval(code)
        return True
    return False

def learn3(num1, num2, num3, code):
    aleato = randint(num1, num2)
    objetivo = num3
    if aleato >= objetivo:
        eval(code)
        return True
    return False

def learn_else(numero1, numero2, numero3, code1, code2):
    aleatorio = randint(numero1, numero2)
    objetivo = numero3
    if aleatorio == objetivo:
        eval(code1)
        return True
    else:
        eval(code2)
        return False
    
def learn_wait(numero1, numero2, numero3, tempo, code):
    time.sleep(tempo)
    aleatorio = randint(numero1, numero2)
    objetivo = numero3
    if aleatorio == objetivo:
        eval(code)
        return True
    return False
