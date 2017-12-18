from bokeh.layouts import column
from bokeh.models import CustomJS, ColumnDataSource, Slider, DataRange1d
from bokeh.plotting import Figure, output_file, show
from bokeh.palettes import Dark2_8
from bokeh.models.widgets import Toggle
import csv
import numpy as np
import pandas as pd
import re
import sys


def spectre_test62(f):
    """ Lecture d'un fichier spectre synthetique de test62 """
    wav = []
    flux = []
    end = False
    prevwav = 0
    while not end:
        try:
            line = re.findall('([\d\s]*\.\d{2})',f.readline())
            wavnew = [float(w) for w in line]
            if(wavnew[-1] <= prevwav):
                end = True
            else:
                wav = np.append(wav,wavnew)
                prevwav = wavnew[-1]
        except:
            end = True
    aflux = f.readlines()
    for line in aflux:
        line = re.sub('-10\d', 'e-100', line)
        flux = np.append(flux, line.rstrip().split())
    return wav,flux
    

def spectre_csv(f):
    """ Lecture d'un fichier spectre d'un fichier csv en 2 colonnes """
    wav = []
    flux = []
    reader = csv.reader(f)
    for row in reader:
        if row:
            wavnew, fluxnew = row
            wav = np.append(wav, float(wavnew))
            flux = np.append(flux, float(fluxnew))
    return wav,flux
    

def spectre_tsv(f):
    """ Lecture d'un fichier spectre en 2 colonnes """
    wav = []
    flux = []
    end = False
    while not end:
        try:
            line = f.readline().split()
            wavnew, fluxnew = line
            wav = np.append(wav,float(wavnew))
            flux = np.append(flux,float(fluxnew))
        except:
            end = True
    return wav,flux
    

def spectre_tsv3(f):
    """ Lecture d'un fichier spectre en 3 colonnes (avec incertitudes sur flux)"""
    while not end:
        try:
            line = f.readline().split()
            wavnew, fluxnew, _  = line
            wav = np.append(wav,float(wavnew))
            flux = np.append(flux,float(fluxnew))
        except:
            end = True
    return wav,flux
    
    
def spectre_sdss_fits(f):
    hdul = fits.open(synth_file)
    
    if 'SDSS' in hdul[0].header['TELESCOP']:
        # .fits from SDSS
        data = hdul[1].data
        
        # log10(wav) dans les .fits
        wav = 10.**data.field(1) # Angstrom
        
        # flux F_lambda en unités de 1e-17 erg/...
        flux = data.field(0)*1e-17 # erg/cm^2/s/Ang
        
        # c_ang = vitesse de la lumière en angstrom / s
        flux *= wav**2/sc.c_ang # erg/cm^2/s/Hz
        
        return wav, flux
            
    else:
        raise Exception('.fits format inconnu')
    

def spectre_etrange(f):
    """ Lecture d'un fichier spectre Fortran imprime en 5 ou 7 colonnes """
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
    print(inputfile+' interprete comme '+types+' en '+unites)
    if imodel:
        print('Teff = '+str(int(teff)))
        

def plot_spectre(filelist):
    for i,inputfile in enumerate(filelist):
        if inputfile.endswith('fits'):
            wav, flux = spectre_sdss_fits(inputfile)
            imodel = False
            inu = True
        else:
            f = open(inputfile, 'r')
            # Lecture du header
            try:
                nn = int(f.tell())
                f.readline()
            except:
                pass
            ref = f.tell()
            test = f.readline()
            f.seek(ref)
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
                
            
            flux = np.array([float(ff) for ff in flux])
            # Detection des unites
            if not imodel and np.mean(flux)<1e-20:
                inu = True
            # Conversion de f_lambda a f_nu
            if not inu:
                flux *= wav*wav/1e8/2.998e10
            # Save data to pd dataframe
            x = wav
            y = flux
            if i==0:
                xmin = np.min(x)
                xmax = np.max(x)
            else:
                nxmin = np.min(x)
                nxmax = np.max(x)
                if(nxmin > xmin): xmin = nxmin
                if(nxmax < xmax): xmax = nxmax
            teff = (-np.trapz(y,x=2.997e18/x)/5.678e-5*4.0*np.pi)**0.25
            spec_info(inputfile,imodel,inu,teff)
            if i==0:
                d = {'x'+inputfile: x, 'y'+inputfile: y, 
                     'x'+inputfile+'save': x, 'y'+inputfile+'save': y}
                df = pd.DataFrame(d)
            else:
                d = {'x'+inputfile: x, 'y'+inputfile: y, 
                     'x'+inputfile+'save': x, 'y'+inputfile+'save': y}
                dfp = pd.DataFrame(d)
                df = pd.concat([df,dfp], ignore_index=False, axis=1)

    # Bokeh callbacks
    d = {'inorm': [0,4500]}
    dfp = pd.DataFrame(d)
    df = pd.concat([df,dfp], ignore_index=False, axis=1)

    d = {'filelist': np.insert(filelist,0,len(filelist))}
    dfp = pd.DataFrame(d)
    df = pd.concat([df,dfp], ignore_index=False, axis=1)

    source = ColumnDataSource(data=df)

    def slider_CB(source=source, window=None):
        data = source.data
        f = float(cb_obj.value)
        inorm = data['inorm']
        data['inorm'][1] = f
        filelist = data['filelist']
        for j in range(int(filelist[0])):
            x, y = data['x'+filelist[j+1]], data['y'+filelist[j+1]]
            xs, ys = data['x'+filelist[j+1]+'save'], data['y'+filelist[j+1]+'save']
            distmin = 1e4
            if(data['inorm'][0]==1):
                for i in range(len(xs)):
                    dist = abs(xs[i]-f)
                    if(dist < distmin):
                        ind = i
                        distmin = dist
                indref = data['inorm'][1]
                indref = ind
                for i in range(len(xs)):
                    y[i] = ys[i]/ys[ind]
            else:
                for i in range(len(xs)):
                    y[i] = ys[i]
            source.trigger('change')

    def norm_CB(source=source, window=None):
        data = source.data
        inorm = data['inorm']
        if inorm[0]==1:
            inorm[0] = 0
        elif inorm[0]==0:
            inorm[0] = 1
        source.trigger('change')
        filelist = data['filelist']
        f = data['inorm'][1]
        for j in range(int(filelist[0])):
            x, y = data['x'+filelist[j+1]], data['y'+filelist[j+1]]
            xs, ys = data['x'+filelist[j+1]+'save'], data['y'+filelist[j+1]+'save']
            distmin = 1e4
            if(data['inorm'][0]==1):
                for i in range(len(xs)):
                    dist = abs(xs[i]-f)
                    if(dist < distmin):
                        ind = i
                        distmin = dist
                        indref = data['inorm'][1]
                indref = ind
                for i in range(len(xs)):
                    y[i] = ys[i]/ys[ind]
            else:
                for i in range(len(xs)):
                    y[i] = ys[i]
            source.trigger('change')

    # Bokeh plot
    plot = Figure(tools="pan,wheel_zoom,box_zoom,reset,previewsave",
                  plot_width=1000,plot_height=800,
                  x_axis_label='Lambda (A)', y_axis_label='Flux F_nu')
    plot.x_range = DataRange1d(start=xmin, end=xmax) 
    for i,inputfile in enumerate(filelist):
        plot.line('x'+inputfile, 'y'+inputfile, source=source, 
                  line_width=3, line_alpha=0.9, line_color=Dark2_8[i],
                  legend=inputfile)
    slider = Slider(start=2000, end=8000, value=5000, step=100, title="Normalization wavelength",
                    callback=CustomJS.from_py_func(slider_CB))
    button = Toggle(label="Normalize", name="1", callback=CustomJS.from_py_func(norm_CB))
    layout = column(button, slider, plot)

    show(layout)
