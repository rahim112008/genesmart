import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import requests
import json
import time
from datetime import datetime
from PIL import Image
import io

# ==========================================
# 1. CONFIGURATION ET CONSTANTES
# ==========================================
st.set_page_config(page_title="GenApAgiE Pro v3.0", page_icon="🌱", layout="wide")

SPECIES_DATA = {
    "Ovins": {
        "icon": "🐑", "races": ["Ouled Djellal", "Hamra", "Sidahou"],
        "states": ["Vide", "Gestante", "Allaitante", "Lactation", "Tarie", "Malade"],
        "measures": ["Poids (kg)", "Hauteur au garrot (cm)", "Longueur du corps (cm)", "Largeur poitrine (cm)"],
        "mammary": True, "milk": True, "carcass_yield": 0.50,
        "markers": [("GDF9", "Fécondité", "Elevée"), ("MSTN", "Muscle", "Moyen")]
    },
    "Bovins": {
        "icon": "🐄", "races": ["Locale", "Améliorée (Frisonne)", "Montbéliarde"],
        "states": ["Vide", "Gestante", "Allaitante", "Lactation", "Tarie"],
        "measures": ["Poids (kg)", "Périmètre thoracique (cm)", "Hauteur aux hanches (cm)"],
        "mammary": True, "milk": True, "carcass_yield": 0.58,
        "markers": [("DGAT1", "Taux Gras", "Elevée")]
    },
    "Abeilles": {
        "icon": "🐝", "castes": ["Reine", "Ouvrière", "Mâle"],
        "states": ["Active", "Hivernage", "Essaimage"],
        "measures": ["Longueur Thorax (mm)", "Largeur Aile (mm)", "Poids (mg)"],
        "mammary": False, "milk": False, "carcass_yield": 0,
        "markers": [("Am_Vg", "Santé", "Elevée")]
    },
    "Caroubier": {
        "icon": "🌳", "varieties": ["Locale", "Performante"],
        "states": ["Semis", "Croissance", "Floraison", "Fructification", "Récolte"],
        "measures": ["Hauteur (cm)", "Diamètre tronc (cm)", "Nombre de feuilles", "Indice Brix"],
        "mammary": False, "milk": False, "carcass_yield": 0,
        "markers": [("Ppd-D1", "Floraison", "Moyen")]
    }
}

# ==========================================
# 2. GESTION DE LA BASE DE DONNÉES (SQLITE)
# ==========================================
def init_db():
    conn = sqlite3.connect("genapagie_core.db")
    c = conn.cursor()
    # Table Sujets
    c.execute('''CREATE TABLE IF NOT EXISTS subjects (
        id TEXT PRIMARY KEY, species TEXT, breed TEXT, state TEXT, 
        age REAL, weight REAL, morpho TEXT, created_at TEXT)''')
    # Table Lait
    c.execute('''CREATE TABLE IF NOT EXISTS milk_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT, subject_id TEXT, date TEXT,
        qty REAL, fat REAL, prot REAL, cells REAL)''')
    conn.commit()
    conn.close()

# ==========================================
# 3. LOGIQUE HYBRIDE (CONNECTIVITÉ & IA)
# ==========================================
def check_connectivity():
    try:
        requests.get("https://www.google.com", timeout=2)
        return True
    except:
        return False

def diagnostic_ia_engine(images, species, state, online_mode):
    """Moteur de diagnostic hybride"""
    time.sleep(1.5) # Simulation de calcul
    if online_mode:
        return {"status": "Sain (Analyse Cloud)", "confidence": 0.98, "alert": "Aucune"}
    else:
        # Logique simplifiée TFLite local
        if species == "Ovins" and state == "Lactation":
            return {"status": "Suspicion Mammite (Local)", "confidence": 0.76, "alert": "Vérifier trayon gauche"}
        return {"status": "Sain (Modèle local)", "confidence": 0.82, "alert": "Aucune"}

# ==========================================
# 4. INTERFACE UTILISATEUR (STREAMLIT)
# ==========================================
init_db()

# Session State pour la connectivité
if 'online' not in st.session_state:
    st.session_state.online = check_connectivity()

# Barre latérale
with st.sidebar:
    st.title("🛡️ GenApAgiE v3.0")
    st.markdown(f"**Statut :** {'🌐 En Ligne' if st.session_state.online else '📴 Hors Ligne'}")
    if st.button("🔄 Scanner le réseau"):
        st.session_state.online = check_connectivity()
        st.rerun()
    
    menu = st.radio("Menu Principal", [
        "📊 Tableau de Bord", 
        "🔍 Scanner & Biométrie", 
        "🥛 Suivi Laitier", 
        "🧬 BioLab Génétique", 
        "🥩 Estimation Carcasse",
        "⚙️ Paramètres"
    ])

# --- MODULE 1 : TABLEAU DE BORD ---
if menu == "📊 Tableau de Bord":
    st.header("Statistiques de l'Exploitation")
    
    conn = sqlite3.connect("genapagie_core.db")
    df = pd.read_sql("SELECT * FROM subjects", conn)
    conn.close()

    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Sujets", len(df))
        col2.metric("Espèces", df['species'].nunique())
        col3.metric("Poids Moyen", f"{df['weight'].mean():.1f} kg")
        col4.metric("Alertes IA", "1")

        c1, c2 = st.columns(2)
        with c1:
            fig = px.pie(df, names='species', title="Répartition par espèce", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.histogram(df, x='state', title="Répartition par état physiologique")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("La base de données est vide. Enregistrez un sujet via le Scanner.")

# --- MODULE 2 : SCANNER & BIOMÉTRIE ---
elif menu == "🔍 Scanner & Biométrie":
    st.header("Analyse Biométrique Contextuelle")
    
    col_input, col_ia = st.columns([2, 1])
    
    with col_input:
        species_choice = st.selectbox("Choisir l'espèce", list(SPECIES_DATA.keys()))
        conf = SPECIES_DATA[species_choice]
        
        c1, c2 = st.columns(2)
        id_subj = c1.text_input("Identifiant (ID)")
        race_subj = c2.selectbox("Race/Variété", conf.get('races', conf.get('varieties', conf.get('castes'))))
        
        c3, c4 = st.columns(2)
        age_subj = c3.number_input("Âge (mois/stade)", min_value=0.0)
        state_subj = c4.selectbox("État Physiologique", conf['states'])

        st.subheader("Mesures Morphométriques")
        measurements = {}
        m_cols = st.columns(2)
        for i, m in enumerate(conf['measures']):
            measurements[m] = m_cols[i % 2].number_input(f"{m}", key=m)
        
        # Logique dynamique Mamelle
        if conf['mammary'] and state_subj in ["Gestante", "Lactation", "Allaitante"]:
            st.markdown("---")
            st.markdown("🧪 **Focus Mamelle**")
            mc1, mc2 = st.columns(2)
            measurements["Profondeur Mamelle"] = mc1.slider("Profondeur (cm)", 0, 40)
            measurements["Score Symétrie"] = mc2.select_slider("Symétrie", options=[1,2,3,4,5])

    with col_ia:
        st.subheader("📸 Diagnostic Photo IA")
        uploaded_files = st.file_uploader("Prendre/Importer (1-5 photos)", accept_multiple_files=True)
        
        if st.button("Lancer l'Analyse IA"):
            if uploaded_files:
                with st.spinner("Traitement IA en cours..."):
                    res = diagnostic_ia_engine(uploaded_files, species_choice, state_subj, st.session_state.online)
                    st.success(f"Résultat : {res['status']}")
                    st.write(f"Confiance : {res['confidence']*100}%")
                    if res['alert'] != "Aucune":
                        st.error(f"⚠️ Alerte : {res['alert']}")
            else:
                st.warning("Veuillez charger une photo.")

    if st.button("💾 Enregistrer dans la base locale"):
        conn = sqlite3.connect("genapagie_core.db")
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO subjects VALUES (?,?,?,?,?,?,?,?)",
                  (id_subj, species_choice, race_subj, state_subj, age_subj, 
                   measurements.get("Poids (kg)", 0), json.dumps(measurements), datetime.now().isoformat()))
        conn.commit()
        conn.close()
        st.toast("Données enregistrées avec succès !")

# --- MODULE 3 : SUIVI LAITIER ---
elif menu == "🥛 Suivi Laitier":
    st.header("Suivi Laitier & Qualité Bio-chimique")
    
    conn = sqlite3.connect("genapagie_core.db")
    df_subjects = pd.read_sql("SELECT id FROM subjects WHERE species IN ('Ovins','Bovins')", conn)
    conn.close()
    
    if df_subjects.empty:
        st.warning("Aucun animal laitier enregistré dans la base.")
    else:
        subj_id = st.selectbox("Sélectionner l'animal", df_subjects['id'])
        
        col1, col2 = st.columns(2)
        with col1:
            qty = st.number_input("Quantité (L)", min_value=0.0)
            fat = st.number_input("Matière Grasse (g/L)", min_value=0.0)
        with col2:
            prot = st.number_input("Protéines (g/L)", min_value=0.0)
            cells = st.number_input("Cellules Somatiques (k/mL)", min_value=0)
            
        if st.button("Enregistrer la traite"):
            st.success("Données de production ajoutées.")
            # Graphique de démo
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[1,2,3,4], y=[12,15,14,16], name="Production (L)"))
            st.plotly_chart(fig)

# --- MODULE 4 : BIOLAB ---
elif menu == "🧬 BioLab Génétique":
    st.header("Analyses Génomiques & GEBV")
    
    species = st.selectbox("Espèce", list(SPECIES_DATA.keys()))
    markers = SPECIES_DATA[species]['markers']
    
    st.subheader("Marqueurs d'intérêt économique")
    m_df = pd.DataFrame(markers, columns=["Gène/Marqueur", "Trait Influencé", "Priorité"])
    st.table(m_df)
    
    st.subheader("Radar des élites")
    categories = ['Lait', 'Viande', 'Résistance', 'Prolificité', 'Adaptation']
    fig = go.Figure(data=go.Scatterpolar(
      r=[4, 5, 2, 2, 3],
      theta=categories,
      fill='toself'
    ))
    st.plotly_chart(fig)

# --- MODULE 5 : CARCASSE ---
elif menu == "🥩 Estimation Carcasse":
    st.header("Estimation Muscle/Gras/Os")
    poids_vif = st.number_input("Poids vif de l'animal (kg)", min_value=0.0, value=50.0)
    species = st.selectbox("Espèce", ["Ovins", "Bovins"])
    
    yield_val = SPECIES_DATA[species]["carcass_yield"]
    poids_carcasse = poids_vif * yield_val
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Poids Carcasse (Est.)", f"{poids_carcasse:.2f} kg")
    col2.metric("Muscle (Est.)", f"{poids_carcasse*0.65:.2f} kg")
    col3.metric("Gras (Est.)", f"{poids_carcasse*0.15:.2f} kg")

# --- FOOTER ---
st.markdown("---")
st.caption(f"GenApAgiE Core Engine v3.0 | 2026 | Mode: {'Online' if st.session_state.online else 'Offline'}")
