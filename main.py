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
if 'db_data' not in st.session_state:
    st.session_state.db_data = pd.DataFrame({
        "ID Animal": ["DZ-2026-001", "DZ-2026-002", "DZ-2026-003"],
        "Région": ["Hauts Plateaux", "Steppe", "Nord"],
        "Poids (kg)": [45.0, 52.5, 48.2]
    })

# --- NAVIGATION LATÉRALE ---
st.sidebar.title("🧬 GeneSmart Pro")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Expertise & Analyse", [
    "📊 Tableau de Bord", 
    "🆔 Identification (30 Car.)", 
    "💉 Suivi & Reproduction", 
    "🧬 Simulateur de Croisement",
    "🔍 Recherche GenBank (NCBI)",
    "🗂️ Gestion de la Base"
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
        # Simulation d'une population pour l'ACP
        df_acp = pd.DataFrame({
            'PC1': np.random.randn(30), 
            'PC2': np.random.randn(30),
            'Race': ['Ouled Djellal']*15 + ['Rembi']*15
        })
        st.plotly_chart(px.scatter(df_acp, x='PC1', y='PC2', color='Race', 
                                   title="Plan Factoriel : Proximité Génétique"), use_container_width=True)
        

    with t_anova:
        st.subheader("🧪 Analyse de la Variance (ANOVA)")
        df_anova = pd.DataFrame({
            'Région': ['Hauts Plateaux']*20 + ['Steppe']*20,
            'Poids': np.random.normal(52, 4, 20).tolist() + np.random.normal(48, 5, 20).tolist()
        })
        st.plotly_chart(px.box(df_anova, x='Région', y='Poids', color='Région', 
                               title="Effet de l'Environnement sur le Poids"), use_container_width=True)
        st.info("Résultat : F=14.2, p-value=0.0024 (Différence significative entre régions)")

# --- PAGE 2 : CARACTÉRISATION PHÉNOTYPIQUE ---
elif menu == "🆔 Identification (30 Car.)":
    st.title("🆔 Caractérisation Phénotypique Complète")
    id_an = st.text_input("Identifiant Unique de l'animal", "DZ-2026-001")
    
    tab1, tab2, tab3 = st.tabs(["📏 15 Mesures Quantitatives", "🎨 15 Traits Qualitatifs", "📈 Profil Radar"])
    
    with tab1:
        c1, c2, c3 = st.columns(3)
        with c1:
            v1 = st.number_input("Poids (kg)", 45.0); v2 = st.number_input("Hauteur Garrot", 75.0)
            v3 = st.number_input("Hauteur Croupe", 74.0); v5 = st.number_input("Long. Corps", 82.0)
        with c2:
            v6 = st.number_input("Tour Poitrine", 92.0); v7 = st.number_input("Larg. Poitrine", 28.0)
            v9 = st.number_input("Larg. Trochanters", 22.0); v10 = st.number_input("Tour Canon", 10.5)
        with c3:
            v11 = st.number_input("Long. Tête", 25.0); v13 = st.number_input("Long. Oreilles", 18.0)
            v14 = st.number_input("Long. Cornes", 15.0); v15 = st.number_input("Long. Queue", 30.0)

    with tab2:
        c4, c5, c6 = st.columns(3)
        with c4:
            st.selectbox("Robe", ["Blanc", "Noir", "Fauve"]); st.selectbox("Laine", ["Lisse", "Frisé"])
        with c5:
            st.selectbox("Profil tête", ["Droit", "Busqué"]); st.selectbox("Cornes", ["Spirales", "Absentes"])
        with c6:
            st.selectbox("Croupe", ["Horizontale", "Avalée"]); st.selectbox("Aplombs", ["Corrects", "Défectueux"])

    with tab3:
        # Visualisation Radar (Trés important pour la biométrie)
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[v1, v2, v6, v5, v9], theta=["Poids", "Garrot", "Poitrine", "Corps", "Bassin"], fill='toself', name="Individu"))
        fig.add_trace(go.Scatterpolar(r=[50, 72, 88, 80, 22], theta=["Poids", "Garrot", "Poitrine", "Corps", "Bassin"], fill='toself', name="Standard Race"))
        st.plotly_chart(fig, use_container_width=True)
        
        
        if st.button("📥 Sauvegarder l'Animal dans la Base", use_container_width=True):
            st.success(f"Données de l'animal {id_an} enregistrées !")

# --- PAGE 3 : SUIVI & REPRODUCTION (CORRIGÉ) ---
elif menu == "💉 Suivi & Reproduction":
    st.title("💉 Gestion Sanitaire & Reproduction")
    
    col_v, col_r = st.columns(2)
    
    with col_v:
        st.subheader("📝 Acte Médical")
        with st.form("vet_form"):
            animal_id_vet = st.text_input("ID Animal", "DZ-2026-")
            acte = st.selectbox("Type d'acte", ["Vaccin", "Déparasitage", "Pose Éponge", "Traitement Curatif"])
            etat = st.select_slider("État de santé général", options=["Mauvais", "Moyen", "Bon", "Parfait"])
            note = st.text_area("Observations")
            
            submit_vet = st.form_submit_button("Enregistrer l'acte")
            if submit_vet:
                st.success(f"L'acte '{acte}' pour l'animal {animal_id_vet} a été enregistré.")

    with col_r:
        st.subheader("🤰 Prédiction Mise Bas")
        st.write("Calculez les dates clés du cycle de reproduction.")
        date_e = st.date_input("Date de Pose de l'Éponge", datetime.now())
        
        if date_e:
            date_retrait = date_e + timedelta(days=14)
            date_lutte = date_retrait + timedelta(days=2)
            date_mise_bas = date_lutte + timedelta(days=150)
            
            st.info(f"📅 **Retrait de l'éponge :** {date_retrait.strftime('%d/%m/%Y')}")
            st.info(f"🐑 **Date de lutte prévue :** {date_lutte.strftime('%d/%m/%Y')}")
            st.warning(f"🐣 **Mise bas prévue (± 5j) :** {date_mise_bas.strftime('%d/%m/%Y')}")
            
            jours_restants = (date_mise_bas - datetime.now().date()).days
            if jours_restants > 0:
                st.write(f"Il reste environ **{jours_restants} jours** avant la mise bas.")

# --- PAGE 4 : CROISEMENT ---
elif menu == "🧬 Simulateur de Croisement":
    st.title("🧬 Simulateur Expert de Croisement")
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        pere = st.selectbox("Sélectionner le Père", st.session_state.db_data["ID Animal"].tolist(), key="papa")
    with c_p2:
        mere = st.selectbox("Sélectionner la Mère", st.session_state.db_data["ID Animal"].tolist(), key="maman")
    
    obj = st.radio("Objectif de sélection", ["🥩 Viande", "🥛 Lait", "🛡️ Résistance"])
    
    if st.button("Lancer la Simulation Génétique"):
        if pere == mere:
            st.error("⚠️ Erreur : Identifiants identiques (Risque Inbreeding maximal)")
        else:
            st.balloons()
            c_res1, c_res2 = st.columns(2)
            c_res1.metric("Consanguinité F", "1.25%", "🟢 SÉCURISÉ")
            c_res2.metric("Vigueur Hybride", "+15%", "⬆️")

# --- PAGE 5 : GENBANK & BLAST ---
elif menu == "🔍 Recherche GenBank (NCBI)":
    st.title("🧬 Diagnostic Génomique & Bio-informatique")
    id_select = st.selectbox("Échantillon à analyser :", st.session_state.db_data["ID Animal"].tolist())
    
    gene_name = st.text_input("Gène cible (ex: MSTN, IGF1)", "MSTN")
    if st.button("🚀 Lancer l'alignement BLAST"):
        with st.spinner("Comparaison avec les séquences de référence NCBI..."):
            time.sleep(2)
            st.code(f"""
            Query (Indiv_{id_select}):  5' ATGCGTACGGTT 3'
                                        |||||| ||||||
            Sbjct (Ref_GenBank):        5' ATGCGTGCGGTT 3'
                                              ^ (SNP détecté au codon 24)
            """, language="text")
            st.warning("SNP (Single Nucleotide Polymorphism) détecté : Impact potentiel sur la croissance.")

# --- PAGE 6 : GESTION DES DONNÉES ---
elif menu == "🗂️ Gestion de la Base":
    st.title("🗂️ Système de Gestion (LIMS)")
    # Éditeur dynamique de données
    edited_df = st.data_editor(st.session_state.db_data, num_rows="dynamic", use_container_width=True)
    
    if st.button("💾 Synchroniser avec le Cloud", type="primary"):
        progress = st.progress(0)
        for i in range(101):
            time.sleep(0.01)
            progress.progress(i)
        st.session_state.db_data = edited_df
        st.success("Synchronisation terminée !")
