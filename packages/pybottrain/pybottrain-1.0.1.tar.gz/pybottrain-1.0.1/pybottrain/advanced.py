import random

learned_requests = {}

def learn(numero1, numero2, numero_objetivo, codigo_if, nivel_aprendizado=1.0):
    aleatorio = random.randint(numero1, numero2)
    objetivo = numero_objetivo
    if aleatorio == objetivo:
        if random.random() <= nivel_aprendizado:
            exec(codigo_if)
            return True
    return False

def learn_else(numero1, numero2, numero_objetivo, codigo_if, codigo_else, nivel_aprendizado=1.0):
    aleatorio = random.randint(numero1, numero2)
    objetivo = numero_objetivo
    if aleatorio == objetivo:
        if random.random() <= nivel_aprendizado:
            exec(codigo_if)
            return True
    else:
        if random.random() <= nivel_aprendizado:
            exec(codigo_else)
            return False
    return False

def learn_chat(user_input, request, response):
    if user_input.lower() == request:
        print(response)