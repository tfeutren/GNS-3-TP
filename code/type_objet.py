# Définition de la classe AS

class AS:
    """
    Classe représentant un AS
    ## Constructeur :
    :param number: Numéro de l'AS (int)
    :param protocol: Protocole utilisé par l'AS (ex: BGP) (str)
    :param listeRouteurs: Liste des routeurs dans l'AS (list)
    :param addReseau: Adresses de réseau utilisées dans l'AS (list)
    """
    
    def __init__(self,number,protocol,listeRouteurs,addReseau):
        self.number = number
        self.protocol = protocol
        self.listeRouteurs = listeRouteurs
        self.addReseau = addReseau

# Définition de la classe Routeur

class Routeur:
    """
    Classe représentant un Routeur :
    ## Constructeur :
    :param ID: Tuple contenant le numéro d'AS et le numéro de routeur (int, int)
    :param interfaces: Liste des interfaces (list)
    :param neighbors: Liste des voisins (list)
    :param ASBR: Booléen indiquant si le routeur est un ASBR (bool, optional)
    :param neighborsEbgp: Liste des voisins eBGP (list, optional)
    :ivar liste: Liste vide, contient les lignes de code cisco IOS à écrire (list)
    ## Méthode
    ### ajoutListe :
    Permet d'ajouter des éléments à self.liste
    :param element: Elément à ajouter (str)
    :return: None
    """
    def __init__(self, ID, interfaces, neighbors, ASBR = False ,neighborsEbgp=[]):
        self.ID = ID
        self.interfaces = interfaces
        self.neighbors= neighbors
        self.neighborsEbgp = neighborsEbgp
        self.ASBR = ASBR
        self.liste = []

    def ajoutListe(self, element):
        self.liste.append(element)