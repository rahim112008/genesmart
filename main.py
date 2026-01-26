import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="GeneSmart Expert v3.0", layout="wide", page_icon="🧬")

# --- 2. INITIALISATION DES DONNÉES ---
if 'db_data' not in st.session_state:
    st.session_state.db_data = pd.DataFrame({
        "ID Animal": ["DZ-2026-001", "DZ-2026-002"],
        "Région": ["Hauts Plateaux", "Steppe"],
        "Poids (kg)": [45.0, 58.5],
        "Hauteur Garrot": [75.0, 78.0],
        "Périmètre Thoracique": [92.0, 98.0],
        "Long. Corps": [82.0, 85.0],
        "Larg. Poitrine": [28.0, 32.0],
        "Cornes": ["Absentes (Mottes)", "Spiralées"],
        "Robe": ["Blanc pur", "Blanc pur"]
    })

# --- 3. BARRE LATÉRALE (Noms exacts pour éviter l'écran noir) ---
st.sidebar.title("🧬 GeneSmart Pro")
menu = st.sidebar.radio("Expertise & Analyse", [
    "📊 Tableau de Bord", 
    "🆔 Identification (30 Car.)", 
    "💉 Suivi & Reproduction", 
    "🧬 Simulateur de Croisement",
    "🔍 Recherche & Prédiction",
    "🗂️ Gestion de la Base"
])

# --- 4. LOGIQUE DES PAGES ---

if menu == "📊 Tableau de Bord":
    st.title("📊 Analyses Statistiques")
    t1, t2 = st.tabs(["Génétique", "Statistiques"])
    with t1:
        st.metric("Taille Efficace (Ne)", "64.2")
        st.plotly_chart(px.bar(x=['AA', 'Aa', 'aa'], y=[0.36, 0.48, 0.16], title="Fréquences Alléliques"))
    with t2:
        st.plotly_chart(px.box(st.session_state.db_data, x='Région', y='Poids (kg)', color='Région'))

elif menu == "🆔 Identification (30 Car.)":
    st.title("🆔 Caractérisation Phénotypique")
    with st.form("id_form"):
        id_an = st.text_input("ID Animal", "DZ-2026-")
        c1, c2 = st.columns(2)
        v1 = c1.number_input("Poids (kg)", 20.0, 120.0, 50.0)
        v2 = c2.number_input("Hauteur Garrot (cm)", 40.0, 100.0, 75.0)
        v5 = c1.number_input("Périmètre Thoracique (cm)", 50.0, 130.0, 90.0)
        v4 = c2.number_input("Longueur Corps (cm)", 40.0, 120.0, 80.0)
        v7 = c1.number_input("Largeur Poitrine (cm)", 15.0, 40.0, 28.0)
        q7 = c2.selectbox("Cornes", ["Spiralées", "Rudimentaires", "Absentes (Mottes)"])
        if st.form_submit_button("Enregistrer"):
            new_row = {"ID Animal": id_an, "Région": "Inconnue", "Poids (kg)": v1, "Hauteur Garrot": v2, 
                        "Périmètre Thoracique": v5, "Long. Corps": v4, "Larg. Poitrine": v7, "Cornes": q7}
            st.session_state.db_data = pd.concat([st.session_state.db_data, pd.DataFrame([new_row])], ignore_index=True)
            st.success("Enregistré !")

elif menu == "💉 Suivi & Reproduction":
    st.title("💉 Santé & Reproduction")
    date_e = st.date_input("Date Pose Éponge", datetime.now())
    st.info(f"Mise bas prévue : {(date_e + timedelta(days=166)).strftime('%d/%m/%Y')}")

elif menu == "🧬 Simulateur de Croisement":
    st.title("🧬 Croisement")
    st.selectbox("Père", st.session_state.db_data["ID Animal"])
    st.selectbox("Mère", st.session_state.db_data["ID Animal"])
    if st.button("Simuler"):
        st.balloons()

elif menu == "🔍 Recherche & Prédiction":
    st.title("🔍 Bloc 5 : Expertise & Prédiction")
    id_sel = st.selectbox("Choisir l'animal :", st.session_state.db_data["ID Animal"])
    data = st.session_state.db_data[st.session_state.db_data["ID Animal"] == id_sel].iloc[0]
    
    # Calculs
    it = data["Périmètre Thoracique"] / data["Hauteur Garrot"]
    st.metric("Indice Thoracique", f"{it:.2f}")
    
    # Graphique Radar
    fig = go.Figure(data=go.Scatterpolar(
        r=[data["Poids (kg)"]/60, it/1.2, data["Larg. Poitrine"]/30],
        theta=['Poids','Thorax','Largeur'], fill='toself'
    ))
    st.plotly_chart(fig)
    

elif menu == "🗂️ Gestion de la Base":
    st.title("🗂️ Bloc 6 : Gestion & Export")
    st.data_editor(st.session_state.db_data, use_container_width=True)
    csv = st.session_state.db_data.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Télécharger CSV", csv, "base.csv", "text/csv")
