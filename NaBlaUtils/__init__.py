"""
Utilitaires Python pour l'analyse et la visualisation de données relatives aux
étoiles naines blanches.

Package créé par Simon Blouin en collaboration avec François Hardy
"""

from .spectres import plot_spectre, load_spectre, load_lines
from .modeles import plot_modele, load_modele
from .get_MWDD import get_MWDD_info, get_MWDD_spectra
