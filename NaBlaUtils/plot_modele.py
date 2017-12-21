import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os.path import basename

from . import __constants__ as sc


def _initDF():
    """ Retourne un DataFrame vide avec les colonnes déjà créées """
    
    columns = [
               'tauR',   # profondeur optique
               'z',      # progondeur géométrique
               'kappaR', # oppacité de Rosseland
               'NH+',    # population H+ (protons)
               'NH',     #            atome hydrogène
               'NHe',    #            hélium
               'NH2',    #            hydrogène moléculaire
               'sm',     # ?????
               'entr',   # entropie
               'P',      # pression
               'T',      # température
               'Ne',     # population électrons
               'rho',    # densité
               'Mass',   # masse au dessus de la couche
               'Frad',   # fraction du flux total en radiation
               'Fconv',  #                        en convection
               'Ftot',   # flux total
              ]
    
    df = pd.DataFrame(columns = columns)
    
    return df
    
    
def _D2E(s):
    # todo: fix 1.000-100 -> 1.000E-100
    return s.replace(b'D', b'E')


def modele_tlusty6(f):
    """ Lecture des modèles *.6 de TLUSTY
        Retourne un dict avec la température effective, gravité de surface,
        et un DataFrame avec les différents paramètres d'intérêt """
    
    df = _initDF() # DataFrame vide
    
    while True:
        # On cherche les lignes d'intérêt
        line = f.readline()
        if 'TEFF'  in line: Teff = float(line.split()[-1])
        if 'LOG G' in line: logg = float(line.split()[-1])
        if 'TOTAL SURFACE FLUX' in line: break # le modèle est en dessous
    line = f.readline() # le header
    f.readline() # ligne vide
    
    conv = {}
    for i in range(len(line.split())-1):
        # convertisseur 1.D+2 -> 1.E+2, pour chaque colonne
        conv[i] = _D2E
    
    data = np.loadtxt(f, converters = conv, unpack = True)
    
    # Stockage dans le DataFrame
    df['Mass']  = data[1]
    df['tauR']  = data[2]
    df['T']     = data[3]
    df['Ne']    = data[4]
    df['rho']   = data[5]
    df['P']     = data[6]
    df['Ftot']  = data[7]
    df['Frad']  = data[8] #* df['Ftot']
    df['Fconv'] = data[9] #* df['Ftot']
    
    return {'Teff': Teff, 'logg': logg, 'modele': df}
    
    
def modele_tlusty7(f):
    """ temp """
    
    raise NotImplementedError('https://i.imgur.com/10lkUdy.gif')
    
    
def modele_test62(f):
    """ Lecture des modèles de test62 / geras
        Retourne un dict avec la température effective, gravité de surface,
        et un DataFrame avec les différents paramètres d'intérêt """
    
    df = _initDF() # DataFrame vide
    
    params = f.readline().split() # Paramètres du modèle et atmosphériques
    
    nq   = int(params[1])
    Teff = float(params[3])
    logg = np.log10(float(params[5]))
    
    # ligne d'abondances (test62) ou autres paramètres (geras)
    test = f.readline().split()
    
    if len(test) == 3:
        # modèle geras
        f.readline()
        
    # pour chaque couche, on lit la ligne
    data = []
    for i in range(nq):
        data.append(np.fromstring(f.readline(), sep = ' '))
    data = np.array(data).T
    
    # Stockage dans le DataFrame
    df['tauR']   = data[0]
    df['kappaR'] = data[1]
    df['NH+']    = data[2]
    df['NH']     = data[3]
    df['NHe']    = data[4]
    df['NH2']    = data[5]
    
    f.readline() # Paramètres du modèle et atmosphériques
    f.readline() # Abondances
    
    # pour chaque couche, on lit la ligne
    data = []
    for i in range(nq):
        data.append(np.fromstring(f.readline(), sep = ' '))
    data = np.array(data).T
    
    # Stockage dans le DataFrame
    df['sm']     = data[0]
    df['entr']   = data[2]
    df['P']      = data[3]
    df['T']      = data[4]
    df['Ne']     = data[5]
    
    # calcul de la densité, basé sur l'hydrogène et l'hélium
    density = df[['NH', 'NH+', 'NH2', 'NHe']] * np.array([1, 1, 2, 4])
    df['rho'] = density.sum(axis = 1) / sc.N_A
    
    # calcul de la profondeur géométrique
    # s = integral( delta_tau / kappa / rho, de 0 à tau )
    kap_rho = df['kappaR'] * df['rho']
    dtau    = df['tauR'].diff()
    df['z'] = (dtau / kap_rho).cumsum()
        
    return {'Teff': Teff, 'logg': logg, 'modele': df}
    
    
def load_modele(inputfile):
    """ Détermine le type de fichier de modèle (TLUSTY, test62 / geras)
        et retourne le dict du modèle """
        
    with open(inputfile, 'r') as f:
        
        test = f.readline().split()
        f.seek(0)
        
        if len(test) == 1:
            # Tlusty.6
            modele = modele_tlusty6(f)
            
        elif len(test) == 2:
            # Tlusty.7
            modele = modele_tlusty7(f)
            
        else:
            # test62 / geras
            modele = modele_test62(f)
            
    return modele
    

def plot_modele(filelist, figname = None, params = ['T', 'P']):
    """ Trace les structures des modèles dans la liste filelist,
        pour les paramètres dans la liste params.
        
        Si figname = None, retourne une fenêtre interactive
        Si un string est donné, enregistre la figure sous figname
        
        params est une liste de deux des différents paramètres du modèle
        d'atmosphère à tracer en fonction de la profondeur optique.
        Par défaut, trace la température et la pression.        
    """
    
    # Labels pour les axes y
    labels  = {
               'tauR'  : r'$\tau_R$',
               'z'     : r'Profondeur géométrique (cm)',
               'kappaR': r'$\kappa_R',
               'NH+'   : r'$N_{H^+}$',
               'NH'    : r'$N_H$',
               'NHe'   : r'$N_{He}$',
               'NH2'   : r'$N_{HII}$',
               'sm'    : r'sm',
               'entr'  : r'S',
               'P'     : r'Pression (dyn cm$^{-2}$)',
               'T'     : r'Température (K)',
               'Ne'    : r'$N_{e^-}$',
               'rho'   : r'Densité (g cm$^{-3}$)',
               'Mass'  : r'Masse (g)',
               'Frad'  : r'Flux radiatif',
               'Fconv' : r'Flux convectif',
               'Ftot'  : r'Flux total',
              }
        
    if not isinstance(filelist, list):
        filelist = [filelist]
        
    assert len(params) == 2 # deux paramètres absolument
        
    # Matplotlib plot
    fig, ax = plt.subplots(nrows = 1, ncols = 2)
    fig.subplots_adjust(wspace=0.3)
    ax[0].minorticks_on()
    ax[1].minorticks_on()
        
    for i, inputfile in enumerate(filelist):
        
        # On lit le modèle
        modeledict = load_modele(inputfile)
        
        Teff   = modeledict['Teff']
        logg   = modeledict['logg']
        modele = modeledict['modele'] # le DataFrame
        
        for p, param in enumerate(params):
            
            # Si un des paramètre n'est pas reconnu, on raise une erreur
            if param not in modele.columns:
                raise ValueError('Paramètre {} inconnu.'.format(param))
                
            if param in ('T', 'z', 'Frad', 'Fconv'):
                # Graphique linéaire en y, log en x
                ax[p].semilogx(modele['tauR'], modele[param],
                             label = basename(inputfile))
                             
            else:
                # Graphique log-log
                ax[p].loglog(modele['tauR'], modele[param],
                             label = basename(inputfile))
                         
            ax[p].set_xlabel(r'$\tau_R$')
            ax[p].set_ylabel(labels[param])
            
    # Crée la légende
    ax[0].legend()
            
    if figname is None:
        plt.show(fig)
    else:
        fig.savefig(figname)
    plt.close(fig)
