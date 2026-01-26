import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import time

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="GeneSmart Expert v3.0", layout="wide", page_icon="🧬")

# --- 2. INITIALISATION (Noms de colonnes simplifiés pour éviter les erreurs) ---
if 'db_data' not in st.session_state:
    st.session_state.db_data = pd.DataFrame(columns=["ID", "Regne", "Stade", "Mesure_1", "Mesure_2", "Mesure_3", "Obs_1", "Obs_2", "Date"])

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
    st.info("Les analyses globales s'afficheront ici après la saisie de plusieurs individus.")

# --- PAGE 2 : IDENTIFICATION DYNAMIQUE ---
elif menu == "🆔 Identification Dynamique":
    st.title(f"🆔 Caractérisation : {regne_choice}")
    
    # Définition automatique des noms des champs selon le règne
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
        
        st.subheader("🎨 Caractères Qualitatifs")
        obs1 = st.text_input("Couleur / Variété", "Blanc" if "Animal" in regne_choice else "Blé dur")
        obs2 = st.text_input("Cornes / Résistance", "Spiralées" if "Animal" in regne_choice else "Forte")
        
        if st.form_submit_button("💾 Enregistrer dans le LIMS"):
            new_row = {
                "ID": id_val, "Regne": regne_choice, "Stade": st_val,
                "Mesure_1": m1, "Mesure_2": m2, "Mesure_3": m3,
                "Obs_1": obs1, "Obs_2": obs2, "Date": datetime.now().strftime("%Y-%m-%d")
            }
            st.session_state.db_data = pd.concat([st.session_state.db_data, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"Données de {id_val} enregistrées !")
            st.balloons()

# --- PAGE 3 : SUIVI & REPRODUCTION ---
elif menu == "💉 Suivi & Reproduction":
    # Le titre change selon le domaine choisi
    titre_cycle = "💉 Gestion du Cycle (Reproduction)" if "Animal" in regne_choice else "🌱 Gestion du Cycle (Croissance)"
    st.title(titre_cycle)
    
    # Texte d'instruction dynamique
    label_date = "Date de Pose Éponge (Brebis)" if "Animal" in regne_choice else "Date de Semis (Plante)"
    date_ref = st.date_input(label_date, datetime.now())
    
    # CALCUL DYNAMIQUE : 150 jours pour l'animal, 120 pour la plante
    jours_cycle = 150 if "Animal" in regne_choice else 120
    date_echeance = date_ref + timedelta(days=jours_cycle)
    
    # Affichage du résultat avec un libellé adapté
    label_echeance = "🐣 Date de Mise bas prévue" if "Animal" in regne_choice else "🚜 Date de Récolte prévue"
    
    st.warning(f"{label_echeance} : {date_echeance.strftime('%d/%m/%Y')}")
    
    # Indicateur visuel du temps restant
    jours_restants = (date_echeance - datetime.now().date()).days
    if jours_restants > 0:
        st.info(f"⏳ Temps restant estimé : **{jours_restants} jours**")

# --- PAGE 4 : RECHERCHE & EXPERTISE (CORRIGÉE) ---
elif menu == "🔍 Recherche & Expertise":
    st.title("🔬 Recherche & Analyse de Profil")
    if st.session_state.db_data.empty:
        st.warning("Aucune donnée disponible. Allez dans 'Identification' d'abord.")
    else:
        ids = st.session_state.db_data["ID"].tolist()
        id_sel = st.selectbox("Sélectionner l'ID", ids)
        res = st.session_state.db_data[st.session_state.db_data["ID"] == id_sel].iloc[0]
        
        st.write("📊 **Valeurs enregistrées :**")
        st.dataframe(pd.DataFrame(res).T)
        
        # RADAR CHART SÉCURISÉ
        st.subheader("🧬 Profil Morphométrique")
        # On définit les étiquettes dynamiquement pour le graphique aussi !
        labs = ["Poids/Rend.", "Hauteur", "Thorax/Grains"]
        vals = [res["Mesure_1"], res["Mesure_2"], res["Mesure_3"]]
        
        fig = go.Figure(data=go.Scatterpolar(r=vals, theta=labs, fill='toself'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, max(vals)+10])))
        st.plotly_chart(fig, use_container_width=True)

# --- PAGE 5 : GESTION ---
elif menu == "🗂️ Gestion de la Base":
    st.title("🗂️ Système LIMS")
    edited = st.data_editor(st.session_state.db_data, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Synchroniser"):
        st.session_state.db_data = edited
        st.success("Base synchronisée !")
