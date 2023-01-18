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
                routeur.ajoutListe("ipv6 route {} Null0".format(As.addReseau))
            
        configProtocol(routeur,As.protocol)
        configProtocol(routeur,"bgp",As)
        configAddress(routeur,As)
        routeur.ajoutListe("end")


def configAddress(routeur,As):

    try:
        indexNeighbors = 0
        indexEbgpNeighbors = 0

        for interface in routeur.interfaces:

            routeur.ajoutListe("interface GigabiteEthernet{}/0".format(str(interface)))
            routeur.ajoutListe("no shutdown")
            routeur.ajoutListe("ipv6 enable")

            if indexNeighbors < len(routeur.neighbors):
                if routeur.neighbors[indexNeighbors] > routeur.ID[1]:
                    routeur.ajoutListe("ipv6 address {}:{}{}::{}/64".format(str(As.addReseau)[:8],str(routeur.ID[1]),str(routeur.neighbors[indexNeighbors]),str(routeur.ID[1])))

                else:
                    routeur.ajoutListe("ipv6 address {}:{}{}::{}/64".format(str(As.addReseau)[:8],str(routeur.neighbors[indexNeighbors]),str(routeur.ID[1]),str(routeur.ID[1])))

                if As.protocol == "rip":
                    routeur.ajoutListe("ipv6 rip 1 enable")
                elif As.protocol == "ospf":
                    routeur.ajoutListe("ipv6 ospf 1 area 1")

                indexNeighbors = indexNeighbors + 1

            elif indexEbgpNeighbors < len(routeur.neighborsEbgp):
                if (routeur.neighborsEbgp[indexEbgpNeighbors])[1] > routeur.ID[1]:
                    routeur.ajoutListe("ipv6 address 2023:0:{}{}::{}/64".format(str(routeur.ID[1]),str((routeur.neighborsEbgp[indexEbgpNeighbors])[1]),str(routeur.ID[1])))

                else:
                    routeur.ajoutListe("ipv6 address 2023:0:{}{}::{}/64".format(str((routeur.neighborsEbgp[indexEbgpNeighbors])[1]),str(routeur.ID[1]),str(routeur.ID[1])))

                indexEbgpNeighbors+=1
            

            routeur.ajoutListe("exit")
        
        routeur.ajoutListe("interface loopback 0")
        routeur.ajoutListe("no shutdown")
        routeur.ajoutListe("ipv6 enable")
        routeur.ajoutListe("ipv6 address {}::{}/128".format(str(routeur.ID[0]),str(routeur.ID[1])))

        if As.protocol == "rip":
            routeur.ajoutListe("ipv6 rip 1 enable")
        elif As.protocol == "ospf":
            routeur.ajoutListe("ipv6 ospf 1 area 1")

        routeur.ajoutListe("exit")
    
    except:
        print("ERROR configAddress {} {}".format(str(As.number),str(routeur.ID)))






def configProtocol(routeur,protocol,As=None):
    #try:
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
            routeur.ajoutListe("bgp router-id {}.{}.{}.{}".format(str(routeur.ID[1]),str(routeur.ID[1]),str(routeur.ID[1]),str(routeur.ID[1])))

            if routeur.ASBR == True:
                
                for r in As.listeRouteurs:
                    if r != routeur:
                        routeur.ajoutListe("neighbor {}::{} remote-as {}".format(str(As.number),str(r.ID[1]),str(As.number)))
                        routeur.ajoutListe("neighbor {}::{} update-source loopback 0".format(str(As.number),str(r.ID[1])))
                    
                for lienBGP in routeur.neighborsEbgp:
                    if lienBGP[1]>routeur.ID[1]:
                        routeur.ajoutListe("neighbor 2023:0:{}{}::{} remote-as {}".format(str(routeur.ID[1]),str(lienBGP[1]),str(lienBGP[1]),str(lienBGP[0])))
                    else:
                        routeur.ajoutListe("neighbor 2023:0:{}{}::{} remote-as {}".format(str(lienBGP[1]),str(routeur.ID[1]),str(lienBGP[1]),str(lienBGP[0])))
            

            else:
                for r in As.listeRouteurs: 
                    if r.ASBR == True:
                        routeur.ajoutListe("neighbour {}::{} remote-as {}".format(str(As.number),str(r.ID[1]),str(As.number)))
                        routeur.ajoutListe("neighbour {}::{} update-source loopback 0".format(str(As.number),str(r.ID[1])))
                    

            routeur.ajoutListe("address-family ipv6 unicast")


            if routeur.ASBR == True:

                for r in As.listeRouteurs:
                    if r != routeur:
                        routeur.ajoutListe("neighbor {}::{} activate".format(str(As.number),str(r.ID[1])))
                    
                for lienBGP in routeur.neighborsEbgp:
                    if lienBGP[1]>routeur.ID[1]:
                        routeur.ajoutListe("neighbor 2023:0:{}{}::{} activate".format(str(routeur.ID[1]),str(lienBGP[1]),str(lienBGP[1])))
                    else:
                        routeur.ajoutListe("neighbor 2023:0:{}{}::{} activate".format(str(lienBGP[1]),str(routeur.ID[1]),str(lienBGP[1])))
   
                
                routeur.ajoutListe("network {}".format(str(As.addReseau)))

            else:
                for r in As.listeRouteurs: 
                    if r.ASBR == True:
                        routeur.ajoutListe("neighbour {}::{} activate".format(str(As.number),str(r.ID[1])))
                    
            routeur.ajoutListe("exit")
            routeur.ajoutListe("exit")

    #except:
        #print("ERROR configProtocol {} {}".format(protocol,str(routeur.ID)))
    


if __name__ == "__main__":
    
    # Définition de nos routeurs à partir de la classe Routeur
    "[ n°AS(1 ou 2) , n°Routeur ], [ <gigabitInterfaces> ] , estASBR? "
    R1 = Routeur([1,1],[1,2],[2,3])
    R2 = Routeur([1,2],[1,2,3],[1,3,4])
    R3 = Routeur([1,3],[1,2,3],[1,2,5])
    R4 = Routeur([1,4],[1,2,3],[2,5,6,7])
    R5 = Routeur([1,5],[1,2,3],[3,4,6,7])
    R6 = Routeur([1,6],[1,2,4],[4,5],True, [(2,8)])
    R7 = Routeur([1,7],[1,2,4],[4,5],True, [(2,9)])
    R8 = Routeur([2,8],[1,2,4],[10,11],True, [(1,6)])
    R9 = Routeur([2,9],[1,2,4],[10,11],True, [(1,7)])
    R10 = Routeur([2,10],[1,2,3,4],[8,9,11,12])
    R11 = Routeur([2,11],[1,2,3,4],[8,9,10,13])
    R12 = Routeur([2,12],[1,2,3],[10,13,14])
    R13 = Routeur([2,13],[1,2,3],[11,12,14])
    R14 = Routeur([2,14],[1,2],[12,13])

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


