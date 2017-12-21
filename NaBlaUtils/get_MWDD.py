import numpy as np
import json
from urllib.request import urlopen
import pkg_resources

def get_MWDD_info(name):
    """ Retourne un dict avec les parametres de l'etoile donnee en input """
    MWDD_table = pkg_resources.resource_stream(__name__, 'MWDD_table.json')
    data = json.load(MWDD_table)
    for entry in data['data']:
        try:
            namelist = entry['allnames']+entry['wdid']+entry['name']
        except KeyError:
            namelist = entry['allnames']+entry['wdid']
        if name.lower().replace(' ', '') in namelist.lower().replace(' ', ''):
            return entry

def get_MWDD_wdid(name):
    """ Retourne l'identifiant unique d'une etoile dans MWDD """
    return get_MWDD_info(name)['wdid']

def get_MWDD_spectra(name):
    """ Retourne un dict contenant tous les spectres de l'etoile demandee dans MWDD """
    output = {}
    wdid = get_MWDD_wdid(name)
    site = 'http://montrealwhitedwarfdatabase.org/WDs/'
    tar = site+wdid+'/spectlist.txt'
    tar = tar.replace(' ', '%20')
    f = str(urlopen(tar).read())
    f = f.replace(' ', '%20').replace(r'\n', ' ').replace("'", '')
    listspec = f.split()[1:]
    for spec in listspec:
        xvec = []
        yvec = []
        s = urlopen(site+wdid.replace(' ', '%20')+'/'+spec).readlines()
        data = [line.decode("utf-8").strip().split(',')  for line in s[2:]]
        s[1] = s[1].decode("utf-8").strip().split(',')
        # print(s[1])
        # print(s[1].split(','))
        for line in data:
            if len(s[1])==2: # wavelength,flux
                x, y = tuple(line)
                x = float(x)
                y = float(y)
            elif len(s[1])==3: # wavelength,flux,sigma
                x, y, _ = tuple(line)
                x = float(x)
                y = float(y)
            elif len(s[1])==4: # wavelength,flux,sigma,flag
                x, y, _, _ = tuple(line)
                x = float(x)
                y = float(y)
            else:
                raise NotImplementedError('Format inconnu '+spec)
            xvec.append(x)
            yvec.append(y)
        output[spec.replace('%20', '_')] = np.array([xvec,yvec])
    return output
