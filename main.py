import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.stats import chi2_contingency
from sklearn.decomposition import PCA
import plotly.express as px

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="GeneSmart Pro", page_icon="🧬", layout="wide")

# --- 2. CONNEXION ET IDENTIFIANTS (Inchangés) ---
# Ton URL de base Supabase pour la base de données
SUPABASE_URL = "https://hvqwthiztriskqhfmymg.supabase.co"

# --- 3. INTERFACE UTILISATEUR (STREAMLIT) ---
st.title("🧬 GeneSmart Pro - Algérie")
st.sidebar.header("Menu de Navigation")
page = st.sidebar.selectbox("Choisir une analyse", 
    ["Tableau de Bord", "Calculs Génétiques", "Analyses Statistiques", "Suivi Reproduction"])

# --- SECTION A : TABLEAU DE BORD ---
if page == "Tableau de Bord":
    st.header("📊 État du Cheptel")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Individus", "120")
    col2.metric("Béliers (Mâles)", "20")
    col3.metric("Brebis (Femelles)", "100")
    
    # Graphique de répartition
    df_data = pd.DataFrame({
        "Catégorie": ["Béliers", "Brebis", "Agneaux"],
        "Nombre": [20, 70, 30]
    })
    fig = px.pie(df_data, values='Nombre', names='Catégorie', title="Répartition du Troupeau")
    st.plotly_chart(fig)

# --- SECTION B : CALCULS GÉNÉTIQUES (Formule de Wright) ---
elif page == "Calculs Génétiques":
    st.header("🧬 Paramètres de Population")
    st.subheader("Calcul de la Taille Efficace (Ne)")
    
    nm = st.number_input("Nombre de mâles reproducteurs (Nm)", value=20)
    nf = st.number_input("Nombre de femelles reproductrices (Nf)", value=100)
    
    if st.button("Calculer Ne"):
        # Formule de Wright : Ne = (4 * Nm * Nf) / (Nm + Nf)
        ne = (4 * nm * nf) / (nm + nf)
        st.success(f"La taille efficace du troupeau (Ne) est de : {ne:.2f}")
        
        if ne < 50:
            st.warning("⚠️ Risque de consanguinité élevé (Seuil de Wright).")
        else:
            st.info("✅ Diversité génétique stable.")

# --- SECTION C : ANALYSES STATISTIQUES (ACP) ---
elif page == "Analyses Statistiques":
    st.header("🔬 Bio-Statistiques Avancées")
    st.write("Analyse en Composantes Principales (ACP) sur les mesures morphologiques")
    
    # Simulation de données pour la démonstration
    data_acp = np.array([[65, 80, 25], [60, 75, 22], [70, 85, 28], [62, 78, 24]])
    pca = PCA(n_components=2)
    pca.fit(data_acp)
    
    st.write("Variance expliquée par les axes :")
    st.bar_chart(pca.explained_variance_ratio_)

# --- SECTION D : REPRODUCTION ---
elif page == "Suivi Reproduction":
    st.header("📅 Gestion de la Reproduction")
    date_pose = st.date_input("Date de pose de l'éponge", datetime.now())
    
    # Calcul des étapes clés
    date_retrait = date_pose + timedelta(days=14)
    date_lutte = date_retrait + timedelta(days=2)
    date_mise_bas = date_lutte + timedelta(days=150)
    
    st.info(f"📅 Retrait éponge : {date_retrait.strftime('%d/%m/%Y')}")
    st.info(f"🐏 Date de lutte : {date_lutte.strftime('%d/%m/%Y')}")
    st.success(f"🐑 Mise-bas estimée : {date_mise_bas.strftime('%d/%m/%Y')}")
