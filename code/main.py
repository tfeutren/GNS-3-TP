import json
from type_objet import AS, Routeur



def creationListAs(*args):

    listAs =[]

    for elem in args:
        listAs.append(elem)

    return listAs


def initConfigRouteur(As):

    for routeur in As.listeRouteurs:
        routeur.ajoutListe("enable")
        routeur.ajoutListe("clear bgp ipv6 unicast *")
        routeur.ajoutListe("configure terminal")
        routeur.ajoutListe("ipv6 unicast-routing")
        if routeur.ASBR == True:
                routeur.ajoutListe("ipv6 route {}".format(As.addReseau))
            
        configProtocol(routeur,As.protocol)
        configProtocol(routeur,"bgp",As)
        configAddress(routeur,As)


def configAddress(routeur,As):

    indexNeighbors = 0

    for interface in routeur.interfaces:

        routeur.ajoutListe("interface GigabiteEthernet{}/0".format(str(interface)))
        routeur.ajoutListe("no shutdown")
        routeur.ajoutListe("ipv6 enable")

        if routeur.neighbors[indexNeighbors] > routeur.ID[1]:
            routeur.ajoutListe("ipv6 adress {}:{}{}::{}".format(str(As.addReseau)[:8],str(routeur.ID[1]),str(routeur.neighbors[indexNeighbors]),str(routeur.ID[1])))

        else:
            routeur.ajoutListe("ipv6 adress {}:{}{}::{}".format(str(As.addReseau)[:8],str(routeur.neighbors[indexNeighbors]),str(routeur.ID[1]),str(routeur.ID[1])))

        if As.protocol == "rip":
            routeur.ajoutListe("ipv6 rip 1 enable")
        elif As.protocol == "ospf":
            routeur.ajoutListe("ipv6 ospf 1 area 1")
        
        routeur.ajoutListe("exit")

        indexNeighbors+=1
    
    routeur.ajoutListe("interface loopback 0")
    routeur.ajoutListe("no shutdown")
    routeur.ajoutListe("ipv6 enable")
    routeur.ajoutListe("ipv6 address {}::{}/128".format(str(routeur.ID[0]),str(routeur.ID[1])))

    if As.protocol == "rip":
        routeur.ajoutListe("ipv6 rip 1 enable")
    elif As.protocol == "ospf":
        routeur.ajoutListe("ipv6 ospf 1 area 1")

    routeur.ajoutListe("exit")






def configProtocol(routeur,protocol,As=None):
    try:
        if protocol == "rip":
            routeur.ajoutListe("ipv6 router rip 1")
            routeur.ajoutListe("redistribute connected")
            routeur.ajoutListe("exit")

        elif protocol == "ospf":
            routeur.ajoutListe("ipv6 router ospf 1")
            routeur.ajoutListe("router-id {}.{}.{}.{}".format(str(routeur.ID[1]),str(routeur.ID[1]),str(routeur.ID[1]),str(routeur.ID[1])))
            routeur.ajoutListe("exit")
        
        elif protocol == "bgp":
            routeur.ajoutListe("router bgp {}".format(routeur.ID[0]))
            routeur.ajoutListe("no bgp default ipv4-unicast")
            routeur.ajoutListe("ipv6 router-id {}.{}.{}.{}".format(str(routeur.ID[1]),str(routeur.ID[1]),str(routeur.ID[1]),str(routeur.ID[1])))

            if routeur.ASBR == True:
                routeur.ajoutListe("à faire")
            else:
                routeur.ajoutListe("à faire")

            routeur.ajoutListe("address-family ipv6 unicast")

            if routeur.ASBR == True:
                routeur.ajoutListe("à faire")
                routeur.ajoutListe("network {}".format(As.addReseau))
            else:
                routeur.ajoutListe("à faire")

            routeur.ajoutListe("exit")
            routeur.ajoutListe("exit")

    except:
        print("ERROR configProtocol {} {}".format(protocol,str(routeur.ID)))
    


if __name__ == "__main__":
    
    # Définition de nos routeurs à partir de la classe Routeur
    "[ n°AS(1 ou 2) , n°Routeur ], [ <gigabitInterfaces> ] , estASBR? "
    R1 = Routeur([1,1],[1,2],[2,3],False)
    R2 = Routeur([1,2],[1,2,3],[1,3,4],False)
    R3 = Routeur([1,3],[1,2,3],[1,2,5],False)
    R4 = Routeur([1,4],[1,2,3],[2,5,6,7],False)
    R5 = Routeur([1,5],[1,2,3],[3,4,6,7],False)
    R6 = Routeur([1,6],[1,2,4],[4,5,8],True)
    R7 = Routeur([1,7],[1,2,4],[4,5,9],True)
    R8 = Routeur([2,8],[1,2,4],[6,10,11],True)
    R9 = Routeur([2,9],[1,2,4],[7,10,11],True)
    R10 = Routeur([2,10],[1,2,3,4],[8,9,11,12],False)
    R11 = Routeur([2,11],[1,2,3,4],[8,9,10,13],False)
    R12 = Routeur([2,12],[1,2,3],[10,13,14],False)
    R13 = Routeur([2,13],[1,2,3],[11,12,14],False)
    R14 = Routeur([2,14],[1,2],[12,13],False)

    # Définition de nos AS à partir de la classe AS
    ASX = AS(1,"rip",[R1,R2,R3,R4,R5,R6,R7],'2020:0:1::/48')
    ASY = AS(2,"ospf",[R8,R9,R10,R11,R12,R13,R14],'2020:0:2::/48')

    listAs = creationListAs(ASX, ASY)
        
    # Ecrire les config des AS
    for As in listAs :

        initConfigRouteur(As)

        for elem in As.listeRouteurs:
            with open("ConfigAutoR{}.txt".format(str(elem.ID[1])), 'w') as file:
                for line in elem.liste:
                    file.write(line+'\n')


