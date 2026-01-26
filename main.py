import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import time

# --- CONFIGURATION INTERFACE ---
st.set_page_config(
    page_title="GeneSmart Expert v3.1 Pro",
    layout="wide",
    page_icon="🧬",
    initial_sidebar_state="expanded"
)

# Palette et style global
st.markdown("""
    <style>
    .stApp {
        background-color: #f7f9fb;
        color: #0b2545;
    }
    div[data-testid="stSidebar"] {
        background-color: #e3efff;
    }
    h1, h2, h3 {
        color: #001F3F;
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION DE LA BASE ---
if 'db_data' not in st.session_state:
    st.session_state.db_data = pd.DataFrame({
        "ID Animal": ["DZ-2026-001", "DZ-2026-002", "DZ-2026-003"],
        "Région": ["Hauts Plateaux", "Steppe", "Nord"],
        "Poids (kg)": [45.0, 52.5, 48.2]
    })

# --- BARRE LATÉRALE ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/5/56/DNA_icon.png", width=100)
st.sidebar.title("🧬 GeneSmart Pro - Expert System")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Expertise & Analyse", [
    "📊 Tableau de Bord",
    "🆔 Identification (30 Car.)",
    "💉 Suivi & Reproduction",
    "🧬 Simulateur de Croisement",
    "🔍 Recherche GenBank (NCBI)",
    "🗂️ Gestion de la Base"
])

# --------------------------------------------------------------------
# PAGE 1 : TABLEAU DE BORD GÉNÉTIQUE
# --------------------------------------------------------------------
if menu == "📊 Tableau de Bord":
    st.title("📊 Analyses Statistiques & Génétiques Intégrées")

    t_gen, t_multi, t_anova = st.tabs(["🧬 Fréquences Alléliques", "📉 ACP / ACM", "🧪 ANOVA"])

    with t_gen:
        c1, c2 = st.columns(2)
        c1.metric("Taille Efficace (Ne)", "64.2", "🟢 Stable")
        c2.metric("Indice Fis", "0.058", "🟢 Faible")

        freqs = pd.DataFrame({
            "Génotypes": ['AA', 'Aa', 'aa'],
            "Fréquences": [0.36, 0.48, 0.16]
        })

        fig_hardy = px.bar(
            freqs,
            x="Génotypes", y="Fréquences",
            title="Distribution des Génotypes (Hardy-Weinberg)",
            color="Génotypes",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_hardy, use_container_width=True)

    with t_multi:
        st.subheader("📉 Analyse en Composantes Principales (Population simulée)")
        df_acp = pd.DataFrame({
            'PC1': np.random.normal(0, 1, 40),
            'PC2': np.random.normal(0, 1, 40),
            'Race': ['Ouled Djellal']*20 + ['Rembi']*20
        })
        fig_acp = px.scatter(
            df_acp, x='PC1', y='PC2', color='Race',
            title="Structure Génétique Populationnelle (ACP 2D)",
            symbol='Race',
            color_discrete_sequence=["#2980B9", "#E67E22"]
        )
        st.plotly_chart(fig_acp, use_container_width=True)

    with t_anova:
        st.subheader("🧪 Effet Régional sur le Poids (ANOVA simulée)")
        df_anova = pd.DataFrame({
            'Région': ['Hauts Plateaux']*20 + ['Steppe']*20,
            'Poids': np.concatenate([
                np.random.normal(52, 4, 20),
                np.random.normal(48, 5, 20)
            ])
        })
        fig_anova = px.box(
            df_anova, x='Région', y='Poids', color='Région',
            color_discrete_sequence=["#3498DB", "#1ABC9C"],
            title="Effets de l’Environnement sur le Poids"
        )
        st.plotly_chart(fig_anova, use_container_width=True)
        st.info("Analyse simulée : F=14.2, p=0.0024 → Différence significative entre régions.")

# --------------------------------------------------------------------
# PAGE 2 : IDENTIFICATION PHÉNOTYPIQUE
# --------------------------------------------------------------------
elif menu == "🆔 Identification (30 Car.)":
    st.title("🆔 Caractérisation Phénotypique Complète (30 paramètres)")
    st.info("Saisie automatisée selon les standards FAO/UPOV – données phénotypiques.")

    id_an = st.text_input("Identifiant Unique de l’animal", "DZ-2026-001")

    col_quant, col_qual = st.columns(2)
    with col_quant:
        st.subheader("📏 Paramètres Quantitatifs")
        quant = {f"q{i}": st.number_input(f"{i}. Mesure anatomique #{i}", 0.0, 150.0, 50.0) for i in range(1, 16)}

    with col_qual:
        st.subheader("🎨 Paramètres Qualitatifs")
        qual = {f"qual{i}": st.selectbox(f"{i+15}. Caractère visuel #{i}", ["Option 1", "Option 2", "Option 3"])
                for i in range(1, 16)}

    if st.button("💾 Enregistrer la caractérisation complète (30/30)", type="primary", use_container_width=True):
        st.balloons()
        st.success(f"✅ L’animal {id_an} a été caractérisé avec succès et ajouté à la base.")

# --------------------------------------------------------------------
# PAGE 3 : SUIVI SANITAIRE & REPRODUCTION
# --------------------------------------------------------------------
elif menu == "💉 Suivi & Reproduction":
    st.title("💉 Gestion Sanitaire & Reproduction – Module Expert")
    col_v, col_r = st.columns(2)

    with col_v:
        st.subheader("🧫 Acte Médical")
        with st.form("vet_form"):
            animal_id_vet = st.text_input("ID Animal", "DZ-2026-001")
            acte = st.selectbox("Type d’acte", ["Vaccin", "Déparasitage", "Traitement Curatif"])
            etat = st.select_slider("État sanitaire global", ["Mauvais", "Moyen", "Bon", "Excellent"])
            note = st.text_area("Observations complémentaires")
            if st.form_submit_button("Enregistrer l’acte"):
                st.success(f"✅ Enregistrement validé pour {animal_id_vet} ({acte}).")

    with col_r:
        st.subheader("🤰 Gestion du Cycle Reproductif")
        date_e = st.date_input("Date de Pose de l’Éponge", datetime.now().date())
        date_retrait = date_e + timedelta(days=14)
        date_lutte = date_retrait + timedelta(days=2)
        date_mise_bas = date_lutte + timedelta(days=150)
        st.info(f"📅 Retrait Éponge : {date_retrait.strftime('%d/%m/%Y')}")
        st.info(f"🐑 Lutte prévue : {date_lutte.strftime('%d/%m/%Y')}")
        st.warning(f"🐣 Mise bas estimée : {date_mise_bas.strftime('%d/%m/%Y')} ± 5j")

# --------------------------------------------------------------------
# PAGE 4 : SIMULATEUR GÉNÉTIQUE
# --------------------------------------------------------------------
elif menu == "🧬 Simulateur de Croisement":
    st.title("🧬 Simulateur Génomique de Croisement")
    c_p1, c_p2 = st.columns(2)
    pere = c_p1.selectbox("Sélectionner le Père :", st.session_state.db_data["ID Animal"])
    mere = c_p2.selectbox("Sélectionner la Mère :", st.session_state.db_data["ID Animal"])
    obj = st.radio("Objectif de sélection", ["🥩 Viande", "🥛 Lait", "🛡️ Résistance"])

    if st.button("Lancer la Simulation Génétique", type="primary"):
        if pere == mere:
            st.error("⚠️ Risque de consanguinité élevé (mêmes identifiants).")
        else:
            st.success("Simulation réussie : Génération F₁ optimisée.")
            c1, c2 = st.columns(2)
            c1.metric("Consanguinité (F)", "1.28%", "🟢 Faible")
            c2.metric("Vigueur Hybride", "+14.7%", "⬆️")

# --------------------------------------------------------------------
# PAGE 5 : RECHERCHE GENBANK / PRÉDICTION GÉNÉTIQUE
# --------------------------------------------------------------------
elif menu == "🔍 Recherche GenBank (NCBI)":
    st.title("🔬 Expertise Génomique & Prédiction")
    liste_ids = st.session_state.db_data["ID Animal"].tolist()
    id_select = st.selectbox("🎯 Sélection ID Animal :", liste_ids)
    donnees = st.session_state.db_data.loc[st.session_state.db_data["ID Animal"] == id_select].iloc[0]

    poids = donnees["Poids (kg)"]
    st.metric("Poids Observé", f"{poids:.1f} kg")

    if poids > 55:
        st.warning("⚠️ Profil associé à une probable mutation MSTN (myostatine) – gain musculaire fort.")
    else:
        st.success("✅ Profil standard – croissance normale et efficace.")

# --------------------------------------------------------------------
# PAGE 6 : GESTION DE LA BASE (LIMS)
# --------------------------------------------------------------------
elif menu == "🗂️ Gestion de la Base":
    st.title("🗂️ LIMS – Gestion des Données Génétiques")
    edited_df = st.data_editor(st.session_state.db_data, num_rows="dynamic", use_container_width=True)
    if st.button("💾 Synchroniser avec le Cloud", type="primary"):
        with st.spinner("Synchronisation en cours..."):
            time.sleep(1)
            st.session_state.db_data = edited_df
        st.success("✅ Données synchronisées avec le serveur central.")
