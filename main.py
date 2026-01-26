import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="GeneSmart Expert v3.0", layout="wide", page_icon="🧬")

# --- 2. INITIALISATION ---
# Utilisation de noms de colonnes universels pour éviter les conflits entre espèces
if 'db_data' not in st.session_state:
    st.session_state.db_data = pd.DataFrame(columns=[
        "ID", "Regne", "Stade", "Mesure_1", "Mesure_2", "Mesure_3", "Obs_1", "Obs_2", "Date"
    ])

# --- 3. BARRE LATÉRALE ---
st.sidebar.title("🧬 GeneSmart Pro")
regne_choice = st.sidebar.selectbox("🔬 Domaine de Recherche", ["Élevage (Animal)", "Agronomie (Végétal)"])
st.sidebar.markdown("---")
menu = st.sidebar.radio("Expertise & Analyse", [
    "📊 Tableau de Bord", 
    "🆔 Identification Dynamique", 
    "💉 Suivi & Reproduction", 
    "🔍 Recherche & Expertise",
    "🗂️ Gestion de la Base"
])

# --- PAGE 1 : TABLEAU DE BORD ---
if menu == "📊 Tableau de Bord":
    st.title(f"📊 Analyses : {regne_choice}")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Échantillons Totaux", len(st.session_state.db_data))
    with c2:
        st.metric("Dernière Mise à jour", datetime.now().strftime("%H:%M"))
    
    if not st.session_state.db_data.empty:
        st.write("---")
        st.subheader("🧬 Répartition des données")
        fig_pie = px.pie(st.session_state.db_data, names='Regne', hole=0.4, title="Proportion Animal vs Végétal")
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("La base est vide. Les statistiques apparaîtront après la première saisie.")

# --- PAGE 2 : IDENTIFICATION DYNAMIQUE (Labels Adaptatifs) ---
elif menu == "🆔 Identification Dynamique":
    st.title(f"🆔 Caractérisation : {regne_choice}")
    
    # Définition dynamique des labels selon le choix dans la sidebar
    label1 = "Poids (kg)" if "Animal" in regne_choice else "Rendement (q/ha)"
    label2 = "Hauteur Garrot (cm)" if "Animal" in regne_choice else "Hauteur Tige (cm)"
    label3 = "Périmètre Thorax (cm)" if "Animal" in regne_choice else "Nombre Grains"
    
    with st.form("form_global"):
        col_id, col_st = st.columns(2)
        id_val = col_id.text_input("Identifiant Unique", "DZ-")
        st_val = col_st.text_input("Stade (Âge/BBCH)", "2 dents" if "Animal" in regne_choice else "Floraison")
        
        st.subheader("📏 Mesures Quantitatives")
        c1, c2, c3 = st.columns(3)
        m1 = c1.number_input(label1, value=0.0)
        m2 = c2.number_input(label2, value=0.0)
        m3 = c3.number_input(label3, value=0.0)
        
        st.subheader("🎨 Caractères Morphologiques")
        obs1_label = "Couleur Robe" if "Animal" in regne_choice else "Variété/Espèce"
        obs2_label = "Cornes/Scrotum" if "Animal" in regne_choice else "Résistance Stress"
        
        obs1 = st.text_input(obs1_label, "Blanc" if "Animal" in regne_choice else "Blé Dur")
        obs2 = st.text_input(obs2_label, "Spiralées" if "Animal" in regne_choice else "Excellente")
        
        if st.form_submit_button("💾 Enregistrer dans le LIMS", use_container_width=True):
            new_row = {
                "ID": id_val, "Regne": regne_choice, "Stade": st_val,
                "Mesure_1": m1, "Mesure_2": m2, "Mesure_3": m3,
                "Obs_1": obs1, "Obs_2": obs2, "Date": datetime.now().strftime("%Y-%m-%d")
            }
            st.session_state.db_data = pd.concat([st.session_state.db_data, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"Données de {id_val} enregistrées !")
            st.balloons()

# --- PAGE 3 : SUIVI & REPRODUCTION (Calculateur Dynamique) ---
elif menu == "💉 Suivi & Reproduction":
    titre_cycle = "💉 Gestion de la Reproduction" if "Animal" in regne_choice else "🌱 Suivi de Croissance"
    st.title(titre_cycle)
    
    label_date = "Date Pose Éponge" if "Animal" in regne_choice else "Date de Semis"
    date_ref = st.date_input(label_date, datetime.now())
    
    # 150 jours pour ovin, 120 jours pour céréales (adaptable)
    jours_cycle = 150 if "Animal" in regne_choice else 120
    date_echeance = date_ref + timedelta(days=jours_cycle)
    
    label_res = "🐣 Mise bas prévue" if "Animal" in regne_choice else "🚜 Récolte estimée"
    st.warning(f"**{label_res} :** {date_echeance.strftime('%d/%m/%Y')}")

# --- PAGE 4 : RECHERCHE & EXPERTISE (Radar Sécurisé) ---
elif menu == "🔍 Recherche & Expertise":
    st.title("🔬 Recherche & Profil Bio-informatique")
    if st.session_state.db_data.empty:
        st.warning("Aucune donnée enregistrée.")
    else:
        ids = st.session_state.db_data["ID"].tolist()
        id_sel = st.selectbox("🎯 Sélectionner un échantillon", ids)
        res = st.session_state.db_data[st.session_state.db_data["ID"] == id_sel].iloc[0]
        
        st.write("📌 **Fiche de l'échantillon :**")
        st.dataframe(pd.DataFrame(res).T)
        
        # Graphique Radar avec labels dynamiques
        st.subheader("🧬 Radar Morphométrique")
        # On redéfinit les noms pour le graphique selon le règne de l'individu choisi
        if res["Regne"] == "Élevage (Animal)":
            labs = ["Poids", "Garrot", "Thorax"]
        else:
            labs = ["Rendement", "Hauteur", "Grains"]
            
        vals = [res["Mesure_1"], res["Mesure_2"], res["Mesure_3"]]
        
        if any(v > 0 for v in vals): # On n'affiche le radar que si on a des données
            fig = go.Figure(data=go.Scatterpolar(r=vals, theta=labs, fill='toself'))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True)))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Veuillez saisir des mesures chiffrées pour générer le radar.")

# --- PAGE 5 : GESTION DE LA BASE ---
elif menu == "🗂️ Gestion de la Base":
    st.title("🗂️ Système de Gestion (LIMS)")
    edited = st.data_editor(st.session_state.db_data, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Synchroniser les modifications"):
        st.session_state.db_data = edited
        st.success("Base de données mise à jour !")
