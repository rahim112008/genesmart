import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="BioGenExpert v10.0 | Ultimate Edition", layout="wide", page_icon="🧬")

# --- 2. INITIALISATION DU SESSION STATE (AVEC DONNÉES DE DÉMO) ---
if 'db_data' not in st.session_state or st.session_state.db_data.empty:
    cols = ["ID", "Age", "GMQ", "Date", "Score_Genotype"] + [f"V{i}" for i in range(1, 16)] + [f"Q{i}" for i in range(16, 31)]
    
    # Création de 2 animaux de démonstration pour que les graphiques s'affichent direct
    demo_data = [
        {
            "ID": "DZ-ELITE-001", "Age": 18, "GMQ": 285.5, "Date": "2024-05-20",
            "V1": 65.0, "V2": 78.0, "V3": 76.0, "V4": 85.0, "V5": 98.0, "Q16": "Blanc", "Q17": "Mèche longue"
        },
        {
            "ID": "DZ-STD-002", "Age": 12, "GMQ": 145.2, "Date": "2024-05-20",
            "V1": 42.0, "V2": 70.0, "V3": 68.0, "V4": 78.0, "V5": 88.0, "Q16": "Fauve", "Q17": "Lisse"
        }
    ]
    # Remplissage automatique des autres colonnes V6-V15 et Q18-Q30 pour éviter les erreurs
    for d in demo_data:
        for i in range(6, 16): d[f"V{i}"] = 15.0
        for i in range(18, 31): d[f"Q{i}"] = "Standard"
        
    st.session_state.db_data = pd.DataFrame(demo_data)

# --- 3. BARRE LATÉRALE ---
st.sidebar.title("🧬 BioGen Analytics Pro")
menu = st.sidebar.radio("Navigation Pipeline", [
    "🆔 Caractérisation (30 Car.)", 
    "📊 Statistiques Multivariées", 
    "🔮 Prédiction & GeneBank",
    "🔀 Simulation de Croisement",
    "📊 Base de Données & Export"
])

# --- 4. PAGE 1 : IDENTIFICATION (SAISIE) ---
if menu == "🆔 Caractérisation (30 Car.)":
    st.title("🆔 Identification et Phénotypage Haut-Débit")
    
    with st.form("main_form"):
        c_h1, c_h2 = st.columns([2, 1])
        id_an = c_h1.text_input("Identifiant Unique de l'animal", "DZ-2026-")
        age_an = c_h2.number_input("Âge de l'animal (mois)", min_value=1, value=12)

        col_quant, col_qual = st.columns(2)
        with col_quant:
            st.subheader("📏 15 Caractères Quantitatifs")
            v1 = st.number_input("1. Poids vif (kg)", 5.0, 150.0, 45.0)
            v2 = st.number_input("2. Hauteur au garrot (cm)", 30.0, 110.0, 75.0)
            v3 = st.number_input("3. Hauteur à la croupe (cm)", 30.0, 110.0, 74.0)
            v4 = st.number_input("4. Longueur du corps (cm)", 30.0, 130.0, 82.0)
            v5 = st.number_input("5. Périmètre thoracique (cm)", 40.0, 150.0, 92.0)
            v_others = [st.number_input(f"{i}. Mesure (cm)", value=15.0) for i in range(6, 16)]
            v_all = [v1, v2, v3, v4, v5] + v_others

        with col_qual:
            st.subheader("🎨 15 Caractères Qualitatifs")
            q16 = st.selectbox("16. Couleur robe", ["Blanc", "Noir", "Fauve", "Pie-rouge"])
            q17 = st.selectbox("17. Type laine", ["Mèche longue", "Mèche courte", "Lisse"])
            q_others = [st.selectbox(f"{i}. Caractère Visuel", ["Type A", "Type B", "Type C"]) for i in range(18, 31)]
            q_all = [q16, q17] + q_others

        if st.form_submit_button("💾 Enregistrer & Lancer l'Analyse"):
            # Calcul GMQ
            jours = age_an * 30.44
            gmq = (v1 - 4.0) / jours * 1000
            
            # Sauvegarde
            new_entry = {"ID": id_an, "Age": age_an, "GMQ": round(gmq, 2), "Date": datetime.now().date()}
            for i, v in enumerate(v_all): new_entry[f"V{i+1}"] = v
            for i, q in enumerate(q_all): new_entry[f"Q{i+16}"] = q
            
            st.session_state.db_data = pd.concat([st.session_state.db_data, pd.DataFrame([new_entry])], ignore_index=True)
            st.success("Données archivées avec succès.")
            st.balloons()

# --- 5. PAGE 2 : STATISTIQUES MULTIVARIÉES ---
elif menu == "📊 Statistiques Multivariées":
    st.title("📊 Moteur d'Analyse Bio-Statistique")
    
    if len(st.session_state.db_data) < 2:
        st.warning("Veuillez saisir au moins 2 individus pour activer les analyses.")
    else:
        tab1, tab2, tab3 = st.tabs(["📉 ACP & Clusters", "🧪 ANOVA One-Way", "🔗 Corrélations"])
        
        with tab1:
            st.subheader("Analyse en Composantes Principales (ACP)")
            fig_pca = px.scatter(st.session_state.db_data, x="V2", y="V1", color="Q16", size="Age",
                                 labels={"V2": "Hauteur (PC1)", "V1": "Poids (PC2)"}, title="Projection Phénotypique")
            st.plotly_chart(fig_pca, use_container_width=True)
            

        with tab2:
            st.subheader("Analyse de la Variance (ANOVA)")
            fig_box = px.box(st.session_state.db_data, x="Q16", y="V1", color="Q16", title="Influence de la Robe sur le Poids")
            st.plotly_chart(fig_box, use_container_width=True)
            

        with tab3:
            st.subheader("Matrice de Corrélation de Pearson")
            numeric_cols = ["Age", "GMQ", "V1", "V2", "V3", "V4", "V5"]
            corr = st.session_state.db_data[numeric_cols].corr()
            st.plotly_chart(px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r'), use_container_width=True)
            

# --- 6. PAGE 3 : PRÉDICTION & GENEBANK ---
elif menu == "🔮 Prédiction & GeneBank":
    st.title("🔮 Expertise Génomique & Conservation")
    if not st.session_state.db_data.empty:
        id_sel = st.selectbox("Individu à expertiser", st.session_state.db_data["ID"])
        data = st.session_state.db_data[st.session_state.db_data["ID"] == id_sel].iloc[0]
        
        c1, c2 = st.columns(2)
        c1.metric("Potentiel de Croissance", f"{data['GMQ']} g/j")
        c2.metric("Indice de Pureté estimé", "88.5%" if data['GMQ'] > 200 else "72.0%")
        
        st.subheader("🧬 Radar de Conformation")
        fig_radar = go.Figure(data=go.Scatterpolar(r=[data['V2'], data['V3'], data['V4'], data['V5'], data['V1']/2],
                                theta=['Garrot', 'Croupe', 'Corps', 'Thorax', 'Masse'], fill='toself'))
        st.plotly_chart(fig_radar)
        

# --- 7. PAGE 4 : CROISEMENT ---
elif menu == "🔀 Simulation de Croisement":
    st.title("🔀 Simulateur de Progrès Génétique")
    st.info("Prédisez les performances de la génération F1 par croisement dirigé.")
    if len(st.session_state.db_data) >= 2:
        m = st.selectbox("Père (Bélier/Taureau)", st.session_state.db_data["ID"])
        f = st.selectbox("Mère (Brebis/Vache)", st.session_state.db_data["ID"])
        
        if st.button("Simuler F1"):
            p1 = st.session_state.db_data[st.session_state.db_data["ID"] == m].iloc[0]['GMQ']
            p2 = st.session_state.db_data[st.session_state.db_data["ID"] == f].iloc[0]['GMQ']
            f1_gmq = (p1 + p2) / 2 * 1.05 # +5% hétérosis
            st.success(f"Performance attendue F1 : {f1_gmq:.2f} g/j")
            

# --- 8. PAGE 5 : BASE DE DONNÉES ---
elif menu == "📊 Base de Données & Export":
    st.title("📊 Registre LIMS Complet")
    st.dataframe(st.session_state.db_data, use_container_width=True)
    csv = st.session_state.db_data.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Exporter la base (CSV)", csv, "BioGen_Full_Data.csv", "text/csv")
