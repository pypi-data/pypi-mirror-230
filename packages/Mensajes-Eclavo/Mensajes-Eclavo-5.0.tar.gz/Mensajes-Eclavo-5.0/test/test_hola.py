import unittest        
from mensaje.hola.saludos import *
from mensaje.adios.despedidas import *
#si queremsos importa todas las funcion añadimos un asterisco    saludar*

class PruebasHola(unittest.TestCase):
    def test_generar_array(self):
        np.testing.assert_array_equal(
         np.array([0,1,2,3,4,5]), generar_array(6))

saludar()
saludo()

despedir()
despedidas()
