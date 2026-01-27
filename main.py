import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURATION & DICTIONNAIRE ---
st.set_page_config(page_title="BioGenExpert Pro v10.0", layout="wide", page_icon="🧬")

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

# --- 2. INITIALISATION AVEC 10 INDIVIDUS DE DÉMO ---
if 'db_data' not in st.session_state:
    data_demo = []
    races = ["Ouled-Djellal", "Rembi", "Hamra"]
    couleurs = ["Blanc", "Fauve", "Brun"]
    
    for i in range(1, 11):
        # Création de profils variés
        poids = np.random.uniform(40, 75)
        age = np.random.randint(10, 24)
        gmq = round((poids - 4.0) / (age * 30.44) * 1000, 2)
        
        indiv = {
            "ID": f"DZ-REF-{100+i}",
            "Age": age,
            "GMQ": gmq,
            "Date": datetime.now().date(),
            "V1": round(poids, 1),
            "V2": round(np.random.uniform(70, 85), 1),
            "V3": round(np.random.uniform(68, 83), 1),
            "V4": round(np.random.uniform(80, 95), 1),
            "V5": round(np.random.uniform(85, 105), 1),
            "Q16": np.random.choice(couleurs),
            "Q17": "Mèche longue" if gmq > 200 else "Lisse",
            "Q18": np.random.choice(["Droit", "Busqué"]),
            "Q29": np.random.choice(races), # On utilise Q29 pour la Race
            "Q30": "Extensif"
        }
        # Remplissage par défaut pour le reste (V6-V15 et Q19-Q28)
        for j in range(6, 16): indiv[f"V{j}"] = 15.0
        for j in range(19, 29): indiv[f"Q{j}"] = "Standard"
        data_demo.append(indiv)
    
    st.session_state.db_data = pd.DataFrame(data_demo)

# --- 3. NAVIGATION ---
st.sidebar.title("🧬 BioGen Pro Suite")
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
        id_an = c1.text_input("Identifiant Unique", "DZ-2026-NEW")
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

# --- 5. PAGE 2 : STATISTIQUES ---
elif menu == "📊 Statistiques Multivariées":
    st.title("📊 Analyses de la Population (n=10)")
    df = st.session_state.db_data
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    
    tab1, tab2, tab3 = st.tabs(["📉 ACP", "🧪 ANOVA", "🔗 Corrélations"])
    
    with tab1:
        c1, c2, c3 = st.columns(3)
        x_ax = c1.selectbox("Axe X", num_cols, index=2, format_func=lambda x: LABEL_MAP.get(x, x))
        y_ax = c2.selectbox("Axe Y", num_cols, index=4, format_func=lambda x: LABEL_MAP.get(x, x))
        col_ax = c3.selectbox("Grouper par", cat_cols, index=3, format_func=lambda x: LABEL_MAP.get(x, x))
        fig = px.scatter(df, x=x_ax, y=y_ax, color=col_ax, size="GMQ", hover_name="ID", labels=LABEL_MAP, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        

    with tab2:
        var_q = st.selectbox("Caractère", num_cols, index=2, format_func=lambda x: LABEL_MAP.get(x, x))
        var_f = st.selectbox("Facteur", cat_cols, index=3, format_func=lambda x: LABEL_MAP.get(x, x))
        st.plotly_chart(px.box(df, x=var_f, y=var_q, color=var_f, points="all", labels=LABEL_MAP), use_container_width=True)
        

    with tab3:
        df_corr = df[num_cols].rename(columns=LABEL_MAP)
        st.plotly_chart(px.imshow(df_corr.corr(), text_auto=True, color_continuous_scale='RdBu_r'), use_container_width=True)
        

# --- 6. PAGE 3 : PRÉDICTION ---
elif menu == "🔮 Prédiction & GeneBank":
    st.title("🔮 Expertise Individuelle")
    id_sel = st.selectbox("Sélectionner un animal de la base", st.session_state.db_data["ID"])
    data = st.session_state.db_data[st.session_state.db_data["ID"] == id_sel].iloc[0]
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🧬 Radar Morphologique")
        r_vals = [data['V2'], data['V3'], data['V4'], data['V5'], data['V1']]
        fig_r = go.Figure(data=go.Scatterpolar(r=r_vals, theta=['Garrot', 'Croupe', 'Corps', 'Thorax', 'Poids'], fill='toself', line_color='gold'))
        st.plotly_chart(fig_r)
        
    with c2:
        st.subheader("🧬 Génomique")
        seq = "ATGCGTACGTTAGCAGCTAG" if data['GMQ'] > 180 else "ATGCGTACGTTAGCGGCTAG"
        st.code(seq)
        st.info("Statut : ÉLITE (Candidat Séquençage)" if data['GMQ'] > 180 else "Statut : PRODUCTION")
        if st.button("🚀 BLAST NCBI"):
            st.markdown(f'<meta http-equiv="refresh" content="0;URL=https://blast.ncbi.nlm.nih.gov/Blast.cgi?QUERY={seq}">', unsafe_allow_html=True)

# --- 7. PAGE 4 & 5 (Simulation & Base) ---
elif menu == "🔀 Simulation de Croisement":
    st.title("🔀 Simulation")
    ne = st.slider("Taille Ne", 10, 200, 50)
    history = [0.5]
    for _ in range(20): history.append(np.random.binomial(2*ne, history[-1])/(2*ne))
    st.line_chart(history)

elif menu == "📊 Base de Données & Export":
    st.title("📊 Registre LIMS")
    st.dataframe(st.session_state.db_data)
    csv = st.session_state.db_data.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Télécharger CSV", csv, "BioGen_Soutenance.csv")
