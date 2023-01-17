import json

# Définition de la classe AS
class AS:
    def __init__(self,number,protocol):
        self.number = number
        self.protocol = protocol
        self.liste = []
    def ajoutListe(self, element):
        self.liste.append(element)

# Définition de nos AS à partir de la classe AS
mesAS = { "ASX" : AS(1,"rip"),
          "ASY" : AS(2,"ospf")}

# Définition de la classe Routeur
class Routeur:
    def __init__(self, ID, interfaces, isASBR):
        self.ID = ID
        self.interfaces = interfaces
        self.isASBR = isASBR

# Définition de nos routeurs à partir de la classe Routeur
"[ n°AS(1 ou 2) , n°Routeur ], [ <gigabitInterfaces> ] , estASBR? "
mesRouteurs = { "R1" : Routeur([1,1],[1,2],False),
                "R2" : Routeur([1,2],[1,2,3],False),
                "R3" : Routeur([1,3],[1,2,3],False),
                "R4" : Routeur([1,4],[1,2,3,4],False),
                "R5" : Routeur([1,5],[1,2,3,4],False),
                "R6" : Routeur([1,6],[1,2,4],True),
                "R7" : Routeur([1,7],[1,2,4],True),
                "R8" : Routeur([2,8],[1,2,4],True),
                "R9" : Routeur([2,9],[1,2,4],True),
                "R10" : Routeur([2,10],[1,2,3,4],False),
                "R11" : Routeur([2,11],[1,2,3,4],False),
                "R12" : Routeur([2,12],[1,2,3],False),
                "R13" : Routeur([2,13],[1,2,3],False),
                "R14" : Routeur([2,14],[1,2],False)}

# Ecriture config AS pour chaque routeur en fonction de leurs paramètres
for root in mesRouteurs:
    for elem in mesAS:
        if mesRouteurs[root].ID[0] == mesAS[elem].number :
            mesAS[elem].ajoutListe('')
            mesAS[elem].ajoutListe( str(  root ) )
            mesAS[elem].ajoutListe('')
            mesAS[elem].ajoutListe("enable")
            mesAS[elem].ajoutListe("clear bgp ipv6 unicast *")
            mesAS[elem].ajoutListe("configure terminal")
            mesAS[elem].ajoutListe("ipv6 unicast-routing")
            if mesRouteurs[str(root)].isASBR == False:
                mesAS[elem].ajoutListe("ipv6 router rip 1")
            else:
                mesAS[elem].ajoutListe("ipv6 route 2020:0:1::/48 Null0")
        
# Ecrire les config des AS
for elem in mesAS:
    with open("ConfigAuto{}.txt".format(str(elem)), 'w') as file:
        for line in mesAS[elem].liste:
            file.write(line+'\n')
