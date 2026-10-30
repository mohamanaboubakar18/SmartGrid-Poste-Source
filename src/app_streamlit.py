import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import json

st.set_page_config(page_title="Smart Grid Supervisor", page_icon="⚡", layout="wide")

st.title("⚡ Tableau de Bord de Supervision - Smart Grid HT/BT")
st.markdown("Interface en temps réel simulant l'acquisition des flux de télémesures des postes sources (RTE / Enedis).")

# Sidebar de configuration
st.sidebar.header("Paramètres de Simulation")
frequence_rafraichissement = st.sidebar.slider("Intervalle d'actualisation (secondes)", 1, 5, 2)
seuil_critique_global = st.sidebar.slider("Seuil d'alerte global (%)", 70, 95, 85)

# Chargement de la topologie
config_path = os.path.join("data", "postes_sources.json")
if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        postes_data = json.load(f)
else:
    postes_data = [
        {"id": "PS-01", "nom": "Poste Brest Nord", "capacite_mw": 100.0, "seuil_alerte_charge": 0.85},
        {"id": "PS-02", "nom": "Poste Quimper Sud", "capacite_mw": 80.0, "seuil_alerte_charge": 0.80},
        {"id": "PS-03", "nom": "Poste Lorient Port", "capacite_mw": 120.0, "seuil_alerte_charge": 0.90}
    ]

# Zone d'affichage dynamique
placeholder = st.empty()

# Simulation d'une boucle en direct sur Streamlit
if st.sidebar.button("Démarrer / Réinitialiser la simulation"):
    st.session_state['run_sim'] = True
else:
    if 'run_sim' not in st.session_state:
        st.session_state['run_sim'] = False

if st.session_state['run_sim']:
    for _ in range(50): # Boucle de démonstration
        with placeholder.container():
            col1, col2, col3 = st.columns(3)
            
            # Génération de charges aléatoires
            charges_actuelles = []
            for i, p in enumerate(postes_data):
                charge = round(p['capacite_mw'] * np.random.uniform(0.65, 1.05), 2)
                charges_actuelles.append(charge)
                
            # KPIs en haut
            with col1:
                st.metric(label=postes_data[0]['nom'], value=f"{charges_actuelles[0]} MW", delta=f"{round((charges_actuelles[0]/postes_data[0]['capacite_mw'])*100, 1)}% Capacité")
            with col2:
                st.metric(label=postes_data[1]['nom'], value=f"{charges_actuelles[1]} MW", delta=f"{round((charges_actuelles[1]/postes_data[1]['capacite_mw'])*100, 1)}% Capacité")
            with col3:
                st.metric(label=postes_data[2]['nom'], value=f"{charges_actuelles[2]} MW", delta=f"{round((charges_actuelles[2]/postes_data[2]['capacite_mw'])*100, 1)}% Capacité")

            st.markdown("---")
            
            # Tableau de supervision détaillé
            df_suivi = pd.DataFrame({
                "Poste Source": [p['nom'] for p in postes_data],
                "Capacité Max (MW)": [p['capacite_mw'] for p in postes_data],
                "Charge Actuelle (MW)": charges_actuelles,
                "Taux de Charge": [f"{(c/p['capacite_mw'])*100:.1f}%" for c, p in zip(charges_actuelles, postes_data)],
                "Statut": ["🚨 SURCHARGE" if (c/p['capacite_mw']) >= p['seuil_alerte_charge'] else "✅ STABLE" for c, p in zip(charges_actuelles, postes_data)]
            })
            
            st.dataframe(df_suivi, use_container_width=True)
            
            # Graphique d'évolution
            chart_data = pd.DataFrame(
                {p['nom']: [c] for p, c in zip(postes_data, charges_actuelles)}
            )
            st.bar_chart(chart_data)
            
        time.sleep(frequence_rafraichissement)
else:
    st.info("Cliquez sur le bouton **'Démarrer / Réinitialiser la simulation'** dans la barre latérale pour lancer le flux de données en temps réel.")
