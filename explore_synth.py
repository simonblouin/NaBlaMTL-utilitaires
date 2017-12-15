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

filelist = sys.argv[1:]

################
### (1) Load ###
################

for i,inputfile in enumerate(filelist):
    wav = []
    flux = []
    end = False
    prevwav = 0
    with open(inputfile) as f:
        try:
            nn = int(f.tell())
            f.readline()
        except:
            pass
        ref = f.tell()
        test = f.readline()
        f.seek(ref)
        if (len(test.split())==10) or (len(test.split())==6): # Case 1: atmo.f output
            print('Format test62.f detecte')
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

        elif(len(test.split(','))==2): # Case 2: csv file
            print('Format csv detecte')
            reader = csv.reader(f)
            for row in reader:
                if row:
                    wavnew, fluxnew = row
                    wav = np.append(wav, float(wavnew))
                    flux = np.append(flux, float(fluxnew))

        elif(len(test.split())==2): # Case 2: tsv file
            print('Format tsv detecte')
            while not end:
                try:
                    line = f.readline().split()
                    wavnew, fluxnew = line
                    wav = np.append(wav,float(wavnew))
                    flux = np.append(flux,float(fluxnew))
                except:
                    end = True
                    
        elif(len(test.split())==3): # Case 3: 3rd column=sigma
            print('Format avec incertitudes detecte')
            while not end:
                try:
                    line = f.readline().split()
                    wavnew, fluxnew, _  = line
                    wav = np.append(wav,float(wavnew))
                    flux = np.append(flux,float(fluxnew))
                except:
                    end = True

        elif(len(test.split())==5 or len(test.split())==7): # Case 4: weird format
            print('Format etrange detecte')
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

        # Save data to pd dataframe
        x = wav
        if i==0:
            xmin = np.min(x)
            xmax = np.max(x)
        else:
            nxmin = np.min(x)
            nxmax = np.max(x)
            if(nxmin > xmin): xmin = nxmin
            if(nxmax < xmax): xmax = nxmax
        y = [float(ff) for ff in flux]
        print((-np.trapz(y,x=2.997e18/x)/5.678e-5*4.0*np.pi)**0.25)
        if i==0:
            d = {'x'+inputfile: x, 'y'+inputfile: y, 
                 'x'+inputfile+'save': x, 'y'+inputfile+'save': y}
            df = pd.DataFrame(d)
        else:
            d = {'x'+inputfile: x, 'y'+inputfile: y, 
                 'x'+inputfile+'save': x, 'y'+inputfile+'save': y}
            dfp = pd.DataFrame(d)
            df = pd.concat([df,dfp], ignore_index=False, axis=1)

#####################
### (2) Callbacks ###
#####################

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


################
### (3) Plot ###
################

plot = Figure(tools="pan,wheel_zoom,box_zoom,reset,previewsave",
              plot_width=1000,plot_height=800,
              x_axis_label='Lambda (A)', y_axis_label='Flux')
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
