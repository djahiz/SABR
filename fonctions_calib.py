"""
    Calibration functions
    ======================
 
    Use to solve minimization problem and find SABR parameters.
 
"""

import math
from scipy.optimize import minimize

def vol_impli_sabr_lognormale(alpha, beta, rho, nu, forward, strike, expiry): 

    if forward <= 0 or strike <= 0:
        vol = 0
    else:
        if forward == strike: 
            if beta == 0:
                A = 1 + ((alpha**2)/((24.)*(forward**2)) + ((nu**2)*(2-3*(rho**2))/24.))*expiry
                vol = alpha/forward*A
            elif beta == 1:
                A = 1 + (alpha*nu*rho/(4.) + ((nu**2)*(2-3*(rho**2))/24.))*expiry
                vol = alpha*A
            else:
                V = (forward)**(1-beta)
                A = 1 + (((1-beta)**2*alpha**2)/((24.)*(V**2)) + (alpha*beta*nu*rho)/((4.)*V) + ((nu**2)*(2-3*(rho**2))/24.))*expiry
                vol = (alpha/V)*A
        else: 
            if beta == 0:
                z = (nu/alpha)*math.sqrt(forward*strike)*math.log(forward/strike)
                xi = math.log((math.sqrt(1-2*rho*z+z**2)+z-rho)/(1-rho))
                A = 1 + ((alpha**2)/((24.)*forward*strike)+((nu**2)*(2-3*(rho**2))/24.))*expiry
                vol = (alpha*math.log(forward/strike)*z*A)/((forward-strike)*xi)
            elif beta == 1:
                z = (nu/alpha)*math.log(forward/strike)
                xi = math.log((math.sqrt(1-2*rho*z+z**2)+z-rho)/(1-rho))
                A = 1 + (alpha*nu*rho/(4.)+((nu**2)*(2-3*(rho**2))/24.))*expiry
                vol = (alpha*z*A)/xi
            else:
                V = (forward*strike)**((1-beta)/2.)
                z = (nu/alpha)*V*math.log(forward/strike)
                xi = math.log((math.sqrt(1-2*rho*z+z**2)+z-rho)/(1-rho))
                A = 1 + (((1-beta)**2*alpha**2)/(24.*(V**2))+(alpha*beta*nu*rho)/(4.*V)+((nu**2)*(2-3*(rho**2))/24.))*expiry
                B = 1 + (1/24.)*(((1-beta)*math.log(forward/strike))**2) + (1/1920.)*(((1-beta)*math.log(forward/strike))**4)
                vol = (alpha*z*A)/(V*xi*B)

    return vol

def objfunc(parameters, forward, strikes, expiry, market_vol):
    sum_error = 0
    for j in range(len(strikes)):
        if market_vol[j] != 0:  
            vol = vol_impli_sabr_lognormale(parameters[0], parameters[1], parameters[2], parameters[3], forward, strikes[j], expiry)
            sum_error += (vol - market_vol[j])**2
    return math.sqrt(sum_error)

def calibration(init_values, limites, forward, strikes ,expiry, market_vol):
    res = minimize(objfunc, init_values, (forward, strikes, expiry, market_vol), bounds = limites, method = 'SLSQP')
    return res.x