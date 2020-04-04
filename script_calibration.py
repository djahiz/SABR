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
# Choix approx normale ou lognormale
while True:
    print("Choix de l'approximation: ")
    print("[1]: Normale")
    print("[2]: Lognormale non shifté")
    print("[3]: Lognormale shifté")
    try:
        choix = int(input("Saisissez une valeur : "))
        if choix == 1 or choix == 2 or choix == 3 or choix == 4:
            break
        else:
            os.system("cls")
    except:
        os.system("cls")

if choix == 1:
    type_approx = "normale"
    modele_shift = ""
    name_input_file = os.getcwd()+"\\inputs_normal.csv"
elif choix == 2:
    type_approx = "lognormale"
    modele_shift = ""
    name_input_file = os.getcwd()+"\\inputs_lognormal.csv"
else:
    type_approx = "lognormale"
    modele_shift = "shift"
    name_input_file = os.getcwd()+"\\inputs_lognormal_shift.csv"

if modele_shift == "shift":
    # Choix valeur de shift
    while True:
        print("Choisissez une valeur de shift (en bps): ")
        try:
            valeur_shift = float(input("Saisissez une valeur : "))
            break
        except:
            os.system("cls")

# Choix calibration avec beta fixé
while True:
    print("Fixer la valeur d'un paramètre ?: ")
    print("[0]: Aucun")
    print("[1]: Beta")
    print("[2]: Rho")
    try:
        choix_param = int(input("Saisissez une valeur : "))
        if choix_param == 0 or choix_param == 1 or choix_param == 2:
            break
        else:
            os.system("cls")
    except:
        os.system("cls")

if choix_param == 1:
    # Choix valeur de beta
    while True:
        print("Choisissez une valeur de Beta dans [0;1]: ")
        try:
            beta_fixe = float(input("Saisissez une valeur : "))
            if beta_fixe >= 0 and beta_fixe <= 1:
                break
            else:
                os.system("cls")
        except:
            os.system("cls")

if choix_param == 2:
    # Choix valeur de rho
    while True:
        print("Choisissez une valeur de Rho dans [-0.99;0.99]: ")
        try:
            rho_fixe = float(input("Saisissez une valeur : "))
            if rho_fixe >= -0.99 and rho_fixe <= 0.99:
                break
            else:
                os.system("cls")
        except:
            os.system("cls")

# valeurs initiales pour la calibration
valeurs_initiales = [0.001,0.5,0,0.001]

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
    # si on a choisi le modele avec shifte
    if modele_shift == "shift":
        forward = float(row[2]) + 0.0001*valeur_shift
        strikes = [float(row[2])+ 0.0001*(k+valeur_shift) for k in K]
    else:
        strikes = [0.0001*k for k in K]
        forward = float(row[2])  
    # on recupere la vol market
    vol_market = [float(v) for v in row[3:len(row)]]
    # si on veut calibrer pour une valeur fixe de beta
    if choix_param == 1:
        valeurs_initiales = [0.001,beta_fixe,0,0.001]
        result = calibration_beta_fixe(valeurs_initiales,beta_fixe,forward,strikes,float(row[1]),vol_market,type_approx)
    # si on veut calibrer pour une valeur fixe de rho
    elif choix_param == 2:
        valeurs_initiales = [0.001,0.5,rho_fixe,0.001]
        result = calibration_rho_fixe(valeurs_initiales,rho_fixe,forward,strikes,float(row[1]),vol_market,type_approx)
    # sinon on calibre les 4 parametres
    else:
        result = calibration(valeurs_initiales,forward,strikes,float(row[1]),vol_market,type_approx)

    param.append([row[0],row[1],result[0],result[1],result[2],result[3]])

    if(type_approx == "normale"):
        vol_impli = [100*vol_impli_sabr_normale(result[0],result[1],result[2],result[3],forward,strike,float(row[1])) for strike in strikes]
        plt.plot(K,vol_impli,label="Hagan normale")
    else:
        vol_impli = [100*vol_impli_sabr_lognormale(result[0],result[1],result[2],result[3],forward,strike,float(row[1])) for strike in strikes]
        plt.plot(K,vol_impli,label="Hagan lognormale "+modele_shift)

    # enregistrement des résultats (parametres fitté + graphs) 
    plt.plot(K,[100*v for v in vol_market],label="Marché")
    plt.legend()
    plt.xlabel("Strike (bps)")
    plt.ylabel("Volatilité Implicite (%)")
    if modele_shift == "shift":
        name_file_outputs = os.getcwd()+"\\Outputs\\avec_shift\\"+type_approx
        if not os.path.exists(name_file_outputs):
            os.makedirs(name_file_outputs)
        plt.savefig(name_file_outputs+"\\Tenor "+row[0]+"y Expiry "+row[1]+"y_"+type_approx+"_shift.png")
    else:
        name_file_outputs = os.getcwd()+"\\Outputs\\sans_shift\\"+type_approx
        if not os.path.exists(name_file_outputs):
            os.makedirs(name_file_outputs)
        plt.savefig(name_file_outputs+"\\Tenor "+row[0]+"y Expiry "+row[1]+"y_"+type_approx+".png")
    plt.clf()

# création du fichier csv de sortie et écriture des résultats
with open(os.getcwd()+"\\Outputs\\output_param.csv", 'w', newline="") as param_file: 
    csvwriter = csv.writer(param_file) 
    csvwriter.writerow(fields_param) 
    csvwriter.writerows(param)
# fermeture des fichiers
input_file.close()
param_file.close()