import streamlit as st
import httpx
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.stats import chi2_contingency
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from sklearn.decomposition import PCA
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="GeneSmart Pro - Master Edition", layout="wide")

# --- CONFIGURATION SUPABASE (TES IDENTIFIANTS) ---
SUPABASE_URL = "https://hvqwthiztriskqhfmymg.supabase.co" 
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh2cXd0aGl6dHJpc2txaGZteW1nIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg5Mzc5NTMsImV4cCI6MjA4NDUxMzk1M30.POMBcfaCH78_BA8lEnsokLj_4tNKAjjIxQK6ss1QlqE"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# --- BARRE LATÉRALE ---
st.sidebar.title("🧬 GeneSmartFerme")
st.sidebar.info("Connecté à Supabase")
menu = ["Accueil", "Saisie FAO & Repro", "Analyses Bio-Statistiques", "Bilan Génétique Pro"]
choix = st.sidebar.selectbox("Navigation", menu)

# --- 1. ACCUEIL ---
if choix == "Accueil":
    st.header("🔬 Serveur GeneSmartFerme Actif")
    st.success("L'application mobile est connectée au moteur de calcul bioinformatique.")
    
    if st.button("Tester la connexion Base de Données"):
        url = f"{SUPABASE_URL}/rest/v1/descripteurs_upov?select=*"
        try:
            res = httpx.get(url, headers=HEADERS)
            st.json(res.json()[:3]) # Affiche les 3 premiers résultats
        except:
            st.error("Erreur de connexion Supabase")

# --- 2. SAISIE FAO & REPRODUCTION ---
elif choix == "Saisie FAO & Repro":
    st.header("📝 Saisie FAO & Suivi Reproduction")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Enregistrement Mesure")
        animal_id = st.number_input("ID Animal", value=1)
        poids = st.number_input("Poids (kg)", value=60.0)
        hauteur = st.number_input("Hauteur au garrot (cm)", value=75.0)
        if st.button("Enregistrer sur Supabase"):
            payload = {"animal_id": animal_id, "poids_kg": poids, "hauteur_au_garrot": hauteur, "date_mesure": datetime.now().strftime("%Y-%m-%d")}
            res = httpx.post(f"{SUPABASE_URL}/rest/v1/mesures_fao", headers=HEADERS, json=payload)
            st.success("Données envoyées !")

    with col2:
        st.subheader("Suivi de Reproduction")
        date_p = st.date_input("Date de pose de l'éponge")
        if date_p:
            date_mise_bas = date_p + timedelta(days=14 + 2 + 150)
            jours_restants = (date_mise_bas - datetime.now().date()).days
            st.metric("Mise bas estimée", date_mise_bas.strftime("%d %B %Y"))
            if 0 <= jours_restants <= 7:
                st.warning("🚨 ALERTE PROCHE")

# --- 3. ANALYSES BIO-STATISTIQUES ---
elif choix == "Analyses Bio-Statistiques":
    st.header("📊 Analyses Bio-Statistiques")
    
    tab1, tab2, tab3 = st.tabs(["ANOVA", "ACP", "Khi-2"])
    
    with tab1:
        st.subheader("Analyse de Variance (ANOVA)")
        data = {'region': ['Steppe', 'Steppe', 'Nord', 'Nord', 'Sud', 'Sud'], 'poids': [65, 68, 60, 62, 70, 72]}
        df = pd.DataFrame(data)
        model = ols('poids ~ region', data=df).fit()
        p_val = anova_lm(model)['PR(>F)'][0]
        st.write(df)
        st.metric("P-Value", f"{p_val:.4f}")
        st.write("Résultat :", "**Significatif**" if p_val < 0.05 else "**Non significatif**")

    with tab2:
        st.subheader("Analyse en Composantes Principales (ACP)")
        X = [[65, 80, 25], [60, 75, 22], [70, 85, 28], [62, 78, 24]]
        pca = PCA(n_components=2)
        pca.fit(X)
        var_exp = [v*100 for v in pca.explained_variance_ratio_]
        st.bar_chart(var_exp)
        st.write(f"Variance expliquée : Axe 1 ({var_exp[0]:.2f}%), Axe 2 ({var_exp[1]:.2f}%)")

    with tab3:
        st.subheader("Test du Khi-2 & Contingence")
        obs = np.array([[40, 10], [10, 40]])
        stat, p, dof, expected = chi2_contingency(obs)
        coeff_c = np.sqrt(stat / (stat + np.sum(obs)))
        st.write(f"Coefficient de contingence C : **{coeff_c:.3f}**")
        st.write(f"Significativité : **{('Hautement Significatif' if p < 0.01 else 'Significatif')}** (p={p:.6f})")

# --- 4. BILAN GÉNÉTIQUE PRO ---
elif choix == "Bilan Génétique Pro":
    st.header("🧬 Bilan Génétique de la Population")
    
    # Simulation selon ta logique Master
    nm, nf = 20, 100
    ne = (4 * nm * nf) / (nm + nf)
    p = 0.6
    hw_hetero = 2 * p * (1-p)
    
    col_a, col_b = st.columns(2)
    col_a.metric("Taille Efficace (Ne)", f"{ne:.2f}")
    col_b.metric("Diversité (Hardy-Weinberg)", f"{hw_hetero*100:.1f}%")
    
    # Graphique Radar / Radar Chart pour le bilan
    categories = ["Taille Efficace", "Diversité (HW)", "Santé Troupeau", "Conformité Ouled Djellal"]
    values = [float(min(ne, 100)), float(hw_hetero * 100), 82.0, 91.0]
    
    fig = go.Figure(data=go.Scatterpolar(r=values, theta=categories, fill='toself', line_color='#2ECC71'))
    st.plotly_chart(fig)
