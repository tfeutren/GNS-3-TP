# --------------------- #
# ** TELNET PROTOCOL ** #
# --------------------- #

from telnetlib import Telnet

# -------------------------------

# Constantes
HOST = "localhost"

# Fonction pour appliquer le protocole Telnet sur un routeur
def configInstanceTelnet(port):
    port=int(port)
    tn = Telnet(HOST,4999+port)
    
    tn.read_until(b"Username: ")
    tn.write(b"cisco\n")
    tn.read_until(b"Password: ")
    tn.write(b"cisco\n")

    with open("ConfigAutoR"+str(port)+".txt", "r") as fic:
        commands = fic.readlines()
    for command in commands:
        tn.write(command.encode('ascii') + b"\n")

    tn.write(b"exit\n")
    print(tn.read_all().decode('ascii'))


