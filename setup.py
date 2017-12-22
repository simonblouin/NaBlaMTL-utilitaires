from setuptools import setup, find_packages

setup(name='NaBlaUtils',
      version='0.1',
      description="Utilitaires Python pour l'analyse et la visualisation de données relatives aux étoiles naines blanches",
      url='https://github.com/simonblouin/NaBlaMTL-utilitaires',
      package_data={'': ['lines.csv', 'MWDD_table.json']},
      packages=find_packages())

