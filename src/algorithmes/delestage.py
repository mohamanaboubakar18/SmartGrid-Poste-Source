def appliquer_delestage_intelligent(reseau):
    actions = []
    for poste in reseau.postes.values():
        if poste.est_en_surcharge():
            exces = poste.charge_actuelle_mw - (poste.capacite_mw * poste.seuil_alerte)
            actions.append(f"Délestage préventif sur {poste.nom} : -{exces:.2f} MW")
            poste.charge_actuelle_mw -= exces 
    return actions
