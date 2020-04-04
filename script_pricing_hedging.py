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

    forward = -39.8#50#-39.8  # valeur forward en bps
    expiry = 1.0   # maturite residuelle en annee
    alpha = 0.7
    beta = 0.8
    rho = -0.99
    nu = 0.83
    zc = 0  # taux zero coupon
    tau = 1 # maturite du zero coupon
    strike_min = -300 # strike en bps
    strike_max = 500
    strikes = [i/100 for i in range(strike_min*100,strike_max*100)]

    # strike pour calculer le prix du caplet
    strike_caplet = 100
    forward_min = -250
    forward_max = 500
    forwards = [i/100 for i in range(forward_min*100,forward_max*100)]

    # si on se place dans le cas du modele avec shift
    shift = 50.01 
    forward = forward + shift
    strikes = [strike+shift for strike in strikes]
    forwards = [f+shift for f in forwards]
    strike_caplet = strike_caplet + shift

    #######################

    while True:
        print("Que voulez vous faire:")
        print("[1]: Génération courbes de volatilité lognormale")
        print("[2]: Génération courbes de volatilité lognormale (beta variable)")
        print("[3]: Génération courbes de volatilité lognormale (shift variable)")
        print("[4]: Calcul du prix par l'approximation")
        print("[5]: Calcul du prix par l'approximation (multiple expiry)")
        print("[6]: Calcul du prix par l'approximation (shift variable)")
        print("[7]: Calcul de densité")
        print("[8]: Calcul de densité (beta variable)")
        print("[9]: Calcul delta")
        print("[10]: Calcul delta (shift variable)")
        try:
            choix = int(input("Saisissez une valeur : "))
            if choix >= 1 and choix <= 10:
                break
            else:
                os.system("cls")
        except:
            os.system("cls")

    if choix == 1:
        vol_lognormale = [vol_impli_sabr_lognormale(alpha,beta,rho,nu,0.0001*forward,0.0001*strike,expiry) for strike in strikes]
        plt.plot([i/10000 for i in range(strike_min*100,strike_max*100)],[100*vol for vol in vol_lognormale],label="Volatilité Black")
        plt.legend()
        plt.xlabel("Strike (%)")
        plt.ylabel("Volatilité Implicite (%)")
        name_file_outputs = os.getcwd()+"\\Outputs\\pricing"
        if not os.path.exists(name_file_outputs):
            os.makedirs(name_file_outputs)
        plt.savefig(name_file_outputs+"\\vol_black.png")
        plt.clf()

    if choix == 2:
        betas = [0.2,0.3,0.4,0.5,0.7]
        for b in betas:
            vol_lognormale = [vol_impli_sabr_lognormale(alpha,b,rho,nu,0.0001*forward,0.0001*strike,expiry) for strike in strikes]
            plt.plot([strike/100 for strike in strikes],[100*vol for vol in vol_lognormale],label="Volatilité Black beta = "+str(b))
        plt.legend()
        plt.xlabel("Strike (%)")
        plt.ylabel("Volatilité Implicite (%)")
        name_file_outputs = os.getcwd()+"\\Outputs\\pricing"
        if not os.path.exists(name_file_outputs):
            os.makedirs(name_file_outputs)
        plt.savefig(name_file_outputs+"\\vol_black_beta.png")
        plt.clf()

    if choix == 3:
        shifts = [50.01,100.01,200.01,500.01]
        for s in shifts:
            vol_lognormale = [vol_impli_sabr_lognormale(alpha,beta,rho,nu,0.0001*(forward-shift+s),0.0001*(strike-shift+s),expiry) for strike in strikes]
            plt.plot([i/10000 for i in range(strike_min*100,strike_max*100)],[100*vol for vol in vol_lognormale],label="Volatilité Black shift = "+str(s)+" bps")
        plt.legend()
        plt.xlabel("Strike (%)")
        plt.ylabel("Volatilité Implicite (%)")
        name_file_outputs = os.getcwd()+"\\Outputs\\pricing"
        if not os.path.exists(name_file_outputs):
            os.makedirs(name_file_outputs)
        plt.savefig(name_file_outputs+"\\vol_black_shift.png")
        plt.clf()

    if choix == 4:
        plt.plot([i/10000 for i in range(forward_min*100,forward_max*100)],[(1/100)*prix_lognormal(alpha,beta,rho,nu,f,strike_caplet,expiry,zc,tau) for f in forwards],label="Prix Black")
        plt.legend()
        plt.xlabel("Forward (%)")
        plt.ylabel("Prix (%)")
        name_file_outputs = os.getcwd()+"\\Outputs\\pricing"
        if not os.path.exists(name_file_outputs):
            os.makedirs(name_file_outputs)
        plt.savefig(name_file_outputs+"\\prix_black.png")
        plt.clf()

    if choix == 5:
        plt.plot([i/10000 for i in range(forward_min*100,forward_max*100)],[(1/100)*prix_lognormal(alpha,beta,rho,nu,f,strike_caplet,expiry,zc,tau) for f in forwards],label="Prix Black T = "+str(expiry)+"Y")
        plt.plot([i/10000 for i in range(forward_min*100,forward_max*100)],[(1/100)*prix_lognormal(alpha,beta,rho,nu,f,strike_caplet,expiry/10,zc,tau) for f in forwards],label="Prix Black T = "+str(expiry/10)+"Y")
        plt.plot([i/10000 for i in range(forward_min*100,forward_max*100)],[(1/100)*prix_lognormal(alpha,beta,rho,nu,f,strike_caplet,expiry/100,zc,tau) for f in forwards],label="Prix Black T = "+str(expiry/100)+"Y")
        plt.plot([i/10000 for i in range(forward_min*100,forward_max*100)],[(1/100)*payoff_caplet(f,strike_caplet) for f in forwards],label="Payoff")
        plt.legend()
        plt.xlabel("Forward (%)")
        plt.ylabel("Prix (%)")
        name_file_outputs = os.getcwd()+"\\Outputs\\pricing"
        if not os.path.exists(name_file_outputs):
            os.makedirs(name_file_outputs)
        plt.savefig(name_file_outputs+"\\prix_black.png")
        plt.clf()

    if choix == 6:
        shifts = [50,100,150,200]
        for s in shifts:
            if s==50:
                alpha,beta,rho,nu = 0.70,0.80,-0.99,0.83
            if s==100:
                alpha,beta,rho,nu = 0.17,0.58,-0.95,0.91
            if s==150:
                alpha,beta,rho,nu = 1.16,1.00,-0.94,1.09
            if s==200:
                alpha,beta,rho,nu = 1.08,1.00,-0.92,1.21
            plt.plot([i/10000 for i in range(forward_min*100,forward_max*100)],[(1/100)*prix_lognormal(alpha,beta,rho,nu,f-shift+s,strike_caplet-shift+s,expiry,zc,tau) for f in forwards],label="Prix Black shift = "+str(s)+"bps")
        plt.legend()
        plt.xlabel("Forward (%)")
        plt.ylabel("Prix (%)")
        name_file_outputs = os.getcwd()+"\\Outputs\\pricing"
        if not os.path.exists(name_file_outputs):
            os.makedirs(name_file_outputs)
        plt.savefig(name_file_outputs+"\\prix_black_shift.png")
        plt.clf()

    if choix == 7:
        plt.plot([strike/100 for strike in strikes],[densite_proba(alpha,beta,rho,nu,forward,strike,expiry,zc,tau) for strike in strikes],label="Densité")
        plt.legend()
        plt.xlabel("Strike (%)")
        plt.ylabel("Densite")
        name_file_outputs = os.getcwd()+"\\Outputs\\pricing"
        if not os.path.exists(name_file_outputs):
            os.makedirs(name_file_outputs)
        plt.savefig(name_file_outputs+"\\densite.png")
        plt.clf()

    if choix == 8:
        for beta in [0.3,0.4,0.5,0.7]:
            plt.plot([strike/100 for strike in strikes],[densite_proba(alpha,beta,rho,nu,forward,strike,expiry,zc,tau) for strike in strikes],label="Densité beta = "+str(beta))
        plt.legend()
        plt.xlabel("Strike (%)")
        plt.ylabel("Densite")
        name_file_outputs = os.getcwd()+"\\Outputs\\pricing"
        if not os.path.exists(name_file_outputs):
            os.makedirs(name_file_outputs)
        plt.savefig(name_file_outputs+"\\densite_beta.png")
        plt.clf()

    if choix == 9:
        plt.plot([i/10000 for i in range(forward_min*100,forward_max*100)],[delta(alpha,beta,rho,nu,f,strike_caplet,expiry,zc,tau) for f in forwards],label="Delta")
        plt.legend()
        plt.xlabel("Forward (%)")
        plt.ylabel("Delta")
        name_file_outputs = os.getcwd()+"\\Outputs\\pricing"
        if not os.path.exists(name_file_outputs):
            os.makedirs(name_file_outputs)
        plt.savefig(name_file_outputs+"\\delta.png")
        plt.clf()

    if choix == 10:
        shifts = [50,100,150,200]
        for s in shifts:
            if s==50:
                alpha,beta,rho,nu = 0.70,0.80,-0.99,0.83
            if s==100:
                alpha,beta,rho,nu = 0.17,0.58,-0.95,0.91
            if s==150:
                alpha,beta,rho,nu = 1.16,1.00,-0.94,1.09
            if s==200:
                alpha,beta,rho,nu = 1.08,1.00,-0.92,1.21
            plt.plot([i/10000 for i in range(forward_min*100,forward_max*100)],[delta(alpha,beta,rho,nu,f-shift+s,strike_caplet-shift+s,expiry,zc,tau) for f in forwards],label="Delta shift = "+str(s)+" bps")
        plt.legend()
        plt.xlabel("Forward (%)")
        plt.ylabel("Delta")
        name_file_outputs = os.getcwd()+"\\Outputs\\pricing"
        if not os.path.exists(name_file_outputs):
            os.makedirs(name_file_outputs)
        plt.savefig(name_file_outputs+"\\delta_shift.png")
        plt.clf()