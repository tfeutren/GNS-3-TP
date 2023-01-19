# -------------------------------- #
# ** Configuration des routeurs ** #
# -------------------------------- #

# Importation des modules

import json
from type_objet import AS, Routeur

# ----------------------------------

#def descriptionJSON(Path):

#création de la liste des As déclarées dans le fichier .json
def creationListAs(*args):

    listAs =[]

    for elem in args:
        listAs.append(elem)

    return listAs

#génération config des routeurs d'une AS
def configRouteur(As):

    idNewNetwork = 1

    for routeur in As.listeRouteurs:
        routeur.ajoutListe("enable")
        routeur.ajoutListe("clear bgp ipv6 unicast *")
        routeur.ajoutListe("configure terminal")
        routeur.ajoutListe("ipv6 unicast-routing")
        if routeur.ASBR == True:
                routeur.ajoutListe("ipv6 route {} Null0".format(As.addReseau))
            
        idNewNetwork=idNewNetwork + configAddress(routeur,As,idNewNetwork)
        configProtocol(routeur,As.protocol)
        configProtocol(routeur,"bgp",As)
        
        routeur.ajoutListe("end")


#génération config address sur interface du routeur
def configAddress(routeur,As,idNewNetwork):

    try:
        updateIndexNetwork = 0
        indexNeighbors = 0
        indexEbgpNeighbors = 0

        # configuration de chaque interface du routeur
        for interface in routeur.interfaces:

            routeur.ajoutListe("interface {}".format(str(interface)))
            routeur.ajoutListe("no shutdown")
            routeur.ajoutListe("ipv6 enable")

            # configuration des interfaces intra-domaines
            if indexNeighbors < len(routeur.neighbors):

                if (routeur.neighbors[indexNeighbors])[1] == None:
                    routeur.ajoutListe("ipv6 address {}:{}::{}/64".format(str(As.addReseau)[:8],str(idNewNetwork),str(routeur.ID[1])))

                    for r in As.listeRouteurs:
                        if r.Id[1] == (routeur.neighbors[indexNeighbors])[1]:

                            for neighbor in r.interfaces:
                                if neighbor[0] == routeur.ID[1] and neighbor[1] == None:
                                    neighbor[1]='ipv6 address {}:{}::{}/64'.format(str(As.addReseau)[:8],str(idNewNetwork),str(r.ID[1]))

                    if As.protocol == "rip":
                        routeur.ajoutListe("ipv6 rip 1 enable")
                    elif As.protocol == "ospf":
                        routeur.ajoutListe("ipv6 ospf 1 area 1")
                    
                indexNeighbors+=1
                updateIndexNetwork+=1

            # configuration des interfaces inter-domaines
            elif indexEbgpNeighbors < len(routeur.neighborsEbgp):
                if (routeur.neighborsEbgp[indexEbgpNeighbors])[1] > routeur.ID[1]:
                    routeur.ajoutListe("ipv6 address 2023:0:{}::{}/64".format(str(idNewNetwork),str(routeur.ID[1])))

                else:
                    routeur.ajoutListe("ipv6 address 2023:0:{}::{}/64".format(str(idNewNetwork),str(routeur.ID[1])))

                indexEbgpNeighbors+=1
                updateIndexNetwork+=1
            
            routeur.ajoutListe("exit")
        
        routeur.ajoutListe("interface loopback 0")
        routeur.ajoutListe("no shutdown")
        routeur.ajoutListe("ipv6 enable")
        routeur.ajoutListe("ipv6 address {}::{}/128".format(str(routeur.ID[0]),str(routeur.ID[1])))

        #configuration des interfaces suivant protocol de routage utilisé
        if As.protocol == "rip":
            routeur.ajoutListe("ipv6 rip 1 enable")
        elif As.protocol == "ospf":
            routeur.ajoutListe("ipv6 ospf 1 area 1")

        routeur.ajoutListe("exit")

        return updateIndexNetwork
    
    except:
        print("ERROR configAddress {} {}".format(str(As.number),str(routeur.ID)))





#génération config protocol du routeur
def configProtocol(routeur,protocol,As=None):
    try:

        #configuration protocol rip
        if protocol == "rip":
            routeur.ajoutListe("ipv6 router rip 1")
            routeur.ajoutListe("redistribute connected")
            routeur.ajoutListe("exit")

        #configuration protocol ospf
        elif protocol == "ospf":
            routeur.ajoutListe("ipv6 router ospf 1")
            routeur.ajoutListe("router-id {}.{}.{}.{}".format(str(routeur.ID[1]),str(routeur.ID[1]),str(routeur.ID[1]),str(routeur.ID[1])))
            routeur.ajoutListe("exit")
        
        #configuration protocol bgp
        elif protocol == "bgp":
            routeur.ajoutListe("router bgp {}".format(routeur.ID[0]))
            routeur.ajoutListe("no bgp default ipv4-unicast")
            routeur.ajoutListe("bgp router-id {}.{}.{}.{}".format(str(routeur.ID[1]),str(routeur.ID[1]),str(routeur.ID[1]),str(routeur.ID[1])))
            
            #déclaration neighbors bgp pour routeurs
            for r in As.listeRouteurs:
                if r != routeur:
                    routeur.ajoutListe("neighbor {}::{} remote-as {}".format(str(As.number),str(r.ID[1]),str(As.number)))
                    routeur.ajoutListe("neighbor {}::{} update-source loopback 0".format(str(As.number),str(r.ID[1])))
                    
            #complément déclaration neighbors bgp pour ASBR
            if routeur.ASBR == True:
                for lienBGP in routeur.neighborsEbgp:
                    if lienBGP[1]>routeur.ID[1]:
                        routeur.ajoutListe("neighbor 2023:0:{}{}::{} remote-as {}".format(str(routeur.ID[1]),str(lienBGP[1]),str(lienBGP[1]),str(lienBGP[0])))
                    else:
                        routeur.ajoutListe("neighbor 2023:0:{}{}::{} remote-as {}".format(str(lienBGP[1]),str(routeur.ID[1]),str(lienBGP[1]),str(lienBGP[0])))
                    

            routeur.ajoutListe("address-family ipv6 unicast")

            #activation neighbors bgp pour routeurs
            for r in As.listeRouteurs:
                if r != routeur:
                    routeur.ajoutListe("neighbor {}::{} activate".format(str(As.number),str(r.ID[1])))

            #complément activation neighbors bgp pour ASBR
            if routeur.ASBR == True:     
                for lienBGP in routeur.neighborsEbgp:
                    if lienBGP[1]>routeur.ID[1]:
                        routeur.ajoutListe("neighbor 2023:0:{}{}::{} activate".format(str(routeur.ID[1]),str(lienBGP[1]),str(lienBGP[1])))
                    else:
                        routeur.ajoutListe("neighbor 2023:0:{}{}::{} activate".format(str(lienBGP[1]),str(routeur.ID[1]),str(lienBGP[1])))
   
                #déclaration réseaux 
                routeur.ajoutListe("network {}".format(str(As.addReseau)))
                    
            routeur.ajoutListe("exit")
            routeur.ajoutListe("exit")

    except:
        print("ERROR configProtocol {} {}".format(protocol,str(routeur.ID)))
    


if __name__ == "__main__":
    
    # Définition de nos routeurs à partir de la classe Routeur
    R1 = Routeur([1,1],['GigabiteEthernet1/0','GigabiteEthernet2/0'],[(2,None),(3,None)])
    R2 = Routeur([1,2],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0'],[(1,None),(3,None),(4,None)])
    R3 = Routeur([1,3],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0'],[(1,None),(2,None),(5,None)])
    R4 = Routeur([1,4],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0','GigabiteEthernet4/0'],[(2,None),(5,None),(6,None),(7,None)])
    R5 = Routeur([1,5],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0','GigabiteEthernet4/0'],[(3,None),(4,None),(6,None),(7,None)])
    R6 = Routeur([1,6],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0'],[(4,None),(5,None)],True, [(2,8,None)])
    R7 = Routeur([1,7],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0'],[(4,None),(5,None)],True, [(2,9,None)])
    R8 = Routeur([2,8],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0'],[(10,None),(11,None)],True, [(1,6,None)])
    R9 = Routeur([2,9],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0'],[(10,None),(11,None)],True, [(1,7,None)])
    R10 = Routeur([2,10],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0','GigabiteEthernet4/0'],[(8,None),(9,None),(11,None),(12,None)])
    R11 = Routeur([2,11],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0','GigabiteEthernet4/0'],[(8,None),(9,None),(10,None),(13,None)])
    R12 = Routeur([2,12],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0'],[(10,None),(13,None),(14,None)])
    R13 = Routeur([2,13],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0'],[(11,None),(12,None),(14,None)])
    R14 = Routeur([2,14],['GigabiteEthernet1/0','GigabiteEthernet2/0'],[(12,None),(13,None)])

    # Définition de nos AS à partir de la classe AS
    ASX = AS(1,"rip",[R1,R2,R3,R4,R5,R6,R7],'2020:0:1::/48')
    ASY = AS(2,"ospf",[R8,R9,R10,R11,R12,R13,R14],'2020:0:2::/48')

    #listAs = descriptJSON("Path")

    listAs = creationListAs(ASX, ASY)
        
    # Ecrire les config des AS
    for As in listAs :

        configRouteur(As)

        for elem in As.listeRouteurs:
            with open("ConfigAutoR{}.txt".format(str(elem.ID[1])), 'w') as file:
                for line in elem.liste:
                    file.write(line+'\n')


#addressage en hexa en incrementant de 1