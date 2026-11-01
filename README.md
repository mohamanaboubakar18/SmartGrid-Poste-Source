# Simulateur Smart Grid HT/BT — Supervision SCADA, IA & Interfaçage Automate (Beckhoff ADS)

## Contexte & Objectifs du Projet

Conçu en croisant mes **6 années d'expérience terrain en maintenance de postes HT/BT (ENEO)** et ma formation d'ingénieur à l'**ENIB** (Génie Électrique, Automatique & Informatique Industrielle), ce projet modélise le fonctionnement d'un bureau d'études et d'un poste de conduite réseau (SCADA).

L'outil simule en temps réel le comportement de **postes sources HT/BT**, anticipe les défaillances thermiques des transformateurs de puissance par **Machine Learning**, exécute des algorithmes de **délestage automatique** en cas de surcharge et assure la **gestion des interfaces de simulation d'automatisme** avec un automate industriel **Beckhoff (TwinCAT)** via le protocole ADS.

## Fonctionnalités Clés

1. **Supervision Temps Réel & IHM Interactive (`app_streamlit.py`)**

   * Tableau de bord SCADA dynamique permettant le suivi en direct des flux de puissance (MW), du taux de charge (%) et des températures des transformateurs.

   * Panneau de contrôle opérateur pour régler les seuils d'alerte, la fréquence d'échantillonnage et injecter des scénarios de crise (pic hivernal, canicule, perte d'ouvrage).

2. **Interfaçage de Simulation d'Automatisme — Beckhoff TwinCAT (`interface_automate_plc.py`)**

   * Liaison bidirectionnelle entre le moteur de simulation Python et un runtime automate **Beckhoff TwinCAT 3** via le protocole **ADS (`pyads`)**.

   * Synchronisation cyclique des variables globales automate (`GVL.bLoadSheddingOrder`, `GVL.rTransformerTempC`, `GVL.rGridLoadPercent`, `GVL.bBreakerStatus`).

   * **Mode Mock PLC hors-ligne intégré :** Basculement transparent sur une mémoire automate virtuelle permettant de tester et valider l'IHM et les séquences d'automatisme sans matériel physique connecté.

3. **Maintenance Prédictive par Intelligence Artificielle (`maintenance_predictive.py`)**

   * Modèle supervisé `RandomForestClassifier` (*Scikit-Learn*) entraîné sur l'historique thermo-électrique des postes sources.

   * Prédiction en temps réel de la probabilité de défaillance d'un transformateur en fonction de la charge, de la température ambiante/point chaud et du vieillissement de l'ouvrage.

4. **Algorithme de Délestage Intelligent (`delestage.py`)**

   * Détection automatique des dépassements de capacité nominale et calcul instantané des puissances à effacer (MW) pour stabiliser le réseau et protéger les organes de coupure.

## Architecture du Dépôt

```text
Simulateur-Smart-Grid/
├── .github/workflows/
│   └── tests.yml                     # Pipeline CI/CD d'exécution automatique des tests unitaires
├── data/
│   ├── postes_sources.json           # Topologie et caractéristiques nominales des postes HT/BT
│   ├── historique_pannes.csv         # Journal d'événements et défauts réseaux
│   └── historique_complet_ml.csv     # Dataset d'entraînement thermo-électrique (500+ cycles)
├── docs/
│   ├── etat_reseau_avant.png         # Bilan graphique pré-délestage (généré par Matplotlib)
│   └── etat_reseau_apres.png         # Bilan graphique post-optimisation
├── src/
│   ├── algorithmes/
│   │   ├── delestage.py              # Logique d'effacement de charge et sécurité réseau
│   │   └── maintenance_predictive.py # Modèle Random Forest (Scikit-Learn) d'estimation de risque
│   ├── modeles/
│   │   ├── poste_source.py           # Modèle orienté objet d'un poste de transformation HT/BT
│   │   └── reseau.py                 # Gestionnaire global de la topologie électrique
│   ├── app_streamlit.py              # IHM Web interactive de supervision temps réel (SCADA)
│   ├── interface_automate_plc.py     # Gestionnaire d'interface de simulation Beckhoff ADS (pyads)
│   ├── main_temps_reel.py            # Boucle d'acquisition et de décision temps réel (Console)
│   ├── main.py                       # Script d'exécution standard et génération de bilans
│   └── visualisation.py              # Génération automatisée des graphiques statiques (.png)
├── tests/
│   └── pytest.ini                    # Configuration des tests de validation logicielle
├── .gitignore
├── requirements.txt                  # Dépendances Python (numpy, pandas, scikit-learn, streamlit, pyads)
└── README.md
```

## Détail du Module d'Interfaçage Automate (Beckhoff / ADS)

Le script `src/interface_automate_plc.py` répond aux problématiques d'**outils de gestion d'interfaces de simulation d'automatisme** (Hardware-in-the-Loop / Software-in-the-Loop) :

* **Table d'échange standardisée (Variables Globales Automate - GVL) :**

  * `GVL.rGridLoadPercent` (`REAL`) : Taux de charge instantané du transformateur (%).

  * `GVL.rTransformerTempC` (`REAL`) : Température estimée du point chaud (°C).

  * `GVL.bLoadSheddingOrder` (`BOOL`) : Ordre de délestage envoyé par le simulateur à l'automate.

  * `GVL.bBreakerStatus` (`BOOL`) : État du disjoncteur HT (ouverture de sécurité déclenchée si surcharge $> 115\,\%$).

```python
# Exemple d'exécution du couplage Simulateur Python <-> Automate Beckhoff
from interface_automate_plc import BeckhoffSimulationInterface

plc = BeckhoffSimulationInterface(ams_net_id="192.168.1.50.1.1", port=851, simulation_mode=True)
plc.connect()

# Synchronisation d'un pas de calcul avec les registres de l'automate
etat_plc = plc.sync_smartgrid_step(load_pct=96.4, temp_c=84.2, shedding_active=True)
plc.close()
```

## Installation & Démarrage Rapide

### 1. Cloner le dépôt et installer les dépendances

```bash
git clone https://github.com/mohamanaboubakar18/Simulateur-Smart-Grid.git
cd Simulateur-Smart-Grid
pip install -r requirements.txt
```

### 2. Lancer l'IHM de supervision temps réel (Streamlit)

```bash
streamlit run src/app_streamlit.py
```

### 3. Tester l'interface de simulation d'automatisme Beckhoff (ADS / Mock PLC)

```bash
python src/interface_automate_plc.py
```

### 4. Lancer la simulation complète (IA + Délestage + Graphiques PNG)

```bash
python src/main.py
```

## Auteur

**Mohaman ABOUBAKAR**

*Élève-Ingénieur à l'ENIB (Génie Électrique, Automatique & Informatique Industrielle) — Titulaire d'une Licence Pro GEII*

*6 ans d'expérience en maintenance et exploitation de postes Haute Tension (HT/BT)*

[LinkedIn](https://linkedin.com/in/mohaman-aboubakar) | mohamanaboubakar18@gmail.com