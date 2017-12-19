"""
Constantes scientifiques prises de scipy.constants, mais converties en 
unités CGS (centimètre, gramme, seconde, erg, dyne, etc.)

Référence utile: http://www.astro.wisc.edu/~dolan/constants.html
"""

import scipy.constants as cst

#  Constante                                   Unité
c     = cst.c / cst.centi                      # cm
c_ang = c * 1e8                                # Ang
h     = cst.h / cst.erg                        # erg s
k     = cst.k / cst.erg                        # erg / K    
e     = cst.e * (10 * cst.c)                   # esu
m_e   = cst.m_e * cst.kilo                     # g
m_p   = cst.m_p * cst.kilo                     # g
N_A   = cst.N_A                                # mol**-1
sigma = cst.sigma / cst.erg * cst.centi**2     # erg / cm**2 / K**4 / s
pi    = cst.pi                                 # -




