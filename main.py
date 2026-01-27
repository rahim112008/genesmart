import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURATION & DICTIONNAIRE SCIENTIFIQUE ---
st.set_page_config(page_title="BioGenExpert Pro v10.0", layout="wide", page_icon="🧬")

# Dictionnaire centralisé pour transformer V1, Q16 en noms clairs
LABEL_MAP = {
    "ID": "Identifiant Animal", "Age": "Âge (mois)", "GMQ": "Gain Moyen Quotidien (g/j)", "Date": "Date Collecte",
    "V1": "Poids Vif (kg)", "V2": "Hauteur au Garrot (cm)", "V3": "Hauteur à la Croupe (cm)", "V4": "Longueur du Corps (cm)",
    "V5": "Périmètre Thoracique (cm)", "V6": "Largeur Poitrine (cm)", "V7": "Profondeur Poitrine (cm)", "V8": "Largeur Hanches (cm)",
    "V9": "Largeur Trochanters (cm)", "V10": "Longueur Croupe (cm)", "V11": "Périmètre Canon (cm)", "V12": "Longueur Tête (cm)",
    "V13": "Largeur Tête (cm)", "V14": "Longueur Oreilles (cm)", "V15": "Longueur Cornes (cm)",
    "Q16": "Couleur Robe", "Q17": "Type Toison", "Q18": "Profil Tête", "Q19": "Forme Cornes", "Q20": "Position Oreilles",
    "Q21": "Pendeloques", "Q22": "Pigmentation Peau", "Q23": "Type Queue", "Q24": "Présence Cornes", "Q25": "État Santé",
    "Q26": "Conformation Pis", "Q27": "Tempérament", "Q28": "Structure Sabots", "Q29": "Localisation", "Q30": "Système Élevage"
}

# --- 2. INITIALISATION DU SESSION STATE ---
if 'db_data' not in st.session_state:
    cols = list(LABEL_MAP.keys())
    st.session_state.db_data = pd.DataFrame(columns=cols)
    # Ajout d'une ligne de démo pour éviter les erreurs d'affichage au départ
    demo = {"ID": "DEMO-01", "Age": 12, "GMQ": 250.0, "Date": datetime.now().date(), "V1": 45.0, "V2": 75.0, "V3": 74.0, "V4": 82.0, "V5": 92.0}
    for i in range(6, 16): demo[f"V{i}"] = 15.0
    for i in range(16, 31): demo[f"Q{i}"] = "Standard"
    st.session_state.db_data = pd.DataFrame([demo])

# --- 3. BARRE LATÉRALE ---
st.sidebar.title("🧬 BioGen Analytics Pro")
menu = st.sidebar.radio("Navigation Pipeline", [
    "🆔 Caractérisation (Saisie)", 
    "📊 Statistiques Multivariées", 
    "🔮 Prédiction & GeneBank",
    "🔀 Simulation de Croisement",
    "📊 Base de Données & Export"
])

# --- 4. PAGE 1 : CARACTÉRISATION ---
if menu == "🆔 Caractérisation (Saisie)":
    st.title("🆔 Identification et Phénotypage")
    with st.form("main_form"):
        c1, c2 = st.columns(2)
        id_an = c1.text_input("Identifiant Unique", "DZ-2026-")
        age_an = c2.number_input("Âge (mois)", min_value=1, value=12)

        col_quant, col_qual = st.columns(2)
        with col_quant:
            st.subheader("📏 Mesures (V1-V15)")
            v_vals = [st.number_input(LABEL_MAP[f"V{i}"], value=15.0 if i > 1 else 45.0) for i in range(1, 16)]
        with col_qual:
            st.subheader("🎨 Observations (Q16-Q30)")
            q_vals = [st.selectbox(LABEL_MAP[f"Q{i}"], ["Type A", "Type B", "Type C"]) for i in range(16, 31)]

        if st.form_submit_button("💾 Enregistrer"):
            gmq = round((v_vals[0] - 4.0) / (age_an * 30.44) * 1000, 2)
            new_entry = {"ID": id_an, "Age": age_an, "GMQ": gmq, "Date": datetime.now().date()}
            for i, v in enumerate(v_vals): new_entry[f"V{i+1}"] = v
            for i, q in enumerate(q_vals): new_entry[f"Q{i+16}"] = q
            st.session_state.db_data = pd.concat([st.session_state.db_data, pd.DataFrame([new_entry])], ignore_index=True)
            st.success("Données enregistrées !")

# --- 5. PAGE 2 : STATISTIQUES DYNAMIQUES ---
elif menu == "📊 Statistiques Multivariées":
    st.title("📊 Analyses Statistiques")
    df = st.session_state.db_data
    if len(df) < 2:
        st.warning("Veuillez saisir au moins 2 individus.")
    else:
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
        
        tab1, tab2, tab3 = st.tabs(["📉 ACP & Clusters", "🧪 ANOVA", "🔗 Corrélations"])
        
        with tab1:
            c1, c2, c3 = st.columns(3)
            x_ax = c1.selectbox("Axe X", num_cols, format_func=lambda x: LABEL_MAP.get(x, x))
            y_ax = c2.selectbox("Axe Y", num_cols, index=1, format_func=lambda x: LABEL_MAP.get(x, x))
            col_ax = c3.selectbox("Couleur", cat_cols, format_func=lambda x: LABEL_MAP.get(x, x))
            fig = px.scatter(df, x=x_ax, y=y_ax, color=col_ax, labels=LABEL_MAP, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
            

        with tab2:
            var_q = st.selectbox("Caractère", num_cols, format_func=lambda x: LABEL_MAP.get(x, x), key="v_q")
            var_f = st.selectbox("Facteur", cat_cols, format_func=lambda x: LABEL_MAP.get(x, x), key="v_f")
            st.plotly_chart(px.box(df, x=var_f, y=var_q, color=var_f, labels=LABEL_MAP), use_container_width=True)
            

        with tab3:
            df_corr = df[num_cols].rename(columns=LABEL_MAP)
            st.plotly_chart(px.imshow(df_corr.corr(), text_auto=True, color_continuous_scale='RdBu_r'), use_container_width=True)
            

# --- 6. PAGE 3 : PRÉDICTION & GENEBANK ---
elif menu == "🔮 Prédiction & GeneBank":
    st.title("🔮 Expertise Génomique")
    if not st.session_state.db_data.empty:
        id_sel = st.selectbox("Individu", st.session_state.db_data["ID"])
        data = st.session_state.db_data[st.session_state.db_data["ID"] == id_sel].iloc[0]
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🧬 Radar FAO")
            r_vals = [data['V2'], data['V3'], data['V4'], data['V5'], data['V1']/2]
            fig_r = go.Figure(data=go.Scatterpolar(r=r_vals, theta=['Garrot', 'Croupe', 'Corps', 'Thorax', 'Masse'], fill='toself'))
            st.plotly_chart(fig_r)
            
        
        with c2:
            st.subheader("🧬 Séquençage Virtuel")
            seq = "ATGCGTACGTTAGCAGCTAG" if data['GMQ'] > 200 else "ATGCGTACGTTAGCGGCTAG"
            st.code(seq)
            st.success("Génotype AA (Élite)" if data['GMQ'] > 200 else "Génotype GG (Standard)")
            if st.button("🚀 Lancer BLAST NCBI"):
                st.markdown(f'<meta http-equiv="refresh" content="0;URL=https://blast.ncbi.nlm.nih.gov/Blast.cgi?QUERY={seq}">', unsafe_allow_html=True)

# --- 7. PAGE 4 : SIMULATION ---
elif menu == "🔀 Simulation de Croisement":
    st.title("🔀 Simulation de Croisement & Dérive")
    if len(st.session_state.db_data) >= 2:
        ne = st.slider("Taille efficace (Ne)", 10, 500, 50)
        gen = st.slider("Générations", 5, 50, 20)
        freq = 0.5
        history = [freq]
        for _ in range(gen):
            freq = np.random.binomial(2*ne, freq) / (2*ne)
            history.append(freq)
        st.plotly_chart(px.line(y=history, labels={'y': 'Fréquence p', 'x': 'Génération'}, title="Simulation Dérive Génétique"))
    else:
        st.warning("Besoin de données.")

# --- 8. PAGE 5 : IMPORT / EXPORT ---
elif menu == "📊 Base de Données & Export":
    st.title("📊 Gestionnaire de Données")
    up = st.file_uploader("Importer fichier", type=["csv", "xlsx"])
    if up:
        try:
            ext = pd.read_csv(up) if up.name.endswith('csv') else pd.read_excel(up)
            st.session_state.db_data = pd.concat([st.session_state.db_data, ext], ignore_index=True)
            st.success("Données fusionnées !")
        except: st.error("Erreur de format.")
    
    st.dataframe(st.session_state.db_data)
    csv = st.session_state.db_data.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Télécharger CSV", csv, "BioGen_Export.csv", "text/csv")
