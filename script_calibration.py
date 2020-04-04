"""
    Calibration module
    ======================
 
    Use it to import very obvious functions.
 
    :Example:
 
    >>> from obvious import add
    >>> add(1, 1)
    2
 
    This is a subtitle
    -------------------
 
    You can say so many things here ! You can say so many things here !
    You can say so many things here ! You can say so many things here !
    You can say so many things here ! You can say so many things here !
    You can say so many things here ! You can say so many things here !
 
    This is another subtitle
    ------------------------
 
    Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
    consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
    cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
    proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
 
 
"""

from fonctions_calib import *
import csv
import matplotlib.pyplot as plt
import os
import time

# script de calibration
# génère un fichier .csv contenant les valeurs des paramètres pour chaque (tenor,expiry)
# génère les courbe de comparaison volatilité marché volatilité calibrée

# première ligne du fichier .csv de sortie
fields_param = ["Tenor","Expiry","Alpha","Beta","Rho","Nu"]
# liste qui contiendra les ligne du fichier .csv
param = []

name_input_file = os.getcwd()+"\\inputs_lognormal.csv"

while True:
    print("Fixe parameter ?: ")
    print("[0]: Aucun")
    print("[1]: Beta")
    print("[2]: Rho")
    try:
        choice = int(input("Enter a value: "))
        if choice in [0, 1, 2]:
            break
        else:
            os.system("cls")
    except ValueError:
        os.system("cls")

if choice == 1:
    while True:
        print("Enter a value for Beta in [0;1]: ")
        try:
            beta_fixe = float(input("Beta = "))
            if beta_fixe >= 0 and beta_fixe <= 1:
                break
            else:
                os.system("cls")
        except ValueError:
            os.system("cls")

if choice == 2:
    while True:
        print("Enter a value for Rho in [-0.99;0.99]: ")
        try:
            rho_fixe = float(input("Rho = "))
            if rho_fixe >= -0.99 and rho_fixe <= 0.99:
                break
            else:
                os.system("cls")
        except ValueError:
            os.system("cls")

# lecture des données en inputs (tenor, expiry, forward, market vol par spread)
with open(name_input_file,"rt") as input_file:
    data_reader = csv.reader(input_file)
    data = [row for row in data_reader]
K = []
for i in range(3,len(data[0])):
    if str.split(data[0][i])[1] == "ATM":
        K.append(10000*float(data[1][2]))
    else:
        K.append(float(str.split(data[0][i])[1]))
# on boucle sur toutes les lignes du fichier inputs
# pour chaque ligne on calibre un jeu de paramètres puis on génère les graphs de comparaison
data.pop(0)
for row in data:
    
    strikes = [0.0001*k for k in K]
    forward = float(row[2])
    # on recupere la vol market
    vol_market = [float(v) for v in row[3:len(row)]]
    # si on veut calibrer pour une valeur fixe de beta

    if choice == 1:
        valeurs_initiales = [0.001,beta_fixe,0,0.001]
        limites = ((0.001,None),(beta_fixe,beta_fixe),(-0.999,0.999),(0.001,None))
    # si on veut calibrer pour une valeur fixe de rho
    elif choice == 2:
        valeurs_initiales = [0.001,0.5,rho_fixe,0.001]
        limites = ((0.001,None),(0,1),(rho_fixe,rho_fixe),(0.001,None))
    # sinon on calibre les 4 parametres
    else:
        valeurs_initiales = [0.001, 0.5, 0, 0.001]
        limites = ((0.001,None),(0,1),(rho_fixe,rho_fixe),(0.001,None))
        
    result = calibration(valeurs_initiales,forward,strikes,float(row[1]),vol_market,type_approx)

    param.append([row[0],row[1],result[0],result[1],result[2],result[3]])

    
    vol_impli = [100*vol_impli_sabr_lognormale(result[0],result[1],result[2],result[3],forward,strike,float(row[1])) for strike in strikes]
    plt.plot(K,vol_impli,label="Hagan lognormale ")

    # enregistrement des résultats (parametres fitté + graphs) 
    plt.plot(K,[100*v for v in vol_market],label="Marché")
    plt.legend()
    plt.xlabel("Strike (bps)")
    plt.ylabel("Volatilité Implicite (%)")
    
    name_file_outputs = os.getcwd()+"\\Outputs"
    if not os.path.exists(name_file_outputs):
        os.makedirs(name_file_outputs)
    plt.savefig(name_file_outputs+"\\Tenor "+row[0]+"y Expiry "+row[1]+"y_.png")
    plt.clf()

# création du fichier csv de sortie et écriture des résultats
with open(os.getcwd()+"\\Outputs\\output_param.csv", 'w', newline="") as param_file: 
    csvwriter = csv.writer(param_file) 
    csvwriter.writerow(fields_param) 
    csvwriter.writerows(param)
# fermeture des fichiers
input_file.close()
param_file.close()