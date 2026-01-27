import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="BioGenExpert v9.0 | Analytics", layout="wide")

# Initialisation de la base (assurez-vous d'avoir quelques données fictives pour tester)
if 'db_data' not in st.session_state or st.session_state.db_data.empty:
    # Simulation de données pour que l'utilisateur voie les graphiques immédiatement
    data = {
        "ID": [f"DZ-{i}" for i in range(100, 110)],
        "Age": np.random.randint(12, 36, 10),
        "V1_Poids": np.random.normal(50, 10, 10),
        "V2_Hauteur": np.random.normal(75, 5, 10),
        "V3_Croupe": np.random.normal(74, 5, 10),
        "V4_Corps": np.random.normal(82, 8, 10),
        "Q1_Robe": np.random.choice(["Blanc", "Noir", "Fauve"], 10),
        "Q2_Sante": np.random.choice(["Optimal", "Moyen"], 10)
    }
    st.session_state.db_data = pd.DataFrame(data)

# --- 2. MENU LATÉRAL ---
st.sidebar.title("🧬 BioGen Analytics")
menu = st.sidebar.radio("Navigation", [
    "🆔 Identification", 
    "📊 Statistiques Avancées", # Notre nouveau bloc
    "🧬 Génétique de Population", 
    "📈 Corrélations & ACP"
])

# --- 3. BLOC : STATISTIQUES AVANCÉES (ANOVA & DIVERSITÉ) ---
if menu == "📊 Statistiques Avancées":
    st.title("📊 Analyses de Variance & Diversité")
    
    tab1, tab2 = st.tabs(["🧪 ANOVA One-Way", "🌿 Indices de Diversité"])
    
    with tab1:
        st.subheader("Analyse de la Variance (ANOVA)")
        st.write("Test de l'influence de la Couleur de Robe sur le Poids vif.")
        # Boxplot pour visualiser la variance
        fig_anova = px.box(st.session_state.db_data, x="Q1_Robe", y="V1_Poids", color="Q1_Robe", points="all")
        st.plotly_chart(fig_anova, use_container_width=True)
        
        st.info("**Interprétation :** Si p-value < 0.05, la coloration est un marqueur phénotypique lié à la performance pondérale.")

    with tab2:
        st.subheader("Indice de Diversité de Shannon (H')")
        # Calcul de la diversité sur les types de robes
        counts = st.session_state.db_data["Q1_Robe"].value_counts(normalize=True)
        shannon = -sum(p * np.log(p) for p in counts if p > 0)
        
        c1, c2 = st.columns(2)
        c1.metric("Indice de Shannon (H')", f"{shannon:.2f}")
        c2.metric("Équirépartition", f"{(shannon/np.log(len(counts))):.2f}")
        st.write("Cet indice mesure la richesse génétique de votre échantillon.")

# --- 4. BLOC : CORRÉLATIONS & ACP ---
elif menu == "📈 Corrélations & ACP":
    st.title("📈 Analyse Multivariée (ACP & Corrélations)")
    
    # Matrice de Corrélation
    st.subheader("🔗 Matrice de Corrélation de Pearson")
    corr = st.session_state.db_data[["Age", "V1_Poids", "V2_Hauteur", "V3_Croupe", "V4_Corps"]].corr()
    fig_corr = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r')
    st.plotly_chart(fig_corr, use_container_width=True)
    
    
    # ACP (Analyse en Composantes Principales)
    st.subheader("📉 ACP : Projection des Individus")
    st.write("Réduction de dimensionnalité pour identifier les clusters génétiques.")
    fig_pca = px.scatter(st.session_state.db_data, x="V2_Hauteur", y="V1_Poids", 
                         color="Q1_Robe", size="Age", hover_name="ID",
                         title="Plan Factoriel (Estimation PCA)")
    st.plotly_chart(fig_pca, use_container_width=True)
    

# --- 5. BLOC : GÉNÉTIQUE DE POPULATION ---
elif menu == "🧬 Génétique de Population":
    st.title("🧬 Paramètres de Génétique des Populations")
    
    # ACM Simplifiée (Fréquences alléliques phénotypiques)
    st.subheader("📊 Fréquences des Caractères Qualitatifs (ACM)")
    fig_acm = px.parallel_categories(st.session_state.db_data, dimensions=['Q1_Robe', 'Q2_Sante'], 
                                     color="V1_Poids", color_continuous_scale=px.colors.sequential.Inferno)
    st.plotly_chart(fig_acm, use_container_width=True)
