import json

# Définition des deux liste qui correspond au deux fichier voulu
ASX = []
ASY = []

# Définition de la classe Routeur
class Routeur:
    def __init__(self, ID, interfaces, isASBR):
        self.ID = ID
        self.interfaces = interfaces
        self.isASBR = isASBR

# Définition de mes routeurs à partir de la classe Routeur
mesRouteurs = { "R1" : Routeur([1,1],[1,2],False),
                "R2" : Routeur([1,2],[1,2,3],False)
 }

# Ecriture pour chaque routeur en fonction de leurs paramètres
for k in mesRouteurs:
    ASX.append('')
    ASX.append( str(  k ) )
    ASX.append('')
    ASX.append("enable")
    ASX.append("clear bgp ipv6 unicast *")
    ASX.append("configure terminal")


# Ecrire dans le fichier text.txt
with open('text.txt', 'w') as file:
    for line in ASX:
        file.write(line+'\n')

