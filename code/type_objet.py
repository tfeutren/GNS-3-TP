# Définition de la classe AS

class AS:
    
    def __init__(self,number,protocol,listeRouteurs,addReseau):
        self.number = number
        self.protocol = protocol
        self.listeRouteurs = listeRouteurs
        self.addReseau = addReseau

# Définition de la classe Routeur

class Routeur:

    def __init__(self, ID, interfaces, neighbors, ASBR):
        self.ID = ID
        self.interfaces = interfaces #liste interfaces
        self.neighbors= neighbors #liste neighbors
        self.ASBR = ASBR
        self.liste = []

    def ajoutListe(self, element):
        self.liste.append(element)