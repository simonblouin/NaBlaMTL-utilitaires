import json

def get_MWDD_info(name):
    """ Retourne un dict avec les parametres de l'etoile donnee en input """
    data = json.load(open('MWDD_table.json'))
    for entry in data['data']:
        try:
            namelist = entry['allnames']+entry['wdid']+entry['name']
        except KeyError:
            namelist = entry['allnames']+entry['wdid']
        if name.lower().replace(' ', '') in namelist.lower().replace(' ', ''):
            return entry
