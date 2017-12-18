import numpy as np
import matplotlib.pyplot as plt
import pylab
import os
import sys

# Ce script créeplusieurs fichiers pdf pour illustrer la structure d'un modele
# Utiliser la commande suivante pour comparer plusieurs structures:
#
# python model_analysis.py fichier1 fichier2 fichier3


# Liste de MODELS
# filenames = np.array(sys.argv[1:])

def model_analysis(filenames, nqmax = 100):

    # Declarations des arrays
    # nqmax = 100
    nq = np.zeros(len(filenames))
    tauR = np.zeros((nqmax,len(filenames)))
    kappaR = np.zeros((nqmax,len(filenames)))
    nHp = np.zeros((nqmax,len(filenames)))
    nH = np.zeros((nqmax,len(filenames)))
    nHe = np.zeros((nqmax,len(filenames)))
    nH2 = np.zeros((nqmax,len(filenames)))
    sm = np.zeros((nqmax,len(filenames)))
    entr = np.zeros((nqmax,len(filenames)))
    pres = np.zeros((nqmax,len(filenames)))
    temp = np.zeros((nqmax,len(filenames)))
    ne = np.zeros((nqmax,len(filenames)))
    dens = np.zeros((nqmax,len(filenames)))

    for ii in range(len(filenames)):
        # Header
        filename = filenames[ii]
        header1 = pylab.genfromtxt(filename,max_rows=1)
        nq[ii] = int(header1[1])

        # Bloc 1
        try:
            data1 = pylab.genfromtxt(filename,usecols=range(0,6),skip_header=3,max_rows=int(nq[ii]))
            ssk = 5
        except:
            data1 = pylab.genfromtxt(filename,usecols=range(0,6),skip_header=2,max_rows=int(nq[ii]))
            ssk = 4
        for jj in range(int(nq[ii])):
            tauR[jj,ii] = data1[jj,0]
            kappaR[jj,ii] = data1[jj,1]
            nHp[jj,ii] = data1[jj,2]
            nH[jj,ii] = data1[jj,3]
            nHe[jj,ii] = data1[jj,4]
            nH2[jj,ii] = data1[jj,5]

        # Bloc 2
        data2 = pylab.genfromtxt(filename,usecols=range(0,6),skip_header=ssk+int(nq[ii]),max_rows=int(nq[ii]))
        for jj in range(int(nq[ii])):
            sm[jj,ii] = data2[jj,0]
            tauR[jj,ii] = data2[jj,1]
            entr[jj,ii] = data2[jj,2]
            pres[jj,ii] = data2[jj,3]
            temp[jj,ii] = data2[jj,4]
            ne[jj,ii] = data2[jj,5]

    # Labels
    labels = ["" for i in range(len(filenames))]
    for ii in range(len(filenames)):
        filename = filenames[ii]
        # sind = filename.index('s')
        # filetemp = filename[sind:len(filename)]
        # uind = filename.index('_')
        # vtag = filename[sind+1:sind+uind+1]
        labels[ii]=filename

    # Plot global setups
    tableau10 = [(255,127,14),(214,39,40),(148,103,189),(44,160,44),(31,119,180),
                 (227,119,194),(188,189,34),(140,86,75),(127,127,127),(23,190,207)]
    for i in range(len(tableau10)):    
        r, g, b = tableau10[i]    
        tableau10[i] = (r / 255., g / 255., b / 255.)    

    # Figure 1: temp vs tau
    plt.figure(1)
    for ii in range(len(filenames)):
        plt.semilogx(tauR[:,ii],temp[:,ii],color=tableau10[ii],label=labels[ii])
    plt.xlabel(r'$\tau_{\mathrm{R}}$')
    ax = plt.gca()
    ax.get_yaxis().get_major_formatter().set_scientific(False)
    plt.ylabel(r'$T\;(\mathrm{K})$')
    ax.minorticks_on()
    ax.tick_params(axis='x',which='minor',bottom='off')
    plt.legend(loc=0)
    plt.savefig('Ttau.pdf')
    plt.close(1)

    # Figure 2: pres vs tau
    plt.figure(2)
    for ii in range(len(filenames)):
        plt.loglog(tauR[:,ii],pres[:,ii],color=tableau10[ii],label=labels[ii])
    ax = plt.gca()
    plt.xlabel(r'$\tau_{\mathrm{R}}$')
    plt.ylabel(r'$P\;(\mathrm{dyn/cm}^2)$')
    plt.minorticks_on()
    ax.tick_params(axis='x',which='minor',bottom='off')
    plt.legend(loc=0)
    plt.savefig('Ptau.pdf')
    plt.close(2)

    # Figure 3: dens vs tau
    plt.figure(3)
    for ii in range(len(filenames)):
        dens[:,ii] = (nH[:,ii]*1 + nHp[:,ii]*1 + nH2[:,ii]*2 + nHe[:,ii]*4)/6.022137e23
        plt.loglog(tauR[:,ii],dens[:,ii],color=tableau10[ii],label=labels[ii])
    ax = plt.gca()
    plt.xlabel(r'$\tau_{\mathrm{R}}$')
    plt.ylabel(r'$\rho\;(\mathrm{g/cm}^3)$')
    plt.minorticks_on()
    ax.tick_params(axis='x',which='minor',bottom='off')
    plt.legend(loc=0)
    plt.savefig('rhotau.pdf')
    plt.close(3)

    # Figure 4: ne vs tau
    plt.figure(4)
    for ii in range(len(filenames)):
        plt.loglog(tauR[:,ii],ne[:,ii],color=tableau10[ii],label=labels[ii])
    ax = plt.gca()
    plt.xlabel(r'$\tau_{\mathrm{R}}$')
    plt.ylabel(r'$n_e\;(\mathrm{cm}^{-3})$')
    plt.minorticks_on()
    ax.tick_params(axis='x',which='minor',bottom='off')
    plt.legend(loc=0)
    plt.savefig('netau.pdf')
    plt.close(4)

    # Figure 5: sgeo vs tauR
    plt.figure(5)
    sgeo = np.zeros((nqmax,len(filenames)))
    for ii in range(len(filenames)):
        sgeo[0,ii] = 0
        for jj in range(int(nq[ii])-1):
            sgeo[jj+1,ii] = sgeo[jj,ii] + 0.5*(tauR[jj+1,ii]+tauR[jj,ii])/kappaR[jj+1,ii]/dens[jj+1,ii]
        plt.semilogx(tauR[:,ii],sgeo[:,ii],color=tableau10[ii],label=labels[ii])
    plt.xlabel(r'$\tau_{\mathrm{R}}$')
    ax = plt.gca()
    ax.get_yaxis().get_major_formatter().set_scientific(False)
    plt.ylabel(r'$s\;(\mathrm{cm})$')
    ax.minorticks_on()
    plt.legend(loc=0)
    plt.savefig('sgeotau.pdf')
    plt.close(5)

    # Figure 6: nref vs tauR
    def nheref(tt,nhein,lambdain):
        ccgs = 2.99792458e10
        rho = nhein*2.4606682008e-49
        w = (ccgs/(lambdain*1e-8))*1.519828866e-16
        wa = 0.8227
        wb = 1.485
        fa = 0.6097
        fb = 1.065
        alpha = fa/(wa**2-w**2) + fb/(wb**2-w**2)
        AR = alpha*2.522546848e24
        BR0 = 2.6528388e-1 - 2.13313277e-2*np.sqrt(tt) + 5.67074893e-5*tt - 1.53422404e-1*np.exp(-tt/1e4)
        BR2 = 4.86326774 - 8.91357329e-2*np.sqrt(tt) + 2.44818091e-4*tt - 4.6396349*np.exp(-tt/1e4)
        BR = 1e49*(BR0 + w*w*BR2)
        RH = AR*rho + BR*rho*rho
        nfinal = np.sqrt((2.*RH+1.)/(1.-RH))
        return nfinal


    # plt.figure(6)
    # nref = np.zeros((nqmax,len(filenames)))
    # for ii in range(len(filenames)):
       # for jj in range(int(nq[ii])):
           # nref[jj,ii] = nheref(temp[jj,ii],nHe[jj,ii],5e3)
       # plt.semilogx(tauR[:,ii],nref[:,ii],color=tableau10[ii],label=labels[ii])
    # plt.xlabel(r'$\tau_{\mathrm{R}}$')
    # ax = plt.gca()
    # ax.get_yaxis().get_major_formatter().set_scientific(False)
    # plt.ylabel(r'$n\;(\mathrm{5000\AA})$')
    # plt.ylim((1,1.01*nref.max()))
    # ax.minorticks_on()
    # plt.legend(loc=0)
    # plt.savefig('nreftau.pdf')
    # plt.close(6)

    # Figure 7: P vs T 
    plt.figure(7)
    for ii in range(len(filenames)):
        plt.semilogx(pres[:,ii],temp[:,ii],color=tableau10[ii],label=labels[ii])
    plt.ylabel(r'$T\;(\mathrm{K})$')
    ax = plt.gca()
    plt.xlabel(r'$P\;(\mathrm{dyn/cm}^2)$')
    ax.minorticks_on()
    plt.legend(loc=0)
    plt.savefig('PT.pdf')
    plt.close(7)

    # Figure 8
    plt.figure(8)
    for ii in range(len(filenames)):
        plt.semilogx(tauR[:,ii],pres[:,ii]/nHe[:,ii]/temp[:,ii]/1.38e-16,color=tableau10[ii],label=labels[ii])
    ax = plt.gca()
    plt.xlabel(r'$\tau_{\mathrm{R}}$')
    plt.ylabel(r'$P/P_{\rm id}$')
    plt.minorticks_on()
    ax.tick_params(axis='x',which='minor',bottom='off')
    plt.legend(loc=0)
    plt.savefig('pnidpid.pdf')
    plt.close(8)

    # Figure 9
    plt.figure(9)
    for ii in range(len(filenames)):
        plt.loglog(tauR[:,ii],nHe[:,ii],color=tableau10[ii],label=labels[ii])
    ax = plt.gca()
    plt.xlabel(r'$\tau_{\mathrm{R}}$')
    plt.ylabel(r'$n_{\rm He}$')
    plt.minorticks_on()
    ax.tick_params(axis='x',which='minor',bottom='off')
    plt.legend(loc=0)
    plt.savefig('nhe.pdf')
    plt.close(9)
