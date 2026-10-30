class PosteSource:
    def __init__(self, id_poste, nom, capacite_mw, seuil_alerte_charge):
        self.id = id_poste
        self.nom = nom
        self.capacite_mw = capacite_mw
        self.seuil_alerte = seuil_alerte_charge
        self.charge_actuelle_mw = 0.0

    def mettre_a_jour_charge(self, charge_mw):
        self.charge_actuelle_mw = charge_mw

    def est_en_surcharge(self):
        return (self.charge_actuelle_mw / self.capacite_mw) >= self.seuil_alerte
