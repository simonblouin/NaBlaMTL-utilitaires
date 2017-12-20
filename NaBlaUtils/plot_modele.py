import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from . import __constants__ as sc


def _initDF():
    """ temp """
    columns = [
               'tauR',
               'kappaR',
               'NH+',
               'NH',
               'NHe',
               'NH2',
               'sm',
               'entr',
               'P',
               'T',
               'Ne',
               'rho',
               'Mass',
               'Frad',
               'Fconv',
               'Ftot',
              ]
    
    df = pd.DataFrame(columns = columns)
    
    return df
    
    
def _D2E(s):
    # todo: fix 1.000-100 -> 1.000E-100
    return s.replace(b'D', b'E')


def modele_tlusty6(f):
    """ temp """
    
    df = _initDF()
    
    while True:
        line = f.readline()
        if 'TEFF'  in line: Teff = float(line.split()[-1])
        if 'LOG G' in line: logg = float(line.split()[-1])
        if 'TOTAL SURFACE FLUX' in line: break
    line = f.readline()
    f.readline()
    
    conv = {}
    for i in range(len(line.split())-1):
        conv[i] = _D2E
    
    data = np.loadtxt(f, converters = conv, unpack = True)
    
    df['Mass']  = data[1]
    df['tauR']  = data[2]
    df['T']     = data[3]
    df['Ne']    = data[4]
    df['rho']   = data[5]
    df['P']     = data[6]
    df['Ftot']  = data[7]
    df['Frad']  = data[8] * df['Ftot']
    df['Fconv'] = data[9] * df['Ftot']
    
    return {'Teff': Teff, 'logg': logg, 'modele': df}
    
    
def modele_tlusty7(f):
    """ temp """
    raise NotImplementedError
    
    
def modele_test62(f):
    """ temp """
    
    df = _initDF()
    
    params = f.readline().split()
    
    nq   = int(params[1])
    Teff = float(params[3])
    logg = np.log10(float(params[5]))
    
    test = f.readline().split()
    
    if len(test) == 3:
        # modèle geras
        f.readline()
        
    data = []
    for i in range(nq):
        data.append(np.fromstring(f.readline(), sep = ' '))
    data = np.array(data).T
    
    df['tauR']   = data[0]
    df['kappaR'] = data[1]
    df['NH+']    = data[2]
    df['NH']     = data[3]
    df['NHe']    = data[4]
    df['NH2']    = data[5]
    
    f.readline()
    f.readline()
    
    data = []
    for i in range(nq):
        data.append(np.fromstring(f.readline(), sep = ' '))
    data = np.array(data).T
    
    df['sm']     = data[0]
    df['entr']   = data[2]
    df['P']      = data[3]
    df['T']      = data[4]
    df['Ne']     = data[5]
    
    density = df[['NH', 'NH+', 'NH2', 'NHe']] * np.array([1, 1, 2, 4])
    df['rho'] = density.sum(axis = 1) / sc.N_A
        
    return {'Teff': Teff, 'logg': logg, 'modele': df}
    
    
def load_modele(inputfile):
    """ temp """
        
    with open(inputfile, 'r') as f:
        
        test = f.readline().split()
        f.seek(0)
        # print(test)
        
        if len(test) == 1:
            # Tlusty.6
            modele = modele_tlusty6(f)
            print(inputfile, 'tlusty.6')
            
        elif len(test) == 2:
            # Tlusty.7
            modele = modele_tlusty7(f)
            print(inputfile, 'tlusty.7')
            
        else:
            # test62 / geras
            modele = modele_test62(f)
            print(inputfile, 'test62 / geras')
            
    return modele
    


def plot_modele(filelist):
    """ temp """
        
    if not isinstance(filelist, list):
        filelist = [filelist]
        
    for i, inputfile in enumerate(filelist):
        
        modele = load_modele(inputfile)
        print(modele['modele'])
    
