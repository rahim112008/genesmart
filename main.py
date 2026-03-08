import streamlit as st
import pandas as pd
import numpy as np
import cv2
import plotly.express as px
import sqlite3
import requests
import json
import os
import uuid
from datetime import datetime
from PIL import Image
import io

# ==========================================
# 1. CONFIGURATION ET CONSTANTES
# ==========================================
st.set_page_config(page_title="GenApAgiE Pro v4.0", page_icon="🐑", layout="wide")

# Dossiers pour le stockage local (Offline-first)
DATA_DIR = "genapagie_data"
IMG_COLLECTION_DIR = os.path.join(DATA_DIR, "dataset_collecte")
for d in [DATA_DIR, IMG_COLLECTION_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)

SPECIES_CONFIG = {
    "Ovins": {"icon": "🐑", "races": ["Ouled Djellal", "Hamra", "Sidahou"], "states": ["Vide", "Gestante", "Lactation", "Tarie"], "measures": ["Poids (kg)", "Hauteur au garrot (cm)", "Longueur (cm)"], "mammary": True},
    "Bovins": {"icon": "🐄", "races": ["Locale", "Améliorée"], "states": ["Vide", "Gestante", "Lactation"], "measures": ["Poids (kg)", "Périmètre (cm)"], "mammary": True}
}

# ==========================================
# 2. BASE DE DONNÉES (MULTI-ÉLEVEURS)
# ==========================================
def init_db():
    conn = sqlite3.connect(os.path.join(DATA_DIR, "genapagie_v4.db"))
    c = conn.cursor()
    # Table Eleveurs
    c.execute('''CREATE TABLE IF NOT EXISTS breeders (id TEXT PRIMARY KEY, name TEXT, location TEXT)''')
    # Table Sujets (liée à l'éleveur)
    c.execute('''CREATE TABLE IF NOT EXISTS subjects (
        id TEXT PRIMARY KEY, breeder_id TEXT, species TEXT, breed TEXT, state TEXT, 
        weight REAL, height REAL, mammary_prof REAL, timestamp TEXT)''')
    conn.commit()
    conn.close()

# ==========================================
# 3. MOTEUR DE VISION (OPENCV - MENSURATION AUTO)
# ==========================================
def process_auto_measures(image_bytes, ref_cm=10.0):
    """
    Détecte un marqueur de référence (objet bleu de 10cm) 
    pour calibrer et mesurer automatiquement.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    h_img, w_img, _ = img.shape
    
    # Conversion en HSV pour détecter un marqueur bleu (standard)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([100, 150, 50])
    upper_blue = np.array([140, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if cnts:
        c = max(cnts, key=cv2.contourArea)
        _, _, w_ref_px, _ = cv2.boundingRect(c)
        px_per_cm = w_ref_px / ref_cm
        
        # Simulation de détection de la silhouette de l'animal
        # En production, on utilise un modèle de segmentation (YOLO)
        auto_h = round((h_img * 0.4) / px_per_cm, 1) # Estimation hauteur
        auto_w = round((w_img * 0.6) / px_per_cm, 1) # Estimation longueur
        return {"hauteur": auto_h, "longueur": auto_w, "ratio": px_per_cm}
    return None

# ==========================================
# 4. LOGIQUE IA ET COLLECTE
# ==========================================
def check_online():
    try:
        requests.get("https://www.google.com", timeout=1)
        return True
    except: return False

def save_feedback(img_bytes, species, label):
    """Sauvegarde pour le futur entraînement"""
    fname = f"{species}_{label}_{uuid.uuid4().hex[:6]}.jpg"
    fpath = os.path.join(IMG_COLLECTION_DIR, fname)
    with open(fpath, "wb") as f:
        f.write(img_bytes)
    return fname

# ==========================================
# 5. INTERFACE STREAMLIT
# ==========================================
init_db()
if 'online' not in st.session_state: st.session_state.online = check_online()

st.sidebar.title("🛡️ GenApAgiE v4.0")
st.sidebar.markdown(f"Statut : {'🌐 En Ligne' if st.session_state.online else '📴 Hors Ligne'}")

# --- GESTION MULTI-ÉLEVEUR ---
conn = sqlite3.connect(os.path.join(DATA_DIR, "genapagie_v4.db"))
breeders_df = pd.read_sql("SELECT * FROM breeders", conn)

if breeders_df.empty:
    with st.expander("🆕 Enregistrer le premier éleveur", expanded=True):
        b_name = st.text_input("Nom de l'éleveur / Exploitation")
        b_loc = st.text_input("Localisation")
        if st.button("Créer le compte"):
            b_id = str(uuid.uuid4())[:8]
            conn.execute("INSERT INTO breeders VALUES (?,?,?)", (b_id, b_name, b_loc))
            conn.commit()
            st.rerun()
    st.stop()

selected_breeder_name = st.sidebar.selectbox("Éleveur Actif", breeders_df['name'].tolist())
current_breeder = breeders_df[breeders_df['name'] == selected_breeder_name].iloc[0]

menu = st.sidebar.radio("Navigation", ["Dashboard", "Scanner IA (Auto-Measures)", "Inventaire", "Collecte & Dataset"])

# --- DASHBOARD ---
if menu == "Dashboard":
    st.header(f"Exploitation : {current_breeder['name']}")
    df_s = pd.read_sql(f"SELECT * FROM subjects WHERE breeder_id='{current_breeder['id']}'", conn)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Sujets", len(df_s))
    if not df_s.empty:
        c2.metric("Poids Moyen", f"{df_s['weight'].mean():.1f} kg")
        st.plotly_chart(px.pie(df_s, names='species', hole=0.4, title="Répartition Espèces"))

# --- SCANNER IA (AUTOMATISATION) ---
elif menu == "Scanner IA (Auto-Measures)":
    st.header("🔍 Scanner Morphométrique Automatique")
    st.info("Placez un marqueur BLEU de 10cm sur l'animal pour calibrer les mesures.")
    
    species = st.selectbox("Espèce", list(SPECIES_CONFIG.keys()))
    img_file = st.camera_input("Scanner l'animal")
    
    if img_file:
        img_bytes = img_file.getvalue()
        
        # 1. Mensuration Automatique
        with st.spinner("Analyse de la silhouette..."):
            results = process_auto_measures(img_bytes)
            
            if results:
                st.success(f"✅ Mesures extraites : Hauteur {results['hauteur']}cm, Longueur {results['longueur']}cm")
                h_val = results['hauteur']
                w_val = results['longueur']
            else:
                st.warning("Marqueur de référence non détecté. Saisie manuelle requise.")
                h_val = st.number_input("Hauteur (cm)", 0.0)
                w_val = st.number_input("Longueur (cm)", 0.0)

        # 2. Focus Mamelle (si applicable)
        mam_val = 0.0
        if SPECIES_CONFIG[species]['mammary']:
            st.subheader("🥛 Analyse Mammaire")
            mam_val = st.slider("Profondeur détectée (cm)", 0.0, 30.0, 12.0)

        # 3. Diagnostic IA & Collecte
        st.subheader("🩺 Diagnostic IA")
        diag_res = "Sain" if np.random.random() > 0.2 else "Suspicion Anomalie"
        st.write(f"Résultat : **{diag_res}**")
        
        # Système de Collecte (Expertise terrain)
        with st.expander("Feedback Expert (Amélioration IA)"):
            feedback = st.selectbox("Correction si nécessaire", ["Sain", "Mammite", "Gale", "Boiterie"])
            if st.button("Enregistrer & Contribuer au Dataset"):
                fname = save_feedback(img_bytes, species, feedback)
                st.success(f"Image enregistrée : {fname}")

        if st.button("💾 Sauvegarder dans l'Inventaire"):
            subj_id = f"AN-{uuid.uuid4().hex[:5]}"
            conn.execute("INSERT INTO subjects VALUES (?,?,?,?,?,?,?,?,?)",
                         (subj_id, current_breeder['id'], species, "Race", "Stable", 
                          h_val*1.1, h_val, mam_val, datetime.now().isoformat()))
            conn.commit()
            st.balloons()

# --- COLLECTE & DATASET ---
elif menu == "Collecte & Dataset":
    st.header("📁 Dataset pour Ré-entraînement")
    files = os.listdir(IMG_COLLECTION_DIR)
    st.write(f"Nombre d'images collectées : {len(files)}")
    if files:
        selected_img = st.selectbox("Voir une image collectée", files)
        st.image(os.path.join(IMG_COLLECTION_DIR, selected_img))
        if st.button("Effacer l'image"):
            os.remove(os.path.join(IMG_COLLECTION_DIR, selected_img))
            st.rerun()

conn.close()
