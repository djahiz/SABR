from fonctions_calib import *
from script_pricing_hedging import *
import matplotlib.pyplot as plt
import scipy.stats as stat
import os
import time
import numpy.random as rd

def vecteur_uniforme(dim):
    vect = []
    for i in range(dim):
        vect.append(rd.uniform(0,1,1)[0])
    return vect

def box_muller(random_vector):
    vect = []
    vect.append(math.sqrt(-math.log(random_vector[0]))*math.cos(2*math.pi*random_vector[1]))
    vect.append(math.sqrt(-math.log(random_vector[0]))*math.sin(2*math.pi*random_vector[1]))
    return vect

def var_correl(rho):
    vect = []
    random_vector = box_muller(vecteur_uniforme(2))
    vect.append(random_vector[0])
    vect.append(random_vector[0]*rho + random_vector[1]*math.sqrt(1-rho**2))
    return vect

def simulation_path(alpha,beta,rho,nu,forward_t0,expiry,nb_etape):
    h = float(expiry)/float(nb_etape)
    trajectoire = []
    forward_t = forward_t0
    alpha_t = alpha
    for i in range(nb_etape+1):
        if beta > 0 and beta < 1 and forward_t0 <= 0:
            forward_t = 0
        else:
            random_vector = var_correl(rho)
            forward_t += alpha_t*(forward_t**beta)*math.sqrt(h)*random_vector[0]
            alpha_t += alpha_t*nu*math.sqrt(h)*random_vector[1]
        trajectoire.append(forward_t)
    return trajectoire

def caplet_monte_carlo(alpha,beta,rho,nu,forward_t0,strike,expiry,nb_etape,nb_simul,zc,tau,graph=False):
    somme = 0
    e = math.exp(-zc*expiry)
    X = []
    V = []
    for i in range(nb_simul):
        trajectoire = simulation_path(alpha,beta,rho,nu,forward_t0,expiry,nb_etape)
        f = trajectoire[len(trajectoire)-1]
        if f-strike > 0:
            somme += f-strike
            X.append(f-strike)
        else:
            X.append(0)
        if i > 1:
            V.append(sum([(x-somme/i)**2 for x in X])/(i-1))
        if i%30 == 0:
            os.system("cls")
            loading = round(i/nb_simul*100)
            egales = ["="]*loading
            spaces = [" "]*(100-loading)
            print("[",end="")
            for e in egales:
                print(e,end="")
            for s in spaces:
                print(s,end="")
            print("] "+str(loading)+"%")
    if graph:
        plt.plot([i for i in range(100,nb_simul)],[1.0*tau*sum(X[0:i])/i for i in range(100,nb_simul)],label="Prix")
        plt.plot([i for i in range(100,len(V))],[1.0*tau*sum(X[0:i])/i-1.96*math.sqrt(V[i]/i) for i in range(100,len(V))],label="Prix IC-95%")
        plt.plot([i for i in range(100,len(V))],[1.0*tau*sum(X[0:i])/i+1.96*math.sqrt(V[i]/i) for i in range(100,len(V))],label="Prix IC+95%")
        plt.legend()
        plt.xlabel("Simulation")
        plt.ylabel("Prix")
        name_file_outputs = os.getcwd()+"\\Outputs\\MC"
        if not os.path.exists(name_file_outputs):
            os.makedirs(name_file_outputs)
        plt.savefig(name_file_outputs+"\\simulation_prix_mc.png")
    ic = 1.96*math.sqrt(V[len(V)-1]/nb_simul)
    return [1.0*tau*float(somme)/float(nb_simul)-ic,1.0*tau*float(somme)/float(nb_simul),1.0*tau*float(somme)/float(nb_simul)+ic]

def objfunc2(parametre,prix,forward,strike,expiry,zc,tau):
    dp = d_plus(forward,strike,parametre[0],expiry)
    dm = d_moins(forward,strike,parametre[0],expiry)
    prix_approx = math.exp(-expiry*zc)*tau*(forward*stat.norm.cdf(dp)-strike*stat.norm.cdf(dm))
    return abs(prix-prix_approx)

def approx_vol_caplet(prix,forward,strike,expiry,zc,tau):
    limite = (0,10000)
    x0 = 10
    res = minimize(objfunc2,x0,(prix,forward,strike,expiry,zc,tau),bounds = limite, method='SLSQP')
    return res.x

if __name__ == '__main__':

    # PARAMETRES
    forward = 100
    strike = 50
    expiry = 1
    alpha = 0.1
    beta = 0.5
    rho = 0
    nu = 0.25
    zc = 0
    tau = 1
    strike_min = 1
    strike_max = 150
    strikes = [i/100 for i in range(strike_min*100,strike_max*100)]
    nb_etape = 250
    nb_simul = 10000

    while True:
        print("Que voulez vous faire:")
        print("[1]: Génération de trajectoires de forward")
        print("[2]: Calcul du prix par Monte Carlo (avec courbes)")
        print("[3]: Calcul du prix par Monte Carlo (sans courbes)")
        print("[4]: Test de la qualité de l'approximation")
        try:
            choix = int(input("Saisissez une valeur : "))
            if choix == 1 or choix == 2 or choix == 3 or choix == 4:
                break
            else:
                os.system("cls")
        except:
            os.system("cls")

    if choix == 1:
        for i in range(50):
            trajectoire = simulation_path(alpha,beta,rho,nu,forward,expiry,nb_etape)
            plt.plot([i*expiry/nb_etape for i in range(nb_etape+1)],[t/100 for t in trajectoire])
        plt.xlabel("Time")
        plt.ylabel("Forward (%)")
        name_file_outputs = os.getcwd()+"\\Outputs\\MC"
        if not os.path.exists(name_file_outputs):
            os.makedirs(name_file_outputs)
        plt.savefig(name_file_outputs+"\\trajectoires.png")
        plt.clf()

    if choix == 2:
        result = caplet_monte_carlo(alpha,beta,rho,nu,forward,strike,expiry,nb_etape,nb_simul,zc,tau,True)
        print("Prix: "+str(result[1]))
        print("Intervalle de confiance à 95%: ["+str(result[0])+", "+str(result[2])+"]")
        input("Appuyer sur n'importe quelle touche...")

    if choix == 3:
        result = caplet_monte_carlo(alpha,beta,rho,nu,forward,strike,expiry,nb_etape,nb_simul,zc,tau,False)
        print("Prix: "+str(result[1]))
        print("Intervalle de confiance à 95%: ["+str(result[0])+", "+str(result[2])+"]")
        input("Appuyer sur n'importe quelle touche...")

    if choix == 4:
        tab_expiriy = [0.25,0.5,0.75,1,2,5,10,20]
        vect_abscisse = []
        erreur = []
        nb_test = 1
        for i in tab_expiriy:
            print("Test "+str(nb_test)+" sur "+str(len(tab_expiriy)))
            time.sleep(0.5)
            vect_abscisse.append(nu*nu*i)
            p_mc = caplet_monte_carlo(alpha,beta,rho,nu,forward,strike,i,nb_etape,nb_simul,zc,tau,False)[1]
            p_approx = prix_lognormal(alpha,beta,rho,nu,forward,strike,i,zc,tau)
            erreur.append(abs((p_mc-p_approx)/p_mc))
            nb_test += 1
        plt.plot(vect_abscisse,erreur)
        plt.xlabel("nu^2*expiry")
        plt.ylabel("Erreur relative")
        name_file_outputs = os.getcwd()+"\\Outputs\\MC"
        if not os.path.exists(name_file_outputs):
            os.makedirs(name_file_outputs)
        plt.savefig(name_file_outputs+"\\qualite_approx.png")