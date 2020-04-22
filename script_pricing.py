from fonctions_calib import *
import matplotlib.pyplot as plt
import scipy.stats as stat
import os
import time

def d_plus(forward,strike,vol,expiry):
    if forward <= 0 or strike <= 0:
        return 0
    else:
        return (math.log(forward/strike)+0.5*vol**2*expiry)/(math.sqrt(expiry)*vol)

def d_moins(forward,strike,vol,expiry):
    if forward <= 0 or strike <= 0:
        return 0
    else:
        return d_plus(forward,strike,vol,expiry)-math.sqrt(expiry)*vol

def prix_lognormal(alpha,beta,rho,nu,forward,strike,expiry,zc,tau):
    if forward <= 0 or strike <= 0:
        return 0
    vol = vol_impli_sabr_lognormale(alpha,beta,rho,nu,0.0001*forward,0.0001*strike,expiry)
    dp = d_plus(forward,strike,vol,expiry)
    dm = d_moins(forward,strike,vol,expiry)
    return math.exp(-expiry*zc)*tau*(forward*stat.norm.cdf(dp)-strike*stat.norm.cdf(dm))

def payoff_caplet(forward,strike):
    return max(0,forward-strike)

def densite_proba(alpha,beta,rho,nu,forward,strike,expiry,zc,tau):
    epsilon = 1e-3
    prix_moins = prix_lognormal(alpha,beta,rho,nu,forward,strike-epsilon,expiry,zc,tau)
    prix = prix_lognormal(alpha,beta,rho,nu,forward,strike,expiry,zc,tau)
    prix_plus = prix_lognormal(alpha,beta,rho,nu,forward,strike+epsilon,expiry,zc,tau)
    return (prix_moins - 2*prix + prix_plus)/epsilon**2

def delta(alpha,beta,rho,nu,forward,strike,expiry,zc,tau):
    if forward <= 0 or strike <= 0:
        return 0
    epsilon = forward/10
    prix_moins = prix_lognormal(alpha,beta,rho,nu,forward-epsilon,strike,expiry,zc,tau)
    prix_plus = prix_lognormal(alpha,beta,rho,nu,forward+epsilon,strike,expiry,zc,tau)
    return (prix_plus - prix_moins)/(2.0*epsilon)

if __name__ == '__main__':
    
    #######################
    ### PARAMETRISATION ###
    #######################

    forward = 50#-39.8  # valeur forward en bps
    expiry = 1.0   # maturite residuelle en annee
    alpha = 0.7
    beta = 0.8
    rho = -0.99
    nu = 0.83
    zc = 0  # taux zero coupon
    tau = 1 # maturite du zero coupon
    strike_min = 0 # strike en bps
    strike_max = 500
    strikes = [i/100 for i in range(strike_min*100,strike_max*100)]

    # strike pour calculer le prix du caplet
    strike_caplet = 100
    forward_min = 0
    forward_max = 500
    forwards = [i/100 for i in range(forward_min*100,forward_max*100)]

    #######################

    while True:
        print("Que voulez vous faire:")
        print("[1]: Calcul du prix par l'approximation")
        print("[2]: Calcul de densité")
        print("[3]: Calcul delta")
        try:
            choix = int(input("Saisissez une valeur : "))
            if choix >= 1 and choix <= 10:
                break
            else:
                os.system("cls")
        except:
            os.system("cls")

    if choix == 1:
        plt.plot([i/10000 for i in range(forward_min*100,forward_max*100)],[(1/100)*prix_lognormal(alpha,beta,rho,nu,f,strike_caplet,expiry,zc,tau) for f in forwards],label="Prix Black")
        plt.legend()
        plt.xlabel("Forward (%)")
        plt.ylabel("Prix (%)")
        name_file_outputs = os.getcwd()+"\\Outputs\\pricing"
        if not os.path.exists(name_file_outputs):
            os.makedirs(name_file_outputs)
        plt.savefig(name_file_outputs+"\\prix_black.png")
        plt.clf()

    if choix == 2:
        plt.plot([strike/100 for strike in strikes],[densite_proba(alpha,beta,rho,nu,forward,strike,expiry,zc,tau) for strike in strikes],label="Densité")
        plt.legend()
        plt.xlabel("Strike (%)")
        plt.ylabel("Densite")
        name_file_outputs = os.getcwd()+"\\Outputs\\pricing"
        if not os.path.exists(name_file_outputs):
            os.makedirs(name_file_outputs)
        plt.savefig(name_file_outputs+"\\densite.png")
        plt.clf()

    if choix == 3:
        plt.plot([i/10000 for i in range(forward_min*100,forward_max*100)],[delta(alpha,beta,rho,nu,f,strike_caplet,expiry,zc,tau) for f in forwards],label="Delta")
        plt.legend()
        plt.xlabel("Forward (%)")
        plt.ylabel("Delta")
        name_file_outputs = os.getcwd()+"\\Outputs\\pricing"
        if not os.path.exists(name_file_outputs):
            os.makedirs(name_file_outputs)
        plt.savefig(name_file_outputs+"\\delta.png")
        plt.clf()