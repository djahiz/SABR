"""
    Calibration module
    ======================
 
    Use to calibrate SABR parameters.
 
    :Inputs:
 
    File format .csv in repository Inputs
    
    :Outputs:

    Create Output repository in the current location to save graphs and .csv with computed parameters for each entry of the input file
  
 
"""

from fonctions_calib import *
import csv
import matplotlib.pyplot as plt
import os

param = []

name_input_file = os.getcwd()+"\\Inputs\\inputs_lognormal.csv"

while True:
    print("Fixe parameter ?: ")
    print("[0]: None")
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

with open(name_input_file,"rt") as input_file:
    data_reader = csv.reader(input_file)
    data = [row for row in data_reader]
K = []
for i in range(3,len(data[0])):
    if str.split(data[0][i])[1] == "ATM":
        K.append(10000*float(data[1][2]))
    else:
        K.append(float(str.split(data[0][i])[1]))

data.pop(0)
for row in data:
    
    strikes = [0.0001*k for k in K]
    forward = float(row[2])
    
    vol_market = [float(v) for v in row[3:len(row)]]

    if choice == 1:
        valeurs_initiales = [0.001,beta_fixe,0,0.001]
        limites = ((0.001,None),(beta_fixe,beta_fixe),(-0.999,0.999),(0.001,None))
    
    elif choice == 2:
        valeurs_initiales = [0.001,0.5,rho_fixe,0.001]
        limites = ((0.001,None),(0,1),(rho_fixe,rho_fixe),(0.001,None))
    
    else:
        valeurs_initiales = [0.001, 0.5, 0, 0.001]
        limites = ((0.001,None),(0,1),(-0.999,0.999),(0.001,None))
        
    result = calibration(valeurs_initiales,limites,forward,strikes,float(row[1]),vol_market)
    
    param.append([row[0],row[1],result[0],result[1],result[2],result[3]])
    
    vol_impli = [100*vol_impli_sabr_lognormale(result[0], result[1], result[2], result[3], forward, strike, float(row[1])) for strike in strikes]

    plt.plot(K, vol_impli, label = "Hagan lognormale ")

    plt.plot(K, [100*v for v in vol_market], label = "Market")
    plt.legend()
    plt.xlabel("Strike (bps)")
    plt.ylabel("Implied Volatility (%)")
    
    name_file_outputs = os.getcwd()+"\\Outputs"
    if not os.path.exists(name_file_outputs):
        os.makedirs(name_file_outputs)
    plt.savefig(name_file_outputs+"\\Tenor "+row[0]+"y Expiry "+row[1]+"y.png")
    plt.clf()


with open(os.getcwd()+"\\Outputs\\output_param.csv", 'w', newline="") as param_file: 
    csvwriter = csv.writer(param_file) 
    csvwriter.writerow(["Tenor", "Expiry", "Alpha", "Beta", "Rho", "Nu"]) 
    csvwriter.writerows(param)

input_file.close()
param_file.close()