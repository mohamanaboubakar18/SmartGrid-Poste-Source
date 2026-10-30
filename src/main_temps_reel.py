import os
import time
import random
from modeles.reseau import ReseauElectrique
from algorithmes.delestage import appliquer_delestage_intelligent

def main():
    print("=== LANCEMENT DU SIMULATEUR SMART GRID (MODE TEMPS RÉEL) ===")
    print("Appuyez sur Ctrl+C pour arrêter la simulation.\n")
    
    config_path = os.path.join("data", "postes_sources.json")
    reseau = ReseauElectrique(config_path)

    try:
        while True:
            print("\n--------------------------------------------------")
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Acquisition flux SCADA...")
            
            for poste in reseau.postes.values():
                # Variation aléatoire simulant la charge en direct
                charge_simulee = poste.capacite_mw * random.uniform(0.6, 1.05)
                poste.mettre_a_jour_charge(round(charge_simulee, 2))
                
                statut = "🚨 SURCHARGE" if poste.est_en_surcharge() else "✅ STABLE"
                ratio = (poste.charge_actuelle_mw / poste.capacite_mw) * 100
                print(f"  - {poste.nom} : {poste.charge_actuelle_mw} MW / {poste.capacite_mw} MW ({ratio:.1f}%) | Statut : {statut}")

            actions = appliquer_delestage_intelligent(reseau)
            if actions:
                print("   ⚡ Actions de régulation automatique :")
                for action in actions:
                    print(f"      ↳ {action}")
            else:
                print("   ✔️ Réseau stable, aucune action requise.")

            # Pause de 3 secondes pour simuler le flux en direct
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nArrêt de la simulation par l'utilisateur.")

if __name__ == '__main__':
    main()
