from fonctions_calib import *
import csv
import matplotlib.pyplot as plt
import os

# script de test de l'impact des paramètres sur le smile de volatilité 

# choisir une valeur pour le taux forward
forward = 0.05
# choix des valeurs de spread
strike_spreads = [10,25,50,100,150,200,250,300,400,500,600,700,800]
strikes = [0.0001*spread for spread in strike_spreads]

# choix des paramètres
alpha = [0.03,0.025,0.035,0.04]
beta = [0.1,0.4,0.6,0.8]
rho = [-0.6,-0.2,0,0.2,0.6]
nu = [0.4,0.5,0.6,0.3,0.2]
expiry = 1

# création du répertoire pour les graphs générés
name_file_outputs = os.getcwd()+"\\Outputs\\Impact param"
if not os.path.exists(name_file_outputs):
    os.makedirs(name_file_outputs)
    
# on fait varier seulement alpha
for a in alpha:
    vol_impli = [100*vol_impli_sabr_lognormale(a,0.4,-0.2,0.2,forward,strike,expiry) for strike in strikes]
    plt.plot([100*strike for strike in strikes],vol_impli,label="Alpha = "+str(a))
plt.legend()
plt.xlabel("Strike (%)")
plt.ylabel("Volatilité Implicite (%)")
plt.savefig(name_file_outputs+"\\impact_alpha.png")
plt.clf()
# on fait varier seulement beta
for b in beta:
    vol_impli = [100*vol_impli_sabr_lognormale(0.01,b,-0.2,0.2,forward,strike,expiry) for strike in strikes]
    plt.plot([100*strike for strike in strikes],vol_impli,label="Beta = "+str(b))
plt.legend()
plt.xlabel("Strike (%)")
plt.ylabel("Volatilité Implicite (%)")
plt.savefig(name_file_outputs+"\\impact_beta.png")
plt.clf()
# on fait varier seulement rho
for r in rho:
    vol_impli = [100*vol_impli_sabr_lognormale(0.01,0.4,r,0.2,forward,strike,expiry) for strike in strikes]
    plt.plot([100*strike for strike in strikes],vol_impli,label="Rho = "+str(r))
plt.legend()
plt.xlabel("Strike (%)")
plt.ylabel("Volatilité Implicite (%)")
plt.savefig(name_file_outputs+"\\impact_rho.png")
plt.clf()
# on fait varier seulement nu
for n in nu:
    vol_impli = [100*vol_impli_sabr_lognormale(0.01,0.4,-0.2,n,forward,strike,expiry) for strike in strikes]
    plt.plot([100*strike for strike in strikes],vol_impli,label="Nu = "+str(n))
plt.legend()
plt.xlabel("Strike (%)")
plt.ylabel("Volatilité Implicite (%)")
plt.savefig(name_file_outputs+"\\impact_nu.png")
plt.clf()
