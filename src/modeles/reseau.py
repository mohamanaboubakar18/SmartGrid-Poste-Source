import json
from .poste_source import PosteSource

class ReseauElectrique:
    def __init__(self, fichier_config):
        self.postes = {}
        with open(fichier_config, 'r', encoding='utf-8') as f:
            for p in json.load(f):
                self.postes[p['id']] = PosteSource(p['id'], p['nom'], p['capacite_mw'], p['seuil_alerte_charge'])
