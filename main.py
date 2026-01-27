import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURATION & DICTIONNAIRE ---
st.set_page_config(page_title="BioGenExpert Pro v10.0", layout="wide", page_icon="🧬")

# Dictionnaire pour transformer les codes techniques en mots compréhensibles
LABEL_MAP = {
    "ID": "Identifiant", "Age": "Âge (mois)", "GMQ": "Gain Moyen Quotidien (g/j)", "Date": "Date Collecte",
    "V1": "Poids Vif (kg)", "V2": "Hauteur au Garrot (cm)", "V3": "Hauteur à la Croupe (cm)", 
    "V4": "Longueur du Corps (cm)", "V5": "Périmètre Thoracique (cm)",
    "Q29": "Race / Population", "Pere": "Père (Sire)", "Mere": "Mère (Dam)"
}

# --- 2. INITIALISATION DE LA BASE (10 INDIVIDUS DE DÉMO) ---
if 'db_data' not in st.session_state:
    data_demo = []
    races = ["Ouled-Djellal", "Rembi", "Hamra"]
    
    # Création de 10 individus pour la soutenance
    for i in range(1, 11):
        poids = np.random.uniform(40, 75)
        age = np.random.randint(12, 36)
        data_demo.append({
            "ID": f"AN-00{i}", "Age": age, "GMQ": round((poids-4)/365*1000, 2),
            "Date": datetime.now().date(), "V1": round(poids, 1), 
            "V2": round(np.random.uniform(70, 85), 1), "V3": round(np.random.uniform(68, 83), 1),
            "V4": round(np.random.uniform(80, 95), 1), "V5": round(np.random.uniform(85, 105), 1),
            "Q29": np.random.choice(races),
            "Pere": "Inconnu", "Mere": "Inconnu"
        })
    # Création d'un lien de parenté pour la démo (Le 3eme est le fils du 1er et 2eme)
    data_demo[2]["Pere"] = "AN-001"
    data_demo[2]["Mere"] = "AN-002"
    
    st.session_state.db_data = pd.DataFrame(data_demo)

# --- 3. FONCTION DE CALCUL DE PARENTÉ ---
def calculer_parenté(id1, id2):
    if id1 == "Inconnu" or id2 == "Inconnu": return 0.0
    if id1 == id2: return 1.0
    
    df = st.session_state.db_data
    p1 = df[df["ID"] == id1]["Pere"].values[0]
    m1 = df[df["ID"] == id1]["Mere"].values[0]
    p2 = df[df["ID"] == id2]["Pere"].values[0]
    m2 = df[df["ID"] == id2]["Mere"].values[0]
    
    if id1 in [p2, m2] or id2 in [p1, m1]: return 0.50 # Parent-Enfant
    if p1 == p2 and m1 == m2 and p1 != "Inconnu": return 0.50 # Frères/Sœurs
    if (p1 == p2 or m1 == m2) and p1 != "Inconnu": return 0.25 # Demi-frères
    return 0.0

# --- 4. BARRE LATÉRALE ---
st.sidebar.title("🧬 BioGen Pro Suite")
menu = st.sidebar.radio("Navigation", [
    "🆔 Saisie & Généalogie", 
    "📊 Statistiques Multivariées", 
    "🔀 Simulation & Risque",
    "💾 Base de Données"
])

# --- 5. PAGE 1 : SAISIE ---
if menu == "🆔 Saisie & Généalogie":
    st.title("🆔 Identification et Ascendance")
    with st.form("form_saisie"):
        c1, c2 = st.columns(2)
        new_id = c1.text_input("Nouvel Identifiant", "DZ-2026-")
        age_an = c2.number_input("Âge (mois)", 1, 120, 12)
        
        ancetres = ["Inconnu"] + st.session_state.db_data["ID"].tolist()
        pere = c1.selectbox("Sélectionner le Père", ancetres)
        mere = c2.selectbox("Sélectionner la Mère", ancetres)
        
        v1 = c1.number_input("Poids Vif (kg)", 5.0, 150.0, 45.0)
        race = c2.selectbox("Race", ["Ouled-Djellal", "Rembi", "Hamra", "Autre"])
        
        if st.form_submit_button("💾 Enregistrer dans le Livre Généalogique"):
            new_entry = {
                "ID": new_id, "Age": age_an, "GMQ": 200, "Date": datetime.now().date(),
                "V1": v1, "V2": 75.0, "V3": 74.0, "V4": 82.0, "V5": 92.0,
                "Q29": race, "Pere": pere, "Mere": mere
            }
            st.session_state.db_data = pd.concat([st.session_state.db_data, pd.DataFrame([new_entry])], ignore_index=True)
            st.success("Animal ajouté avec succès !")

# --- 6. PAGE 2 : STATISTIQUES (AVEC NOMS COMPRÉHENSIBLES) ---
elif menu == "📊 Statistiques Multivariées":
    st.title("📊 Analyses de la Population")
    df = st.session_state.db_data
    num_cols = ["Age", "GMQ", "V1", "V2", "V3", "V4", "V5"]
    
    tab1, tab2 = st.tabs(["📉 Nuage de Points (ACP)", "🧪 Comparaison (ANOVA)"])
    
    with tab1:
        c1, c2 = st.columns(2)
        x_ax = c1.selectbox("Axe X", num_cols, index=2, format_func=lambda x: LABEL_MAP[x])
        y_ax = c2.selectbox("Axe Y", num_cols, index=4, format_func=lambda x: LABEL_MAP[x])
        fig = px.scatter(df, x=x_ax, y=y_ax, color="Q29", size="V1", hover_name="ID", labels=LABEL_MAP, title="Analyse Morphologique")
        st.plotly_chart(fig, use_container_width=True)
        

    with tab2:
        var_sel = st.selectbox("Caractère à comparer", num_cols, format_func=lambda x: LABEL_MAP[x])
        st.plotly_chart(px.box(df, x="Q29", y=var_sel, color="Q29", labels=LABEL_MAP, title="Variabilité entre Races"), use_container_width=True)
        

# --- 7. PAGE 3 : SIMULATION & RISQUE ---
elif menu == "🔀 Simulation & Risque":
    st.title("🔀 Aide à l'Accouplement")
    c_m, c_f = st.columns(2)
    malle = c_m.selectbox("Choisir le Mâle", st.session_state.db_data["ID"], index=0)
    femelle = c_f.selectbox("Choisir la Femelle", st.session_state.db_data["ID"], index=1)
    
    coeff = calculer_parenté(malle, femelle)
    
    st.subheader("🛡️ Diagnostic de Consanguinité")
    if coeff >= 0.5:
        st.error(f"❌ ACCOUPLEMENT INTERDIT : Parenté de {coeff*100}% (Lien direct détecté).")
    elif 0 < coeff < 0.5:
        st.warning(f"⚠️ RISQUE ÉLEVÉ : Parenté de {coeff*100}% (Cousins ou Demi-frères).")
    else:
        st.success("✅ ACCOUPLEMENT AUTORISÉ : Aucune parenté détectée dans la base.")

    st.markdown("---")
    st.write("### 🌳 Arbre Généalogique Visuel")
    row_m = st.session_state.db_data[st.session_state.db_data["ID"] == malle].iloc[0]
    row_f = st.session_state.db_data[st.session_state.db_data["ID"] == femelle].iloc[0]
    
    col1, col2 = st.columns(2)
    col1.info(f"♂️ Mâle : **{malle}**\n\n- Père : {row_m['Pere']}\n- Mère : {row_m['Mere']}")
    col2.success(f"♀️ Femelle : **{femelle}**\n\n- Père : {row_f['Pere']}\n- Mère : {row_f['Mere']}")
    

# --- 8. PAGE 4 : BASE DE DONNÉES ---
elif menu == "💾 Base de Données":
    st.title("💾 Registre LIMS (Livre Généalogique)")
    df_visu = st.session_state.db_data.rename(columns=LABEL_MAP)
    st.dataframe(df_visu, use_container_width=True)
    
    csv = df_visu.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Télécharger la base complète (Excel/CSV)", csv, "BioGen_Final.csv", "text/csv")
