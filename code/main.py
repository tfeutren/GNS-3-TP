# -------------------------------- #
# ** Configuration des routeurs ** #
# -------------------------------- #

# Importation des modules

import json
from type_objet import AS, Routeur
from readData import List_AS, List_Router
from telnet import *
from multiprocessing import Process

# ----------------------------------

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
        configProtocol(routeur,As.protocol)
        configProtocol(routeur,"bgp",As)
        
        routeur.ajoutListe("end")

    return idNewNetwork


#génération config address sur interface du routeur
def configAddress(routeur,As,listeAs,idNewNetwork):

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

                updateIndexNetwork+=1       
        
            else:
                routeur.ajoutListe("ipv6 address {}".format(str((routeur.neighbors[indexNeighbors])[1])))
            
            print(As.protocol+" intra "+str(routeur.ID[1]))
            if As.protocol == "rip":
                routeur.ajoutListe("ipv6 rip 1 enable")
            elif As.protocol == "ospf":
                routeur.ajoutListe("ipv6 ospf 1 area 1")
                if len(routeur.neighbors[indexNeighbors])==3 :
                    routeur.ajoutListe("ipv6 ospf cost "+str(routeur.neighbors[indexNeighbors][2]))
            
            indexNeighbors+=1
            

        # configuration des interfaces inter-domaines
        elif indexEbgpNeighbors < len(routeur.neighborsEbgp):
            if (routeur.neighborsEbgp[indexEbgpNeighbors])[2] == "":

                (routeur.neighborsEbgp[indexEbgpNeighbors])[2] = "2023:0:{}::{}/64".format(str(idNewNetwork+updateIndexNetwork),str(routeur.ID[1]))
                routeur.ajoutListe("ipv6 address {}".format(str((routeur.neighborsEbgp[indexEbgpNeighbors])[2])))

                for AsNei in listeAs:
                    if AsNei.number == (routeur.neighborsEbgp[indexEbgpNeighbors])[0]:
                        for r in AsNei.listeRouteurs:
                            if r.ID[1] == (routeur.neighborsEbgp[indexEbgpNeighbors])[1]:
                                for neighborEbgp in r.neighborsEbgp:
                                    if neighborEbgp[1] == routeur.ID[1] and neighborEbgp[2]=="":
                                        neighborEbgp[2]="2023:0:{}::{}/64".format(str(idNewNetwork+updateIndexNetwork),str(r.ID[1]))
                updateIndexNetwork+=1
                
            else:
                routeur.ajoutListe("ipv6 address {}".format(str((routeur.neighborsEbgp[indexEbgpNeighbors])[2])))

            indexEbgpNeighbors+=1
        
        routeur.ajoutListe("!")
    
    routeur.ajoutListe("interface loopback 0")
    routeur.ajoutListe("no shutdown")
    routeur.ajoutListe("ipv6 enable")
    routeur.ajoutListe("ipv6 address {}::{}/128".format(str(routeur.ID[0]),str(routeur.ID[1])))

    #configuration des interfaces suivant protocol de routage utilisé
    print(As.protocol+" loopback "+str(routeur.ID[1]))
    if As.protocol == "rip":
        routeur.ajoutListe("ipv6 rip 1 enable")
    elif As.protocol == "ospf":
        routeur.ajoutListe("ipv6 ospf 1 area 1")

    routeur.ajoutListe("!")

    return updateIndexNetwork


#génération config protocol du routeur
def configProtocol(routeur,protocol,As=None):

    #configuration protocol rip
    if protocol == "rip":
        routeur.ajoutListe("ipv6 router rip 1")
        routeur.ajoutListe("redistribute connected")
        routeur.ajoutListe("!")

    #configuration protocol ospf
    elif protocol == "ospf":
        routeur.ajoutListe("ipv6 router ospf 1")
        routeur.ajoutListe("router-id {}.{}.{}.{}".format(str(routeur.ID[1]),str(routeur.ID[1]),str(routeur.ID[1]),str(routeur.ID[1])))
        routeur.ajoutListe("!")
    
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
                routeur.ajoutListe("neighbor {}{} send-community".format(str(lienBGP[2])[:11],str(lienBGP[1])))

                if lienBGP[3]=="peer":
                    routeur.ajoutListe("set-community 2")
                    routeur.ajoutListe("neighbor {}{} route-map Peer in".format(str(lienBGP[2])[:11],str(lienBGP[1])))
                    

                elif lienBGP[3]=="provider":
                    routeur.ajoutListe("set-community 3")
                    routeur.ajoutListe("neighbor {}{} route-map Provider in".format(str(lienBGP[2])[:11],str(lienBGP[1])))


                elif lienBGP[3]=="customer":
                    routeur.ajoutListe("set-community 1")
                    routeur.ajoutListe("neighbor {}{} route-map Customer in".format(str(lienBGP[2])[:11],str(lienBGP[1])))


                
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
                
        routeur.ajoutListe("!")
        routeur.ajoutListe("!")

        if routeur.ASBR == True:

            routeur.ajoutListe("ip bgp-community new-format")

            routeur.ajoutListe("route-map Peer permit 101")
            routeur.ajoutListe("match community peer permit 2")
            routeur.ajoutListe("set LOCAL_PREF 200")
            routeur.ajoutListe("!")

            routeur.ajoutListe("route-map Customer permit 102")
            routeur.ajoutListe("match community customer permit 1")
            routeur.ajoutListe("set LOCAL_PREF 300")
            routeur.ajoutListe("!")

            routeur.ajoutListe("route-map Provider permit 100")
            routeur.ajoutListe("match community provider permit 3")
            routeur.ajoutListe("set LOCAL_PREF 100")
            routeur.ajoutListe("!")

            routeur.ajoutListe("ip community-list peer")
            routeur.ajoutListe("ip community-list customer")
            routeur.ajoutListe("ip community-list provider")



    

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

    # convertir un string en ligne de commande
    for line in List_Router:
        exec(line)
        print(line)
            

    # Définition de nos AS à partir de la classe AS
    listeAsStr =[]
    for line in List_AS:
        exec(line)
        sousLine = ""
        for k in range(len(line)):
            if line[k] == " ":
                break
            else:
                sousLine+=line[k]
        listeAsStr.append(sousLine)
    listeAs = [globals()[x] for x in listeAsStr]

    idNewNetwork = 1   
    
    # Ecrire les config des AS
    for As in listeAs :

        idNewNetwork = configRouteur(As,listeAs,idNewNetwork)

        for elem in As.listeRouteurs:
            with open("ConfigAutoR{}.txt".format(str(elem.ID[1])), 'w') as file:
                for line in elem.liste:
                    file.write(line+'\n')
'''
            conf = Process(target= configInstanceTelnet, args=(str(elem.ID[1]),))
            conf.start()

    conf.join()
''' 