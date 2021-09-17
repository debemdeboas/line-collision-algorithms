# ************************************************
#   Ponto.py
#   Define a classe Ponto
#   Autor: Márcio Sarroglia Pinho
#       pinho@pucrs.br
# ************************************************


""" Classe Ponto """
class Ponto:   
    def __init__(self, x=0,y=0,z=0):
        self.x = x
        self.y = y
        self.z = z
    

    """ Imprime os valores de cada eixo do ponto """
    def imprime(self):
        print (self.x, self.y, self.z)


    """ Define os valores dos eixos do ponto """
    def set(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z
