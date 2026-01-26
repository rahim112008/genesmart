import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="GeneSmart Expert v3.0", layout="wide", page_icon="🧬")

# --- 2. INITIALISATION (L'âge est ajouté ici dans la structure) ---
if 'db_data' not in st.session_state:
    st.session_state.db_data = pd.DataFrame({
        "ID Animal": ["DZ-2026-001", "DZ-2026-002"],
        "Âge": ["2 dents", "Dents de lait"], # Colonne synchronisée
        "Région": ["Hauts Plateaux", "Steppe"],
        "Poids (kg)": [45.0, 58.5],
        "Hauteur Garrot": [75.0, 78.0],
        "Périmètre Thoracique": [92.0, 98.0],
        "Long. Corps": [82.0, 85.0],
        "Larg. Poitrine": [28.0, 32.0]
    })

# --- 3. MENU ---
st.sidebar.title("🧬 GeneSmart Pro")
menu = st.sidebar.radio("Expertise & Analyse", [
    "📊 Tableau de Bord", 
    "🆔 Identification (30 Car.)", 
    "🔍 Recherche & Prédiction",
    "🗂️ Gestion de la Base"
])

# --- 4. LOGIQUE DES PAGES ---

if menu == "📊 Tableau de Bord":
    st.title("📊 Analyses Statistiques")
    # Petit bonus : Statistique par Âge
    fig_age = px.box(st.session_state.db_data, x='Âge', y='Poids (kg)', color='Âge', title="Répartition du Poids par Stade d'Âge")
    st.plotly_chart(fig_age, use_container_width=True)

elif menu == "🆔 Identification (30 Car.)":
    st.title("🆔 Caractérisation Phénotypique")
    with st.form("id_form"):
        id_an = st.text_input("ID Animal", "DZ-2026-")
        # AJOUT DE LA CASE ÂGE
        v_age = st.selectbox("Âge (Dentition)", ["Dents de lait", "2 dents", "4 dents", "6 dents", "8 dents"])
        
        c1, c2 = st.columns(2)
        v1 = c1.number_input("Poids (kg)", 20.0, 120.0, 50.0)
        v2 = c2.number_input("Hauteur Garrot (cm)", 40.0, 100.0, 75.0)
        v5 = c1.number_input("Périmètre Thoracique (cm)", 50.0, 130.0, 90.0)
        v4 = c2.number_input("Longueur Corps (cm)", 40.0, 120.0, 80.0)
        
        if st.form_submit_button("💾 Enregistrer l'animal"):
            new_row = {
                "ID Animal": id_an, 
                "Âge": v_age, # L'âge est capturé ici
                "Région": "Inconnue", 
                "Poids (kg)": v1, 
                "Hauteur Garrot": v2, 
                "Périmètre Thoracique": v5, 
                "Long. Corps": v4, 
                "Larg. Poitrine": 25.0
            }
            st.session_state.db_data = pd.concat([st.session_state.db_data, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"Animal {id_an} enregistré avec le stade {v_age} !")

elif menu == "🔍 Recherche & Prédiction":
    st.title("🔍 Expertise & Prédiction")
    id_sel = st.selectbox("Choisir l'animal :", st.session_state.db_data["ID Animal"])
    
    # RÉCUPÉRATION AUTOMATIQUE
    data = st.session_state.db_data[st.session_state.db_data["ID Animal"] == id_sel].iloc[0]
    
    st.info(f"📌 **Détails de l'individu :** ID: {id_sel} | Stade: {data['Âge']}")
    
    it = data["Périmètre Thoracique"] / data["Hauteur Garrot"]
    st.metric("Indice Thoracique", f"{it:.2f}")

elif menu == "🗂️ Gestion de la Base":
    st.title("🗂️ Gestion & Export")
    # L'âge apparaît ici automatiquement dans le tableau
    edited_df = st.data_editor(st.session_state.db_data, use_container_width=True)
    if st.button("💾 Sauvegarder"):
        st.session_state.db_data = edited_df
        st.success("Base mise à jour !")
