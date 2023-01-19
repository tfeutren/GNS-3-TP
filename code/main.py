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
def configRouteur(As,listeAs,idNewNetwork):

    for routeur in As.listeRouteurs:
        routeur.ajoutListe("enable")
        routeur.ajoutListe("clear bgp ipv6 unicast *")
        routeur.ajoutListe("configure terminal")
        routeur.ajoutListe("ipv6 unicast-routing")
        if routeur.ASBR == True:
                routeur.ajoutListe("ipv6 route {} Null0".format(As.addReseau))
            
        idNewNetwork=idNewNetwork + configAddress(routeur,As,listeAs,idNewNetwork)
        print(str(idNewNetwork)+" "+str(routeur.ID[1]))
        configProtocol(routeur,As.protocol)
        configProtocol(routeur,"bgp",As)
        
        routeur.ajoutListe("end")

    return idNewNetwork


#génération config address sur interface du routeur
def configAddress(routeur,As,listeAs,idNewNetwork):

    #try:
        updateIndexNetwork = 0
        indexNeighbors = 0
        indexEbgpNeighbors = 0

        # configuration de chaque interface du routeur
        for interface in routeur.interfaces:

            routeur.ajoutListe("interface {}".format(str(interface)))
            routeur.ajoutListe("no shutdown")
            routeur.ajoutListe("ipv6 enable")

            # configuration des interfaces intra-domaines
            if indexNeighbors < len(routeur.neighbors) :
                if (routeur.neighbors[indexNeighbors])[1] == "":

                    (routeur.neighbors[indexNeighbors])[1] = "{}:{}::{}/64".format(str(As.addReseau)[:8],str(idNewNetwork+updateIndexNetwork),str(routeur.ID[1]))
                    routeur.ajoutListe("ipv6 address {}".format(str((routeur.neighbors[indexNeighbors])[1])))

                    for r in As.listeRouteurs:
                        if r.ID[1] == (routeur.neighbors[indexNeighbors])[0]:
                            for neighbor in r.neighbors:
                                if neighbor[0] == routeur.ID[1] and neighbor[1] == "":
                                    neighbor[1] = "{}:{}::{}/64".format(str(As.addReseau)[:8],str(idNewNetwork+updateIndexNetwork),str(r.ID[1]))
                                    
                    if As.protocol == "rip":
                        routeur.ajoutListe("ipv6 rip 1 enable")
                    elif As.protocol == "ospf":
                        routeur.ajoutListe("ipv6 ospf 1 area 1")

                    updateIndexNetwork+=1       
            
                else:
                    routeur.ajoutListe("ipv6 address {}".format(str((routeur.neighbors[indexNeighbors])[1])))
                
                indexNeighbors+=1
                

            # configuration des interfaces inter-domaines
            elif indexEbgpNeighbors < len(routeur.neighborsEbgp):
                if (routeur.neighborsEbgp[indexEbgpNeighbors])[2] == "":

                    (routeur.neighborsEbgp[indexEbgpNeighbors])[2] = "2023:0:{}::{}/64".format(str(idNewNetwork+updateIndexNetwork),str(routeur.ID[1]))
                    routeur.ajoutListe("ipv6 address {}".format(str((routeur.neighborsEbgp[indexEbgpNeighbors])[2])))

                    for As in listeAs:
                        if As.number == (routeur.neighborsEbgp[indexEbgpNeighbors])[0]:
                            for r in As.listeRouteurs:
                                if r.ID[1] == (routeur.neighborsEbgp[indexEbgpNeighbors])[1]:
                                    for neighborEbgp in r.neighborsEbgp:
                                        if neighborEbgp[1] == routeur.ID[1] and neighborEbgp[2]=="":
                                            neighborEbgp[2]="2023:0:{}::{}/64".format(str(idNewNetwork+updateIndexNetwork),str(r.ID[1]))
                    updateIndexNetwork+=1
                    
                else:
                    routeur.ajoutListe("ipv6 address {}".format(str((routeur.neighborsEbgp[indexEbgpNeighbors])[2])))

                indexEbgpNeighbors+=1
            
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
    
    #except:
    #    print("ERROR configAddress {} {}".format(str(As.number),str(routeur.ID)))





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
                    routeur.ajoutListe("neighbor {}{} remote-as {}".format(str(lienBGP[2])[:11],str(lienBGP[1]),str(lienBGP[0])))
                    

            routeur.ajoutListe("address-family ipv6 unicast")

            #activation neighbors bgp pour routeurs
            for r in As.listeRouteurs:
                if r != routeur:
                    routeur.ajoutListe("neighbor {}::{} activate".format(str(As.number),str(r.ID[1])))

            #complément activation neighbors bgp pour ASBR
            if routeur.ASBR == True:     
                for lienBGP in routeur.neighborsEbgp:
                    routeur.ajoutListe("neighbor {}{} activate".format(str(lienBGP[2])[:11],str(lienBGP[1])))

   
                #déclaration réseaux 
                routeur.ajoutListe("network {}".format(str(As.addReseau)))
                    
            routeur.ajoutListe("exit")
            routeur.ajoutListe("exit")

    except:
        print("ERROR configProtocol {} {}".format(protocol,str(routeur.ID)))
    
#Importer les données dans les fichiers JSON
def appelJSON(nomFichier):
    #Appel de nos AS à partir du fichier JSON
    with open(nomFichier) as json_file_Root:
        dataRoot = json.load(json_file_Root)
    
    for i, router in enumerate(dataRoot,start=1):
        locals()[f'R{i}'] = Routeur(router['ID'] ,
                                    router['interfaces'],
                                    router['neighbors'], 
                                    router.get('ASBR', False), 
                                    router.get('neighborsEbgp', []))
    
    #Appel de nos AS à partir du fihcier JSON
    with open('fichier_intention_AS.json') as json_file_AS:
        dataAS = json.load(json_file_AS)
    
    locals()[f'listeAs'] = []
    for i, As in enumerate(dataAS,start=1):
        locals()[f'AS{i}'] = AS(As['number'],
                                As['protocol'],
                                As['listeRouteurs'],
                                As('addReseau'))
        (f'listeAs').append(f'AS{i}')

    return (f'listeAs')
        
        
            


if __name__ == "__main__":

    R1 = Routeur([1,1],['GigabiteEthernet1/0','GigabiteEthernet2/0'],[[2,""],[3,""]])
    R2 = Routeur([1,2],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0'],[[1,""],[3,""],[4,""]])
    R3 = Routeur([1,3],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0'],[[1,""],[2,""],[5,""]])
    R4 = Routeur([1,4],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0','GigabiteEthernet4/0'],[[2,""],[5,""],[6,""],[7,""]])
    R5 = Routeur([1,5],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0','GigabiteEthernet4/0'],[[3,""],[4,""],[6,""],[7,""]])
    R6 = Routeur([1,6],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0'],[[4,""],[5,""]],True, [[2,8,""]])
    R7 = Routeur([1,7],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0'],[[4,""],[5,""]],True, [[2,9,""]])
    R8 = Routeur([2,8],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0'],[[10,""],[11,""]],True, [[1,6,""]])
    R9 = Routeur([2,9],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0'],[[10,""],[11,""]],True, [[1,7,""]])
    R10 = Routeur([2,10],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0','GigabiteEthernet4/0'],[[8,""],[9,""],[11,""],[12,""]])
    R11 = Routeur([2,11],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0','GigabiteEthernet4/0'],[[8,""],[9,""],[10,""],[13,""]])
    R12 = Routeur([2,12],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0'],[[10,""],[13,""],[14,""]])
    R13 = Routeur([2,13],['GigabiteEthernet1/0','GigabiteEthernet2/0','GigabiteEthernet3/0'],[[11,""],[12,""],[14,""]])
    R14 = Routeur([2,14],['GigabiteEthernet1/0','GigabiteEthernet2/0'],[[12,""],[13,""]])
        
    AS1 = AS(1,"rip",[R1,R2,R3,R4,R5,R6,R7],'2020:0:1::/48')
    AS2 = AS(2,"ospf",[R8,R9,R10,R11,R12,R13,R14],'2020:0:2::/48')

    #listeAs = descriptJSON("Path")

    listeAs = creationListAs(AS1, AS2)

   # listeAs = appelJSON ('fichier_intention_Root.json')

    idNewNetwork = 1   
    
    # Ecrire les config des AS
    for As in listeAs :

        idNewNetwork = configRouteur(As,listeAs,idNewNetwork)

        for elem in As.listeRouteurs:
            with open("ConfigAutoR{}.txt".format(str(elem.ID[1])), 'w') as file:
                for line in elem.liste:
                    file.write(line+'\n')


#addressage en hexa en incrementant de 1