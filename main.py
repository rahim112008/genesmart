import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# --- 1. CONFIGURATION SCIENTIFIQUE ---
st.set_page_config(page_title="GeneSmart Pro | Research Suite", layout="wide", page_icon="🔬")

# Constantes de recherche (Héritabilité moyenne pour les ovins)
H2_POIDS = 0.35 
H2_CONFORMATION = 0.25

# --- 2. DATA ENGINE (Session State) ---
if 'db_data' not in st.session_state:
    st.session_state.db_data = pd.DataFrame({
        "ID_ANIMAL": ["DZ-001", "DZ-002"],
        "AGE_DENTS": ["2 dents", "4 dents"],
        "POIDS_KG": [48.5, 55.0],
        "H_GARROT": [74.0, 76.0],
        "P_THORACIQUE": [91.0, 95.0],
        "L_CORPS": [81.0, 83.0],
        "GENOTYPE_PRED": ["Normal", "Porteur MSTN"]
    })

# --- 3. ARCHITECTURE DE NAVIGATION ---
st.sidebar.title("🔬 Research Portal")
menu = st.sidebar.radio("Modules d'analyse", [
    "🧬 Génomique Populationnelle", 
    "🆔 Phénomique (Saisie)", 
    "🔍 Inférence & EBV (Bloc 5)",
    "🗂️ LIMS & Export (Bloc 6)"
])

# --- PAGE 1 : GÉNOMIQUE POPULATIONNELLE ---
if menu == "🧬 Génomique Populationnelle":
    st.title("🧬 Structure Génétique de la Population")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        # Simulation d'une ACP (PCA) bio-informatique
        pca_data = pd.DataFrame({
            'PC1': np.random.normal(0, 1, 50),
            'PC2': np.random.normal(0, 1, 50),
            'Cluster': np.random.choice(['Ouled Djellal', 'Rembi', 'Hamra'], 50)
        })
        st.plotly_chart(px.scatter(pca_data, x='PC1', y='PC2', color='Cluster', 
                                  title="Analyse en Composantes Principales (Distance Génétique)"), use_container_width=True)
    with col2:
        st.subheader("📊 Paramètres de Population")
        st.metric("Taux de Consanguinité (F)", "0.024", "Stable")
        st.metric("Hétérozygotie Attendue (He)", "0.68")

# --- PAGE 2 : PHÉNOMIQUE (SAISIE) ---
elif menu == "🆔 Phénomique (Saisie)":
    st.title("🆔 Caractérisation Phénomique")
    with st.form("research_form"):
        c1, c2, c3 = st.columns(3)
        id_an = c1.text_input("ID Individu", "DZ-")
        age = c2.selectbox("Stade (Dentition)", ["Dents de lait", "2 dents", "4 dents", "6 dents", "8 dents"])
        poids = c3.number_input("Poids vif (kg)", 10.0, 150.0, 50.0)
        
        st.markdown("---")
        # Mesures pour les indices zootechniques
        cc1, cc2, cc3 = st.columns(3)
        h_gar = cc1.number_input("Hauteur Garrot (cm)", 30.0, 110.0, 75.0)
        p_tho = cc2.number_input("Périmètre Thoracique (cm)", 40.0, 140.0, 92.0)
        l_cor = cc3.number_input("Longueur Corps (cm)", 30.0, 130.0, 82.0)
        
        if st.form_submit_button("🧬 Séquencer les données phénotypiques"):
            # Calcul de prédiction simple (Ex: Myostatine si poids > 60kg à 2 dents)
            geno = "Porteur MSTN" if poids > 58 and age == "2 dents" else "Standard"
            
            new_entry = {
                "ID_ANIMAL": id_an, "AGE_DENTS": age, "POIDS_KG": poids,
                "H_GARROT": h_gar, "P_THORACIQUE": p_tho, "L_CORPS": l_cor,
                "GENOTYPE_PRED": geno
            }
            st.session_state.db_data = pd.concat([st.session_state.db_data, pd.DataFrame([new_entry])], ignore_index=True)
            st.success("Données intégrées au pipeline d'analyse.")

# --- PAGE 5 : INFERENCE & EBV (BLOC 5) ---
elif menu == "🔍 Inférence & EBV (Bloc 5)":
    st.title("🔍 Inférence Génomique & Valeur Génétique")
    id_sel = st.selectbox("Sélectionner un individu pour analyse profonde", st.session_state.db_data["ID_ANIMAL"])
    row = st.session_state.db_data[st.session_state.db_data["ID_ANIMAL"] == id_sel].iloc[0]
    
    # CALCUL EBV (Estimated Breeding Value)
    # Formule : EBV = h2 * (Phénotype_Individu - Moyenne_Population)
    moyenne_pop = st.session_state.db_data["POIDS_KG"].mean()
    ebv = H2_POIDS * (row["POIDS_KG"] - moyenne_pop)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("EBV Poids (kg)", f"{ebv:+.2f}")
    c2.metric("Indice de Compacité", f"{(row['H_GARROT']/row['L_CORPS']):.2f}")
    c3.info(f"Probabilité Génotype : **{row['GENOTYPE_PRED']}**")

    # Graphique Radar : Comparaison Individu vs Moyenne
    categories = ['Poids', 'Garrot', 'Thorax', 'Corps']
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[row["POIDS_KG"]/moyenne_pop, row["H_GARROT"]/75, row["P_THORACIQUE"]/92, row["L_CORPS"]/80],
        theta=categories, fill='toself', name=f'Individu {id_sel}'
    ))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1.5])), title="Bio-Profil Morphologique")
    st.plotly_chart(fig)

# --- PAGE 6 : GESTION & EXPORT (BLOC 6) ---
elif menu == "🗂️ LIMS & Export (Bloc 6)":
    st.title("🗂️ Laboratory Information Management System (LIMS)")
    st.write("Validation et exportation des métadonnées de recherche.")
    
    edited = st.data_editor(st.session_state.db_data, use_container_width=True)
    if st.button("🔄 Synchroniser la base"):
        st.session_state.db_data = edited
        st.rerun()
    
    st.markdown("---")
    csv = st.session_state.db_data.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Dataset (Research Format)", csv, "genomic_dataset.csv", "text/csv")
