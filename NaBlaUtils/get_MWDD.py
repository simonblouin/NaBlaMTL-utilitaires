import json
from urllib.request import urlopen

def get_MWDD_info(name):
    """ Retourne un dict avec les parametres de l'etoile donnee en input """
    data = json.load(open('MWDD_table.json', encoding='latin1'))
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
        s[1] = s[1].decode("utf-8").strip()
        for line in data:
            if s[1]=='wavelength,flux':
                x, y = tuple(line)
                x = float(x)
                y = float(y)
            elif s[1]=='wavelength,flux,sigma':
                x, y, _ = tuple(line)
                x = float(x)
                y = float(y)
            elif s[1]=='wavelength,flux,sigma,flag':
                x, y, _, _ = tuple(line)
                x = float(x)
                y = float(y)
            else:
                print('Format inconnu '+spec)
            xvec.append(x)
            yvec.append(y)
        output[spec.replace('%20', '_')] = [xvec,yvec]
    return output
