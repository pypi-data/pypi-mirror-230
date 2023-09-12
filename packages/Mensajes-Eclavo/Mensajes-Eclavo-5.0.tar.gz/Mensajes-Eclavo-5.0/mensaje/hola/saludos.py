
import numpy as np
def saludar():
    print("hola te saludo desde saludos.saludar()")

def prueb():
    print("esto es una prueba de la nueva funcion")

def generar_array(numeros):
    return np.arange(numeros)

class saludo:
     def __init__(self):
         print("hola te saludo de sde saludo.__init__()")

if __name__=='__main__': # name hace referencia al nombre del modulo
    print(generar_array(5))