import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import time

# --- CONFIGURATION INTERFACE ---
st.set_page_config(
    page_title="GeneSmart Expert v3.0", 
    layout="wide", 
    page_icon="🧬"
)

# --- INITIALISATION DE LA BASE (Session State) ---
# On crée une structure qui accepte tous les caractères phénotypiques dès le début
if 'db_data' not in st.session_state:
    st.session_state.db_data = pd.DataFrame(columns=[
        "ID Animal", "Région", "Poids (kg)", "Hauteur Garrot", "Périmètre Thoracique", 
        "Long. Corps", "Larg. Poitrine", "Cornes", "Robe", "Date Enregistrement"
    ])
    # Données démo
    demo = pd.DataFrame({
        "ID Animal": ["DZ-2026-001", "DZ-2026-002"],
        "Région": ["Hauts Plateaux", "Steppe"],
        "Poids (kg)": [45.0, 58.5],
        "Hauteur Garrot": [75.0, 78.0],
        "Périmètre Thoracique": [92.0, 98.0],
        "Long. Corps": [82.0, 85.0],
        "Larg. Poitrine": [28.0, 32.0],
        "Cornes": ["Absentes (Mottes)", "Spiralées"],
        "Robe": ["Blanc pur", "Blanc pur"],
        "Date Enregistrement": [datetime.now().date(), datetime.now().date()]
    })
    st.session_state.db_data = pd.concat([st.session_state.db_data, demo], ignore_index=True)

# --- NAVIGATION LATÉRALE ---
st.sidebar.title("🧬 GeneSmart Pro")
st.sidebar.info(f"Base de données : {len(st.session_state.db_data)} individus")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Expertise & Analyse", [
    "📊 Tableau de Bord", 
    "🆔 Identification (30 Car.)", 
    "💉 Suivi & Reproduction", 
    "🧬 Simulateur de Croisement",
    "🔍 Recherche & Prédiction (Bloc 5)",
    "🗂️ Gestion & Export (Bloc 6)"
])

# --- PAGE 1 : ANALYSES STATISTIQUES ---
if menu == "📊 Tableau de Bord":
    st.title("📊 Analyses Statistiques & Génétiques")
    t_gen, t_multi, t_anova = st.tabs(["🧬 Génétique", "📉 ACP / ACM", "🧪 ANOVA"])
    
    with t_gen:
        c1, c2 = st.columns(2)
        c1.metric("Taille Efficace (Ne)", "64.2", "🟢 Stable")
        c2.metric("Indice Fis", "0.058", "🟢 Faible")
        st.plotly_chart(px.bar(x=['AA', 'Aa', 'aa'], y=[0.36, 0.48, 0.16], 
                               labels={'x':'Génotypes', 'y':'Fréquences'},
                               title="Fréquences Alléliques (Hardy-Weinberg)"), use_container_width=True)
    
    with t_multi:
        st.subheader("📉 Analyse en Composantes Principales (ACP)")
        df_acp = pd.DataFrame({
            'PC1': np.random.randn(30), 'PC2': np.random.randn(30),
            'Race': ['Ouled Djellal']*15 + ['Rembi']*15
        })
        st.plotly_chart(px.scatter(df_acp, x='PC1', y='PC2', color='Race', title="Plan Factoriel : Proximité Génétique"), use_container_width=True)

    with t_anova:
        st.subheader("🧪 Analyse de la Variance (ANOVA)")
        st.plotly_chart(px.box(st.session_state.db_data, x='Région', y='Poids (kg)', color='Région', title="Poids par Région"), use_container_width=True)

# --- PAGE 2 : IDENTIFICATION (30 CARACTÈRES) ---
elif menu == "🆔 Identification (30 Car.)":
    st.title("🆔 Caractérisation Phénotypique")
    
    with st.form("form_caracterisation"):
        id_an = st.text_input("Identifiant Unique", "DZ-2026-")
        reg = st.selectbox("Région", ["Hauts Plateaux", "Steppe", "Nord", "Sahara"])
        
        col_quant, col_qual = st.columns(2)
        with col_quant:
            st.subheader("📏 Quantitatifs")
            v1 = st.number_input("Poids vif (kg)", 20.0, 120.0, 50.0)
            v2 = st.number_input("Hauteur au garrot (cm)", 40.0, 100.0, 75.0)
            v5 = st.number_input("Périmètre thoracique (cm)", 50.0, 130.0, 90.0)
            v4 = st.number_input("Longueur du corps (cm)", 40.0, 120.0, 80.0)
            v7 = st.number_input("Largeur poitrine (cm)", 15.0, 40.0, 28.0)
        
        with col_qual:
            st.subheader("🎨 Qualitatifs")
            q1 = st.selectbox("Couleur de la robe", ["Blanc pur", "Noir", "Fauve"])
            q7 = st.selectbox("Présence de cornes", ["Spiralées", "Rudimentaires", "Absentes (Mottes)"])
            q5 = st.selectbox("Profil tête", ["Droit", "Busqué", "Ultra-busqué"])

        submit = st.form_submit_button("💾 Enregistrer dans la base", use_container_width=True)
        
        if submit:
            new_data = {
                "ID Animal": id_an, "Région": reg, "Poids (kg)": v1, 
                "Hauteur Garrot": v2, "Périmètre Thoracique": v5, 
                "Long. Corps": v4, "Larg. Poitrine": v7,
                "Cornes": q7, "Robe": q1, "Date Enregistrement": datetime.now().date()
            }
            st.session_state.db_data = pd.concat([st.session_state.db_data, pd.DataFrame([new_data])], ignore_index=True)
            st.success(f"Animal {id_an} enregistré !")
            st.balloons()

# --- PAGE 5 : EXPERTISE & PRÉDICTION ---
elif menu == "🔍 Recherche GenBank (NCBI)":
    st.title("🔬 Expertise & Prédiction")
    
    liste_ids = st.session_state.db_data["ID Animal"].tolist()
    id_select = st.selectbox("🎯 Choisir l'animal à analyser :", liste_ids)
    
    # Récupération des données réelles
    row = st.session_state.db_data[st.session_state.db_data["ID Animal"] == id_select].iloc[0]
    
    t1, t2 = st.tabs(["📊 Index Zootechniques", "🧬 Inférence Génétique"])
    
    with t1:
        it = (row["Périmètre Thoracique"] / row["Hauteur Garrot"])
        ic = (row["Hauteur Garrot"] / row["Long. Corps"])
        st.metric("Indice Thoracique", f"{it:.2f}")
        st.metric("Indice de Compacité", f"{ic:.2f}")
        st.plotly_chart(px.radar(r=[it, ic, row["Larg. Poitrine"]/30], theta=['Thorax', 'Compacité', 'Largeur'], line_close=True))

    with t2:
        if row["Poids (kg)"] > 55:
            st.warning("⚠️ Probabilité élevée de mutation Myostatine (MSTN)")
        if row["Cornes"] == "Absentes (Mottes)":
            st.info("🧬 Génotype prédit : Locus P (Polled) Dominant")

# --- PAGE 6 : GESTION & EXPORT (BLOC 6) ---
elif menu == "🗂️ Gestion de la Base":
    st.title("🗂️ Bloc 6 : Gestion & Exportation")
    
    edited_df = st.data_editor(st.session_state.db_data, use_container_width=True, num_rows="dynamic")
    
    if st.button("💾 Sauvegarder les modifications"):
        st.session_state.db_data = edited_df
        st.success("Base mise à jour !")

    st.markdown("---")
    csv = st.session_state.db_data.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Télécharger pour Excel (CSV)", csv, "data_master.csv", "text/csv", use_container_width=True)
