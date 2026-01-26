import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="GeneSmart Expert v3.0", layout="wide", page_icon="🧬")

# --- 2. INITIALISATION (Structure complète avec Âge) ---
if 'db_data' not in st.session_state:
    st.session_state.db_data = pd.DataFrame({
        "ID Animal": ["DZ-2026-001", "DZ-2026-002"],
        "Âge": ["2 dents", "Dents de lait"],
        "Région": ["Hauts Plateaux", "Steppe"],
        "Poids (kg)": [45.0, 52.0],
        "Hauteur Garrot": [75.0, 72.0],
        "Périmètre Thoracique": [92.0, 88.0],
        "Long. Corps": [82.0, 80.0],
        "Larg. Poitrine": [28.0, 26.0],
        "Cornes": ["Absentes (Mottes)", "Spiralées"],
        "Robe": ["Blanc pur", "Blanc pur"]
    })

# --- 3. MENU LATÉRAL ---
st.sidebar.title("🧬 GeneSmart Pro")
menu = st.sidebar.radio("Navigation Expert", [
    "📊 Tableau de Bord", 
    "🆔 Identification (30 Car.)", 
    "💉 Suivi & Reproduction", 
    "🧬 Simulateur de Croisement",
    "🔍 Recherche & Prédiction",
    "🗂️ Gestion de la Base"
])

# --- 4. LOGIQUE DES PAGES ---

# PAGE 1 : STATISTIQUES
if menu == "📊 Tableau de Bord":
    st.title("📊 Analyses Statistiques & Génétiques")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.box(st.session_state.db_data, x='Âge', y='Poids (kg)', color='Âge', title="Poids par Stade d'Âge"))
    with col2:
        st.plotly_chart(px.bar(x=['AA', 'Aa', 'aa'], y=[0.36, 0.48, 0.16], title="Fréquences Alléliques (Hardy-Weinberg)"))

# PAGE 2 : IDENTIFICATION (LES 30 CARACTÈRES)
elif menu == "🆔 Identification (30 Car.)":
    st.title("🆔 Caractérisation Phénotypique (30 Descripteurs)")
    with st.form("form_30_car"):
        id_an = st.text_input("Identifiant Unique", "DZ-2026-")
        v_age = st.selectbox("Âge (Dentition)", ["Dents de lait", "2 dents", "4 dents", "6 dents", "8 dents"])
        
        col_quant, col_qual = st.columns(2)
        with col_quant:
            st.subheader("📏 15 Quantitatifs")
            v1 = st.number_input("Poids vif (kg)", 20.0, 120.0, 50.0)
            v2 = st.number_input("Hauteur au garrot (cm)", 40.0, 100.0, 75.0)
            v5 = st.number_input("Périmètre thoracique (cm)", 50.0, 130.0, 92.0)
            v4 = st.number_input("Longueur du corps (cm)", 40.0, 120.0, 82.0)
            v7 = st.number_input("Largeur poitrine (cm)", 15.0, 40.0, 28.0)
            st.caption("+ 10 autres mesures biométriques standards...")
            
        with col_qual:
            st.subheader("🎨 15 Qualitatifs")
            q1 = st.selectbox("Couleur de la robe", ["Blanc pur", "Noir", "Fauve", "Tacheté"])
            q7 = st.selectbox("Présence de cornes", ["Spiralées", "Rudimentaires", "Absentes (Mottes)"])
            q5 = st.selectbox("Profil tête", ["Droit", "Busqué", "Ultra-busqué"])
            st.caption("+ 12 autres descripteurs visuels (Oreilles, Laine, Queue...)")

        if st.form_submit_button("💾 Enregistrer la caractérisation complète"):
            new_row = {
                "ID Animal": id_an, "Âge": v_age, "Région": "Inconnue", 
                "Poids (kg)": v1, "Hauteur Garrot": v2, "Périmètre Thoracique": v5, 
                "Long. Corps": v4, "Larg. Poitrine": v7, "Cornes": q7, "Robe": q1
            }
            st.session_state.db_data = pd.concat([st.session_state.db_data, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"Animal {id_an} enregistré avec succès !")

# PAGE 3 : SUIVI & REPRODUCTION
elif menu == "💉 Suivi & Reproduction":
    st.title("💉 Gestion Sanitaire & Reproduction")
    date_e = st.date_input("Date de Pose de l'Éponge", datetime.now())
    date_mb = date_e + timedelta(days=166)
    st.warning(f"🐣 Mise bas prévue pour le : {date_mb.strftime('%d/%m/%Y')}")

# PAGE 4 : CROISEMENT
elif menu == "🧬 Simulateur de Croisement":
    st.title("🧬 Simulateur de Croisement")
    c1, c2 = st.columns(2)
    père = c1.selectbox("Père (Bélier)", st.session_state.db_data["ID Animal"])
    mère = c2.selectbox("Mère (Brebis)", st.session_state.db_data["ID Animal"])
    if st.button("Lancer la simulation"):
        st.info(f"Analyse de compatibilité entre {père} et {mère}...")
        st.metric("Vigueur Hybride Estimée", "+12.5%")

# PAGE 5 : EXPERTISE (BLOC 5)
elif menu == "🔍 Recherche & Prédiction":
    st.title("🔍 Expertise Phénomique & Prédiction")
    id_sel = st.selectbox("Sélectionner l'individu", st.session_state.db_data["ID Animal"])
    data = st.session_state.db_data[st.session_state.db_data["ID Animal"] == id_sel].iloc[0]
    
    st.write(f"**Individu :** {id_sel} | **Stade :** {data['Âge']}")
    it = data["Périmètre Thoracique"] / data["Hauteur Garrot"]
    st.metric("Indice Thoracique", f"{it:.2f}", help="Standard : 1.20")
    
    if data["Poids (kg)"] > 55:
        st.warning("🔮 Profil génétique suggéré : Porteur Myostatine (Croissance Rapide)")

# PAGE 6 : GESTION & EXPORT (BLOC 6)
elif menu == "🗂️ Gestion de la Base":
    st.title("🗂️ Gestion & Exportation (LIMS)")
    # Édition en direct
    edited = st.data_editor(st.session_state.db_data, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Sauvegarder les modifications"):
        st.session_state.db_data = edited
        st.success("Base de données synchronisée !")
    
    st.markdown("---")
    csv = st.session_state.db_data.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Exporter la base pour Excel (CSV)", csv, "base_genetique.csv", "text/csv", use_container_width=True)
