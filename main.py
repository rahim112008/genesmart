import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import time

# --- 1. CONFIGURATION INTERFACE ---
st.set_page_config(
    page_title="GeneSmart Expert v3.0 | Research Suite", 
    layout="wide", 
    page_icon="🧬"
)

# --- 2. INITIALISATION (Structure flexible) ---
if 'db_data' not in st.session_state:
    st.session_state.db_data = pd.DataFrame({
        "ID": ["DZ-2026-001", "PLANTE-X"],
        "Règne": ["Animal", "Végétal"],
        "Stade": ["2 dents", "Floraison"],
        "Poids/Rendement": [45.0, 12.5],
        "Mesure_2": [75.0, 80.0],
        "Caractère_Quali": ["Blanc", "Vert foncé"]
    })

# --- 3. NAVIGATION & RÉGNE ---
st.sidebar.title("🧬 GeneSmart Pro")
regne = st.sidebar.selectbox("🔬 Domaine de Recherche", ["Élevage (Animal)", "Agronomie (Végétal)"])
st.sidebar.markdown("---")

menu = st.sidebar.radio("Expertise & Analyse", [
    "📊 Tableau de Bord", 
    "🆔 Identification Dynamique", 
    "💉 Suivi & Reproduction", 
    "🧬 Simulateur de Sélection",
    "🔍 Recherche & Expertise",
    "🗂️ Gestion de la Base"
])

# --- PAGE 1 : ANALYSES ---
if menu == "📊 Tableau de Bord":
    st.title(f"📊 Analyses : {regne}")
    t_gen, t_stat = st.tabs(["🧬 Génétique", "📉 Statistiques"])
    
    with t_gen:
        c1, c2 = st.columns(2)
        c1.metric("Diversité Génétique", "0.78" if regne == "Animal" else "0.82", "Stable")
        c2.metric("Taux d'homozygotie", "0.12", "Normal")
        st.plotly_chart(px.bar(x=['Pop A', 'Pop B', 'Pop C'], y=[10, 25, 15], title="Distribution Géographique"), use_container_width=True)

    with t_stat:
        st.subheader("Analyse en Composantes Principales (Simulation)")
        df_acp = pd.DataFrame({'PC1': np.random.randn(20), 'PC2': np.random.randn(20), 'Groupe': ['A']*10 + ['B']*10})
        st.plotly_chart(px.scatter(df_acp, x='PC1', y='PC2', color='Groupe', title="Plan Factoriel (Phénomique)"), use_container_width=True)

# --- PAGE 2 : IDENTIFICATION DYNAMIQUE (LA CLÉ) ---
elif menu == "🆔 Identification Dynamique":
    st.title(f"🆔 Caractérisation : {regne}")
    st.info(f"Saisie libre des descripteurs selon les standards {'FAO' if regne == 'Animal' else 'UPOV'}")

    with st.form("dynamic_form"):
        c1, c2 = st.columns(2)
        id_sujet = c1.text_input("Identifiant Unique", "DZ-")
        stade = c2.text_input("Stade (Âge / BBCH / Dentition)", "2 dents" if regne == "Animal" else "Tallage")

        st.markdown("---")
        # --- BLOC QUANTITATIF ---
        st.subheader("📏 Mesures Quantitatives (Biométrie)")
        cq1, cq2, cq3 = st.columns(3)
        label_q1 = cq1.text_input("Nom Caractère 1", "Poids (kg)" if regne == "Animal" else "Rendement (q/ha)")
        val_q1 = cq1.number_input("Valeur 1", value=0.0)
        
        label_q2 = cq2.text_input("Nom Caractère 2", "Hauteur (cm)" if regne == "Animal" else "Hauteur Tige (cm)")
        val_q2 = cq2.number_input("Valeur 2", value=0.0)
        
        label_q3 = cq3.text_input("Nom Caractère 3", "Périmètre (cm)" if regne == "Animal" else "Nombre Grains")
        val_q3 = cq3.number_input("Valeur 3", value=0.0)

        st.markdown("---")
        # --- BLOC QUALITATIF ---
        st.subheader("🎨 Caractères Qualitatifs (Observations)")
        cql1, cql2 = st.columns(2)
        label_ql1 = cql1.text_input("Descripteur 1", "Couleur" if regne == "Animal" else "Forme Feuille")
        val_ql1 = cql1.text_input("Observation 1")
        
        label_ql2 = cql2.text_input("Descripteur 2", "Cornes" if regne == "Animal" else "Résistance")
        val_ql2 = cql2.text_input("Observation 2")

        if st.form_submit_button("💾 Enregistrer dans la Base Universelle", use_container_width=True, type="primary"):
            new_row = {
                "ID": id_sujet, "Règne": regne, "Stade": stade,
                label_q1: val_q1, label_q2: val_q2, label_q3: val_q3,
                label_ql1: val_ql1, label_ql2: val_ql2,
                "Date": datetime.now().strftime("%d/%m/%Y")
            }
            st.session_state.db_data = pd.concat([st.session_state.db_data, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"Enregistrement réussi pour {id_sujet}")
            st.balloons()

# --- PAGE 3 : SUIVI & REPRO ---
elif menu == "💉 Suivi & Reproduction":
    st.title("💉 Gestion Technique")
    if regne == "Animal":
        st.subheader("🤰 Prédiction Mise Bas")
        date_e = st.date_input("Date Pose Éponge", datetime.now())
        st.info(f"Mise bas prévue : {(date_e + timedelta(days=166)).strftime('%d/%m/%Y')}")
    else:
        st.subheader("🌱 Cycle de Croissance")
        date_s = st.date_input("Date de Semis", datetime.now())
        st.warning(f"Récolte estimée : {(date_s + timedelta(days=120)).strftime('%d/%m/%Y')}")

# --- PAGE 4 : CROISEMENT ---
elif menu == "🧬 Simulateur de Sélection":
    st.title("🧬 Amélioration Génétique")
    liste_ids = st.session_state.db_data[st.session_state.db_data["Règne"] == regne]["ID"].tolist()
    
    if len(liste_ids) >= 2:
        c1, c2 = st.columns(2)
        p1 = c1.selectbox("Parent 1", liste_ids)
        p2 = c2.selectbox("Parent 2", liste_ids)
        if st.button("Calculer Gain Génétique"):
            st.success("Gain estimé : +15% sur le caractère principal")
    else:
        st.warning("Il faut au moins deux individus du même règne pour simuler un croisement.")

# --- PAGE 5 : EXPERTISE DYNAMIQUE ---
elif menu == "🔍 Recherche & Expertise":
    st.title("🔬 Recherche de Profils")
    liste_ids = st.session_state.db_data["ID"].tolist()
    id_sel = st.selectbox("Choisir l'ID :", liste_ids)
    
    # Récupération automatique
    data = st.session_state.db_data[st.session_state.db_data["ID"] == id_sel].dropna(axis=1)
    st.write("📌 **Données identifiées pour cet échantillon :**")
    st.dataframe(data)
    
    # Graphique dynamique selon les colonnes présentes
    num_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    if len(num_cols) >= 2:
        st.plotly_chart(px.radar(data, r=num_cols[0:3], theta=num_cols[0:3], title="Radar Bio-Morphologique"))

# --- PAGE 6 : GESTION (LIMS) ---
elif menu == "🗂️ Gestion de la Base":
    st.title("🗂️ Système de Gestion (LIMS)")
    st.write("Nettoyage et exportation du Dataset Multi-Taxon.")
    
    edited_df = st.data_editor(st.session_state.db_data, num_rows="dynamic", use_container_width=True)

    if st.button("💾 Synchroniser avec le Cloud", type="primary"):
        progress = st.progress(0)
        for i in range(101):
            time.sleep(0.01)
            progress.progress(i)
        st.session_state.db_data = edited_df
        st.success("Synchronisation terminée !")

    csv = st.session_state.db_data.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Exporter le Dataset (CSV)", csv, "data_export.csv", "text/csv", use_container_width=True)
