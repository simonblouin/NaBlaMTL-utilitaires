import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import csv
import re
from os.path import basename

from . import __constants__ as sc
from . import fortranformat as ff


# def spectre_test62(f):
    # """ Lecture d'un fichier spectre synthetique de test62 """
    # wav = []
    # flux = []
    # end = False
    # prevwav = 0
    # while not end:
        # try:
            # line = re.findall('([\d\s]*\.\d{2})',f.readline())
            # wavnew = [float(w) for w in line]
            # if(wavnew[-1] <= prevwav):
                # end = True
            # else:
                # wav = np.append(wav,wavnew)
                # prevwav = wavnew[-1]
        # except:
            # end = True
    # aflux = f.readlines()
    # for line in aflux:
        # line = re.sub('-10\d', 'e-100', line)
        # flux = np.append(flux, line.rstrip().split())
    # return wav,flux
    
    
def spectre_test62(f):
    """ Lecture d'un fichier spectre synthétique de test62,
        avec le package fortranformat """
    
    format_wav  = ff.FortranRecordReader('(10f8.2)')
    format_flux = ff.FortranRecordReader('(6e12.5)')
        
    wav = []
    flux = []
    npts = int(f.readline()) # nombre de points de fréquence
    
    while len(wav) < npts:
        wav += format_wav.read(f.readline())
    wav = np.array(wav[:npts])
    
    f.readline() # Paramètres atmosphériques
    
    while len(flux) < npts:
        flux += format_flux.read(f.readline())
    flux = np.array(flux[:npts])
    
    return wav, flux
    

def spectre_csv(f):
    """ Lecture d'un fichier spectre d'un fichier csv en 2 colonnes """
    
    skip = 0
    while True:
        try:    
            wav, flux = np.loadtxt(f, delimiter = ',',
                                   skiprows = skip, unpack = True)
        
        except ValueError:
            # Si les première lignes ont un en-tête
            skip += 1
            
        else:
            break
            
    return wav,flux
    

def spectre_tsv(f):
    """ Lecture d'un fichier spectre en 2 colonnes """
    
    skip = 0
    while True:
        try:    
            wav, flux = np.loadtxt(f, skiprows = skip, unpack = True)
        
        except ValueError:
            # Si les première lignes ont un en-tête
            skip += 1
            
        else:
            break
            
    return wav,flux
    

# def spectre_tsv3(f):
    # """ Lecture d'un fichier spectre en 3 colonnes (avec incertitudes sur flux)"""
    # try:
        # wav, flux, dflux = np.loadtxt(f, unpack = True)
    
    # except ValueError:
        # # Format TLUSTY, avec D comme format scientifique au lieu de E
        # f.seek(0)
        # D2E = lambda s: s.replace(b'D', b'E')
        # reg = re.compile(b'\d\.\d*-\d{3}')
        # addD = lambda s: D2E(s.replace(b'-', b'D-')) if reg.search(s) else D2E(s)
        # convert = {0: D2E,
                   # 1: addD}
                   
        # wav, flux, dflux = np.loadtxt(f, unpack = True, converters = convert)
 
    
    # return wav,flux
    
    
def spectre_tsv3(f):
    """ Lecture d'un fichier spectre en 3 colonnes
    (avec incertitudes sur flux)"""
    
    skip = 0
    while True:
        try:    
            wav, flux, dflux = np.loadtxt(f, skiprows = skip, unpack = True)
        
        except ValueError:
            # Si les première lignes ont un en-tête
            skip += 1
            
        else:
            break
            
    return wav,flux
    
    
def spectre_sdss_fits(f):
    """ Lecture d'un fichier spectre .fits du SDSS """
    hdul = fits.open(f)
    
    if 'SDSS' in hdul[0].header['TELESCOP']:
        # .fits from SDSS
        data = hdul[1].data
        
        # log10(wav) dans les .fits
        wav = 10.**data.field(1) # Angstrom
        
        # flux F_lambda en unités de 1e-17 erg/...
        flux = data.field(0)*1e-17 # erg/cm^2/s/Ang
        
        # c_ang = vitesse de la lumière en angstrom / s
        # flux *= wav**2/sc.c_ang # erg/cm^2/s/Hz
        
        hdul.close()
        return wav, flux
            
    else:
        raise Exception('.fits format inconnu')
    

def spectre_etrange(f):
    """ Lecture d'un fichier spectre Fortran imprime en 5 ou 7 colonnes """
    end = False
    while not end:
        try:
            line = f.readline().split()
            wavnew = [float(w) for w in line]
            wav = np.append(wav,wavnew)
            prevwav = wavnew[-1]
        except:
            end = True
            aflux = f.readlines()
            for line in aflux:
                line = re.sub('-10\d', 'e-100', line)
                flux = np.append(flux, line.rstrip().split())
                
    wav, flux = np.array(wav), np.array(flux)
    return wav,flux
    

def spec_info(inputfile,imodel,inu,teff):
    if imodel:
        types = 'modele'
    else:
        types = 'observation'
    if inu:
        unites = 'f_nu'
    else:
        unites = 'f_lambda'
    print(basename(inputfile)+' interprete comme '+types+' en '+unites)
    if imodel:
        print('Teff = '+str(int(teff)))
        
        
def load_spectre(inputfile):
    """ Trouve le format du fichier inputfile, puis utilise la bonne méthode
        pour lire le fichier, et retourne le spectre wav, flux, ainsi que les
        flags imodel et inu """
    
    if inputfile.endswith('fits'):
        wav, flux = spectre_sdss_fits(inputfile)
        imodel = False
        inu = False
    else:
        f = open(inputfile, 'r')
        # Lecture du header
        try:
            nn = int(f.tell())
            f.readline()
        except:
            pass
        # Lire la première ligne
        f.readline()
        # Vérifier le format dans la deuxième ligne
        test = f.readline()
        f.seek(0) # rewind jusqu'au début
        # Lecture des donnees
        if (len(test.split())==10) or (len(test.split())==6): # test62
            wav, flux = spectre_test62(f) 
            imodel = True
            inu = True
        elif(len(test.split(','))==2): # csv
            wav, flux = spectre_csv(f)
            imodel = False
            inu = False
        elif(len(test.split())==2): # tsv
            wav, flux = spectre_tsv(f)
            imodel = False
            inu = False
        elif(len(test.split())==3): # tsv avec incertitudes
            wav, flux = spectre_tsv3(f)
            imodel = False
            inu = False
        elif(len(test.split())==5 or len(test.split())==7): # format etrange
            wav, flux = spectre_etrange(f)
            imodel = False
            inu = False
        else:
            print('Erreur dans plot_spectre')
            print('Format inconnu pour '+inputfile)
        f.close()
        # flux = np.array([float(ff) for ff in flux])
        
    return wav, flux, (imodel, inu)

        
def normalisation(wav, flux):
    """ Normalisation du spectre à la valeur maximale du flux, 
        pour avoir tout les spectres sous le même ordre de grandeur """
    
    return flux / flux.max() # flux maximal = 1

    # flux_norm = flux[wav>wav_norm][0]
    # return flux / flux_norm
        

def plot_spectre(filelist, figname = None):
    """ Trace les spectres dans la liste filelist
        Si figname = None, retourne une fenêtre interactive
        Si un string est donné, enregistre la figure sous figname """

    # Matplotlib plots
    fig, ax = plt.subplots()
    ax.minorticks_on()
    
    ax.set_xlabel('Longueur d\'onde ' + r'($\AA$)')
    ax.set_ylabel(r'$F_\nu$ ' + '(normalisé)')

    for i,inputfile in enumerate(filelist):
    
        wav, flux, (imodel, inu) = load_spectre(inputfile)
        
        # Detection des unites
        if np.mean(wav) > 1e10:
            # wav en fréquence
            wav = sc.c_ang / wav
        if not imodel and np.mean(flux)<1e-20:
            inu = True
        # Conversion de f_lambda a f_nu
        if not inu:
            flux *= wav*wav/sc.c_ang

        teff = (-np.trapz(flux,x=sc.c_ang/wav)/sc.sigma*4.0*np.pi)**0.25
        spec_info(inputfile,imodel,inu,teff)
        
        flux = normalisation(wav, flux)
        ax.plot(wav, flux, label = basename(inputfile))
        
    ax.legend()
    
    if figname is None:
        plt.show(fig)
    else:
        fig.savefig(figname)
    plt.close(fig)
        

