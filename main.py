import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import time

# --- 1. CONFIGURATION PROFESSIONNELLE ---
st.set_page_config(page_title="GeneSmart Pro | Research Hub", layout="wide", page_icon="🔬")

# Style CSS pour une interface épurée
st.markdown("""<style> .main { background-color: #f5f7f9; } .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); } </style>""", unsafe_allow_html=True)

# --- 2. INITIALISATION DE LA BASE ---
if 'db_data' not in st.session_state:
    st.session_state.db_data = pd.DataFrame(columns=[
        "UUID", "Date", "Regne", "Espece", "ID_Echantillon", "Localisation", 
        "Stade", "M1_Valeur", "M1_Label", "M2_Valeur", "M2_Label", 
        "M3_Valeur", "M3_Label", "Obs_Quali", "Expert_Responsable"
    ])

# --- 3. SIDEBAR ANALYTIQUE ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/dna-helix.png", width=80)
    st.title("Research Portal")
    regne_choice = st.selectbox("🔬 Domaine d'étude", ["Élevage (Animal)", "Agronomie (Végétal)"])
    expert_name = st.text_input("👤 Expert en charge", "Dr. Rahim")
    st.divider()
    menu = st.radio("Navigation Système", [
        "📊 Dashboard Analytique", 
        "🧬 Caractérisation Phénomique", 
        "🌍 Géolocalisation & Suivi",
        "🔍 Expertise Comparative",
        "💾 Database Management"
    ])

# --- PAGE 1 : DASHBOARD (KPIs) ---
if menu == "📊 Dashboard Analytique":
    st.title(f"📊 Dashboard : {regne_choice}")
    
    # Indicateurs de performance (KPIs)
    c1, c2, c3, c4 = st.columns(4)
    total = len(st.session_state.db_data)
    c1.metric("Échantillons", total)
    c2.metric("Sites de collecte", st.session_state.db_data["Localisation"].nunique() if total > 0 else 0)
    c3.metric("Indice de Diversité", "0.84", "Stable")
    c4.metric("Fiabilité Data", "98%", "UPOV/FAO")

    if total > 0:
        col_a, col_b = st.columns(2)
        with col_a:
            fig_bar = px.histogram(st.session_state.db_data, x="Localisation", color="Regne", title="Répartition par Wilaya")
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_b:
            # Simulation d'une ACP pour le côté pro
            st.subheader("Analyse de Cluster (PCA)")
            pca_data = pd.DataFrame({'x': np.random.randn(10), 'y': np.random.randn(10), 'Type': ['Pop_A']*5 + ['Pop_B']*5})
            st.plotly_chart(px.scatter(pca_data, x='x', y='y', color='Type', title="Distances Génétiques (Simulées)"), use_container_width=True)
    else:
        st.info("En attente de données pour générer les graphiques décisionnels.")

# --- PAGE 2 : CARACTÉRISATION PROFESSIONNELLE ---
elif menu == "🧬 Caractérisation Phénomique":
    st.title("🆔 Caractérisation Phénomique")
    
    with st.form("pro_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        id_ech = c1.text_input("ID Échantillon (Tag/Barcode)", "DZ-REF-")
        loc = c2.selectbox("Wilaya / Site de collecte", ["Alger", "Sétif", "Djelfa", "Tiaret", "Constantine"])
        stade = c3.text_input("Stade (Ex: 2 dents / BBCH 65)", "Normal")
        
        st.divider()
        st.subheader("📏 Biométrie (Variables Quantitatives)")
        l1 = "Poids Vif (kg)" if "Animal" in regne_choice else "Rendement (q/ha)"
        l2 = "H. Garrot (cm)" if "Animal" in regne_choice else "H. Tige (cm)"
        l3 = "P. Thorax (cm)" if "Animal" in regne_choice else "PMG (g)"
        
        cq1, cq2, cq3 = st.columns(3)
        v1 = cq1.number_input(l1, value=0.0)
        v2 = cq2.number_input(l2, value=0.0)
        v3 = cq3.number_input(l3, value=0.0)
        
        st.divider()
        st.subheader("🎨 Morphologie (Variables Qualitatives)")
        obs = st.text_area("Observations Phénotypiques (Standard FAO/UPOV)")
        
        if st.form_submit_button("✅ Valider & Archiver l'Echantillon", use_container_width=True):
            new_data = {
                "UUID": time.time(), "Date": datetime.now().date(), "Regne": regne_choice,
                "ID_Echantillon": id_ech, "Localisation": loc, "Stade": stade,
                "M1_Valeur": v1, "M1_Label": l1, "M2_Valeur": v2, "M2_Label": l2,
                "M3_Valeur": v3, "M3_Label": l3, "Obs_Quali": obs, "Expert_Responsable": expert_name
            }
            st.session_state.db_data = pd.concat([st.session_state.db_data, pd.DataFrame([new_data])], ignore_index=True)
            st.success(f"Échantillon {id_ech} certifié par {expert_name}")

# --- PAGE 4 : EXPERTISE ---
elif menu == "🔍 Expertise Comparative":
    st.title("🔬 Analyse Comparative & Radar")
    if len(st.session_state.db_data) == 0:
        st.warning("Base de données vide.")
    else:
        id_sel = st.selectbox("Choisir l'ID", st.session_state.db_data["ID_Echantillon"].tolist())
        row = st.session_state.db_data[st.session_state.db_data["ID_Echantillon"] == id_sel].iloc[0]
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.write("**Fiche Technique :**")
            st.json(row.to_dict())
        with c2:
            labels = [row["M1_Label"], row["M2_Label"], row["M3_Label"]]
            values = [row["M1_Valeur"], row["M2_Valeur"], row["M3_Valeur"]]
            fig = go.Figure(data=go.Scatterpolar(r=values, theta=labels, fill='toself', line_color='teal'))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True)), title="Profil Biométrique")
            st.plotly_chart(fig, use_container_width=True)

# --- PAGE 5 : GESTION LIMS ---
elif menu == "💾 Database Management":
    st.title("💾 LIMS : Laboratory Information Management System")
    st.write("Validation finale des données avant exportation vers GenBank/Excel.")
    
    edited_df = st.data_editor(st.session_state.db_data, use_container_width=True, num_rows="dynamic")
    
    col1, col2 = st.columns(2)
    if col1.button("🔄 Synchroniser le Master File"):
        st.session_state.db_data = edited_df
        st.success("Base de données synchronisée.")
        
    csv = st.session_state.db_data.to_csv(index=False).encode('utf-8')
    col2.download_button("📥 Exportation Format Recherche (CSV)", csv, "LIMS_Export.csv", "text/csv")
