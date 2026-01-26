import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import uuid

# --- 1. INITIALISATION DU SYSTÈME ---
if 'db_data' not in st.session_state:
    st.session_state.db_data = pd.DataFrame(columns=[
        "UUID", "Timestamp", "Regne", "ID_Sujet", "Stade_Pheno", 
        "M1_Val", "M2_Val", "M3_Val", "Index_Compacite", 
        "Quali_Robe_Var", "Quali_Sante_Res", "Expert", "Prediction_Genotype", "F_Coeff"
    ])

st.set_page_config(page_title="BioGenExpert Pro", layout="wide", page_icon="🔬")

# --- 2. NAVIGATION EXPERT ---
with st.sidebar:
    st.header("🧬 Pipeline Génomique")
    regne = st.selectbox("Domaine d'Étude", ["Élevage (Animal)", "Agronomie (Végétal)"])
    expert = st.text_input("Investigateur", "Dr. Rahim")
    menu = st.radio("Navigation", [
        "📊 Dashboard & Bio-Statistiques", 
        "🆔 Phénotypage de Précision", 
        "🧬 Génomique & Prédiction",
        "🏥 Gestion Santé & Pathologie", # NOUVEAU
        "🚜 Gestion Agricole/Élevage",   # NOUVEAU
        "📜 Certificat & LIMS"
    ])

# --- 3. BLOC : GESTION SANTÉ & PATHOLOGIE (NOUVEAU) ---
if menu == "🏥 Gestion Santé & Pathologie":
    st.title("🏥 Monitoring de la Résilience")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Carnet de Santé" if "Animal" in regne else "🍃 Diagnostic Phytosanitaire")
        status = st.select_slider("Niveau de vigueur", options=["Critique", "Moyen", "Optimal"], value="Optimal")
        patho = st.multiselect("Signes cliniques détectés", 
                               ["Parasites", "Fièvre", "Lésions"] if "Animal" in regne else ["Rouille", "Oïdium", "Carence Azote"])
        st.info(f"Analyse de résilience : {expert} préconise un suivi renforcé.")

    with col2:
        st.subheader("📊 Prévalence dans la population")
        # Visualisation de la santé globale de la base
        if not st.session_state.db_data.empty:
            fig_health = px.pie(st.session_state.db_data, names='Quali_Sante_Res', hole=0.4)
            st.plotly_chart(fig_health, use_container_width=True)

# --- 4. BLOC : GESTION AGRICOLE & ÉLEVAGE (NOUVEAU) ---
elif menu == "🚜 Gestion Agricole/Élevage":
    st.title("🚜 Optimisation de la Production")
    
    if "Animal" in regne:
        st.subheader("🥩 Gestion de la Valeur Bouchère / Laitière")
        c1, c2, c3 = st.columns(3)
        c1.metric("Gain de Poids Moyen (GMS)", "850g/j", "+5%")
        c2.metric("Indice de Consommation", "3.2", "-0.1")
        c3.metric("Potentiel Laitier", "18L/j", "Stable")
        
    else:
        st.subheader("🌾 Prédiction de Rendement & Intrants")
        c1, c2, c3 = st.columns(3)
        c1.metric("Besoin N-P-K", "120-60-40", "Optimal")
        c2.metric("Stress Hydrique", "Bas", "-12%")
        c3.metric("Rendement Estimé", "45 q/ha", "+3.5")
        

# --- 5. BLOC : DASHBOARD & STATS (ANOVA / ACP) ---
elif menu == "📊 Dashboard & Bio-Statistiques":
    st.title("📊 Analyses Multivariées (ACP & ANOVA)")
    if len(st.session_state.db_data) < 3:
        st.warning("Données insuffisantes pour les calculs de variance.")
    else:
        # ACP simplifiée par projection
        fig_acp = px.scatter(st.session_state.db_data, x="M1_Val", y="M2_Val", 
                             color="Prediction_Genotype", size="Index_Compacite",
                             title="Analyse en Composantes Principales (Distance Génétique)")
        st.plotly_chart(fig_acp, use_container_width=True)
        

# --- 6. BLOC : PHÉNOTYPAGE (REMPLISSAGE LIMS) ---
elif menu == "🆔 Phénotypage de Précision":
    st.title("📝 Saisie Phénotypique Standardisée")
    with st.form("lims_form"):
        c1, c2 = st.columns(2)
        id_s = c1.text_input("ID Individu", "DZ-")
        stade = c2.text_input("Stade Phénologique", "Adulte/Floraison")
        
        m1 = st.number_input("Masse (kg/q)", value=0.0)
        m2 = st.number_input("Dimension (cm/m)", value=1.0)
        m3 = st.number_input("Densité (Thorax/PMG)", value=0.0)
        
        q_sante = st.selectbox("État Sanitaire", ["Optimal", "Stress", "Critique"])
        
        if st.form_submit_button("Sauvegarder l'échantillon"):
            idx = m1/m2
            pred = "Elite" if idx > 0.8 else "Standard"
            new_row = {
                "UUID": str(uuid.uuid4())[:8], "Timestamp": datetime.now().strftime("%Y-%m-%d"),
                "Regne": regne, "ID_Sujet": id_s, "Stade_Pheno": stade, 
                "M1_Val": m1, "M2_Val": m2, "M3_Val": m3, "Index_Compacite": idx,
                "Quali_Robe_Var": "Standard", "Quali_Sante_Res": q_sante, 
                "Expert": expert, "Prediction_Genotype": pred, "F_Coeff": 0.0
            }
            st.session_state.db_data = pd.concat([st.session_state.db_data, pd.DataFrame([new_row])], ignore_index=True)
            st.success("Donnée archivée.")

# --- 7. BLOC : GÉNOMIQUE (RADAR) ---
elif menu == "🧬 Génomique & Prédiction":
    st.title("🔬 Prédiction Génomique")
    if not st.session_state.db_data.empty:
        id_sel = st.selectbox("Sélectionner l'individu", st.session_state.db_data["ID_Sujet"].unique())
        row = st.session_state.db_data[st.session_state.db_data["ID_Sujet"] == id_sel].iloc[0]
        
        # Radar Chart
        fig = go.Figure(data=go.Scatterpolar(
            r=[row['M1_Val'], row['M2_Val'], row['M3_Val']],
            theta=['Masse', 'Structure', 'Densité'], fill='toself'
        ))
        st.plotly_chart(fig)
        

# --- 8. BLOC : CERTIFICAT & LIMS ---
elif menu == "📜 Certificat & LIMS":
    st.title("📜 Documents Officiels")
    st.dataframe(st.session_state.db_data)
    if not st.session_state.db_data.empty:
        st.download_button("📥 Télécharger CSV", st.session_state.db_data.to_csv().encode('utf-8'), "Export_BioGen.csv")
