import streamlit as st
import sqlite3
import json
import math
import hashlib
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from PIL import Image
import io
import base64
import time
import numpy as np
from scipy import stats
import statsmodels.api as sm
import zipfile
import os
import uuid
from scipy.optimize import linprog
import joblib
import random

# Machine Learning
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet

# Pour l'analyse exploratoire (optionnel)
try:
    from ydata_profiling import ProfileReport
    from streamlit_pandas_profiling import st_profile_report
    profiling_available = True
except ImportError:
    profiling_available = False

# Traitement d'image
import cv2

# Outil pour les coordonnées de clics
from streamlit_image_coordinates import streamlit_image_coordinates

# Deep learning
import tensorflow as tf
from tensorflow.keras import layers, models
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------
PHOTO_DIR = "photos_brebis"
MODEL_DIR = "models"
DATASET_DIR = "dataset"
os.makedirs(PHOTO_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(DATASET_DIR, exist_ok=True)

class Config:
    APP_NAME = "Ovin Manager Pro"
    LABORATOIRE = "GenApAgiE"
    VERSION = "7.0"
    
    VERT = "#2E7D32"
    ORANGE = "#FF6F00"
    BLEU = "#1565C0"
    ROUGE = "#C62828"
    VIOLET = "#6A1B9A"
    CYAN = "#00838F"
    
    NCBI_EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    ETALONS = {
        "baton_1m": {"nom": "Bâton 1m", "largeur": 1000, "hauteur": None},
        "a4": {"nom": "Feuille A4", "largeur": 210, "hauteur": 297},
        "carte": {"nom": "Carte bancaire", "largeur": 85.6, "hauteur": 53.98},
        "piece_100da": {"nom": "Pièce 100 DA", "diametre": 29.5}
    }
    
    RACES = {
        "Hamra": {"origine": "Atlas saharien", "aptitude": "Mixte", "genes": ["BMP15", "GDF9"]},
        "Ouled Djellal": {"origine": "Steppes algériennes", "aptitude": "Viande", "genes": ["MSTN", "IGF2"]},
        "Sidahou": {"origine": "Aurès", "aptitude": "Lait", "genes": ["LALBA", "CSN3", "DGAT1"]},
        "Rembi": {"origine": "Tell", "aptitude": "Mixte", "genes": ["BMP15", "LALBA"]},
        "Autre": {"origine": "Inconnue", "aptitude": "Variable", "genes": []}
    }
    
    GENES_ECONOMIQUES = {
        "BMP15": {"nom": "Bone Morphogenetic Protein 15", "chr": "X", "effet": "Fécondité"},
        "GDF9": {"nom": "Growth Differentiation Factor 9", "chr": "5", "effet": "Fécondité"},
        "BMPR1B": {"nom": "BMP Receptor 1B", "chr": "6", "effet": "Prolificité (Booroola)"},
        "MSTN": {"nom": "Myostatin", "chr": "2", "effet": "Hypertrophie musculaire"},
        "IGF2": {"nom": "Insulin-like Growth Factor 2", "chr": "2", "effet": "Croissance"},
        "GH": {"nom": "Growth Hormone", "chr": "19", "effet": "Croissance"},
        "GHR": {"nom": "Growth Hormone Receptor", "chr": "16", "effet": "Efficacité alimentaire"},
        "LALBA": {"nom": "Alpha-Lactalbumin", "chr": "3", "effet": "Protéines lait"},
        "CSN3": {"nom": "Kappa-Casein", "chr": "6", "effet": "Qualité fromagère"},
        "DGAT1": {"nom": "Diacylglycerol Acyltransferase 1", "chr": "14", "effet": "Matière grasse lait"},
        "SCD": {"nom": "Stearoyl-CoA Desaturase", "chr": "22", "effet": "Acides gras insaturés"},
        "TLR4": {"nom": "Toll-like Receptor 4", "chr": "1", "effet": "Résistance infections"},
        "MHC": {"nom": "Major Histocompatibility Complex", "chr": "20", "effet": "Immunité"},
        "PRNP": {"nom": "Prion Protein", "chr": "13", "effet": "Résistance tremblante"},
        "CAST": {"nom": "Calpastatin", "chr": "7", "effet": "Tendreté viande"},
        "CAPN1": {"nom": "Calpain 1", "chr": "16", "effet": "Tendreté viande"},
        "FABP4": {"nom": "Fatty Acid Binding Protein 4", "chr": "8", "effet": "Marbling (gras intramusculaire)"}
    }
    
    ETATS_PHYSIO = [
        "Jeune", "Gestation début", "Gestation fin",
        "Lactation début", "Lactation milieu", "Lactation fin",
        "Tarie", "Engraissement"
    ]

# -----------------------------------------------------------------------------
# BASE DE DONNÉES
# -----------------------------------------------------------------------------
@st.cache_resource
def get_database():
    return Database()

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("ovin_streamlit.db", check_same_thread=False)
        self.init_database()
    
    def init_database(self):
        cursor = self.conn.cursor()
        
        # Tables existantes
        tables = [
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT,
                nom_laboratoire TEXT DEFAULT 'GenApAgiE', date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""",
            """CREATE TABLE IF NOT EXISTS eleveurs (
                id INTEGER PRIMARY KEY, user_id INTEGER, nom TEXT, region TEXT,
                telephone TEXT, email TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS elevages (
                id INTEGER PRIMARY KEY, eleveur_id INTEGER, nom TEXT,
                localisation TEXT, superficie REAL
            )""",
            """CREATE TABLE IF NOT EXISTS brebis (
                id INTEGER PRIMARY KEY, elevage_id INTEGER, numero_id TEXT UNIQUE,
                nom TEXT, race TEXT, date_naissance TEXT, etat_physio TEXT,
                photo_profil TEXT, photo_mamelle TEXT, sequence_fasta TEXT,
                variants_snps TEXT, profil_genetique TEXT
            )""",
            """CREATE TABLE IF NOT EXISTS mesures_morpho (
                id INTEGER PRIMARY KEY, brebis_id INTEGER, date_mesure TIMESTAMP,
                longueur_corps REAL, hauteur_garrot REAL, tour_poitrine REAL,
                circonference_canon REAL, largeur_bassin REAL, score_global REAL
            )""",
            """CREATE TABLE IF NOT EXISTS mesures_mamelles (
                id INTEGER PRIMARY KEY, brebis_id INTEGER, date_mesure TIMESTAMP,
                longueur_trayon REAL, diametre_trayon REAL, symetrie TEXT,
                attache TEXT, forme TEXT, score_total REAL
            )""",
            """CREATE TABLE IF NOT EXISTS composition_corporelle (
                id INTEGER PRIMARY KEY, brebis_id INTEGER, date_estimation TIMESTAMP,
                poids_vif REAL, poids_carcasse REAL, rendement_carcasse REAL,
                poids_viande REAL, pct_viande REAL, poids_graisse REAL,
                pct_graisse REAL, poids_os REAL, pct_os REAL,
                gigot_poids REAL, epaule_poids REAL, cotelette_poids REAL
            )""",
            """CREATE TABLE IF NOT EXISTS analyses_genomiques (
                id INTEGER PRIMARY KEY, brebis_id INTEGER, date_analyse TIMESTAMP,
                gene_cible TEXT, sequence_query TEXT, blast_hits TEXT,
                identite_pct REAL, e_value REAL
            )"""
        ]
        
        for table in tables:
            cursor.execute(table)
        
        # Ajout de la colonne poids_vif si elle n'existe pas
        cursor.execute("PRAGMA table_info(brebis)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'poids_vif' not in columns:
            cursor.execute("ALTER TABLE brebis ADD COLUMN poids_vif REAL")
        
        # Nouvelles tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productions (
                id INTEGER PRIMARY KEY,
                brebis_id INTEGER,
                date DATE,
                quantite REAL,
                ph REAL,
                mg REAL,
                proteine REAL,
                ag_satures REAL,
                densite REAL,
                extrait_sec REAL,
                FOREIGN KEY (brebis_id) REFERENCES brebis(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS genotypes (
                id INTEGER PRIMARY KEY,
                brebis_id INTEGER,
                snp_name TEXT,
                genotype TEXT,
                chromosome TEXT,
                position INTEGER,
                FOREIGN KEY (brebis_id) REFERENCES brebis(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS phenotypes (
                id INTEGER PRIMARY KEY,
                brebis_id INTEGER,
                trait TEXT,
                valeur REAL,
                date_mesure DATE,
                FOREIGN KEY (brebis_id) REFERENCES brebis(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diagnostics (
                id INTEGER PRIMARY KEY,
                brebis_id INTEGER,
                date DATE,
                maladie TEXT,
                symptomes TEXT,
                traitement TEXT,
                FOREIGN KEY (brebis_id) REFERENCES brebis(id)
            )
        """)
        
        # Tables nutrition
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aliments (
                id INTEGER PRIMARY KEY,
                nom TEXT UNIQUE,
                type TEXT,
                uem REAL,
                pdin REAL,
                ms REAL,
                prix_kg REAL
            )
        """)
        
        # Remplir la table aliments avec des données de base (marché algérien)
        aliments_init = [
            ("Orge", "Concentré", 1.1, 80, 86, 25),
            ("Maïs", "Concentré", 1.3, 70, 86, 30),
            ("Son de blé", "Concentré", 0.9, 120, 87, 18),
            ("Tourteau de soja", "Concentré", 1.2, 400, 88, 45),
            ("Foin de luzerne", "Fourrage", 0.6, 120, 85, 15),
            ("Foin d'avoine", "Fourrage", 0.5, 70, 85, 12),
            ("Paille", "Fourrage", 0.3, 20, 88, 5),
            ("CMV", "Minéral", 0, 0, 100, 80)
        ]
        for alim in aliments_init:
            try:
                cursor.execute("INSERT OR IGNORE INTO aliments (nom, type, uem, pdin, ms, prix_kg) VALUES (?, ?, ?, ?, ?, ?)", alim)
            except:
                pass
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rations (
                id INTEGER PRIMARY KEY,
                nom TEXT,
                etat_physio TEXT,
                description TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ration_composition (
                id INTEGER PRIMARY KEY,
                ration_id INTEGER,
                aliment_id INTEGER,
                quantite_kg REAL,
                FOREIGN KEY (ration_id) REFERENCES rations(id),
                FOREIGN KEY (aliment_id) REFERENCES aliments(id)
            )
        """)
        
        # Tables santé
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vaccinations (
                id INTEGER PRIMARY KEY,
                brebis_id INTEGER,
                date_vaccin DATE,
                vaccin TEXT,
                rappel DATE,
                FOREIGN KEY (brebis_id) REFERENCES brebis(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS soins (
                id INTEGER PRIMARY KEY,
                brebis_id INTEGER,
                date_soin DATE,
                type TEXT,
                diagnostic TEXT,
                traitement TEXT,
                FOREIGN KEY (brebis_id) REFERENCES brebis(id)
            )
        """)
        
        # Tables reproduction
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chaleurs (
                id INTEGER PRIMARY KEY,
                brebis_id INTEGER,
                date_debut DATE,
                date_fin DATE,
                methode_synchro TEXT,
                observation TEXT,
                FOREIGN KEY (brebis_id) REFERENCES brebis(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saillies (
                id INTEGER PRIMARY KEY,
                brebis_id INTEGER,
                date_saillie DATE,
                male_id TEXT,
                methode TEXT,
                resultat TEXT,
                FOREIGN KEY (brebis_id) REFERENCES brebis(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mises_bas (
                id INTEGER PRIMARY KEY,
                brebis_id INTEGER,
                date_mise_bas DATE,
                nb_agneaux INTEGER,
                poids_portee REAL,
                remarques TEXT,
                FOREIGN KEY (brebis_id) REFERENCES brebis(id)
            )
        """)
        
        self.conn.commit()
    
    def execute(self, query: str, params: tuple = ()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor
    
    def fetchall(self, query: str, params: tuple = ()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def fetchone(self, query: str, params: tuple = ()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

# -----------------------------------------------------------------------------
# FONCTION UTILITAIRE POUR LES PHOTOS
# -----------------------------------------------------------------------------
def save_uploaded_photo(uploaded_file):
    if uploaded_file is not None:
        ext = os.path.splitext(uploaded_file.name)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(PHOTO_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return filename
    return None

# -----------------------------------------------------------------------------
# FONCTION DE FILTRAGE PAR ÉLEVEUR
# -----------------------------------------------------------------------------
def filtrer_par_eleveur(query_base: str, params: list, join_eleveur: bool = True) -> tuple:
    if st.session_state.eleveur_id is not None:
        if join_eleveur:
            query_base += " AND el.id=?"
        else:
            query_base += " AND eleveur_id=?"
        params.append(st.session_state.eleveur_id)
    return query_base, tuple(params)

# -----------------------------------------------------------------------------
# CLASSES MÉTIER
# -----------------------------------------------------------------------------
class OvinScience:
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def calcul_score_morpho(longueur: float, hauteur: float, poitrine: float, 
                          canon: float, bassin: float) -> float:
        try:
            indice_format = (longueur / hauteur) * 100 if hauteur > 0 else 0
            indice_corpulence = (poitrine / hauteur) * 100 if hauteur > 0 else 0
            
            score = 40
            if 100 <= indice_format <= 120: score += 20
            if 115 <= indice_corpulence <= 135: score += 20
            if canon > 7.0: score += 10
            if bassin > 18: score += 10
            
            return min(100, round(score, 2))
        except:
            return 0
    
    @staticmethod
    def calcul_score_mamelle(long_trayon: float, diametre: float,
                           symetrie: str, attache: str, forme: str) -> float:
        score = 5.0
        if 4 <= long_trayon <= 6: score += 1.5
        if 2 <= diametre <= 3: score += 1.5
        if symetrie == "Symétrique": score += 0.5
        if attache == "Solide": score += 0.5
        if forme == "Globuleuse": score += 0.5
        if attache != "Pendante": score += 0.5
        return min(10, round(score, 2))
    
    @staticmethod
    def estimer_composition(poids_vif: float, race: str, condition_corporelle: float) -> Dict:
        try:
            rendement = 0.48 if race == "Ouled Djellal" else 0.45 if race == "Sidahou" else 0.46
            rendement += (condition_corporelle - 3) * 0.01
            poids_carcasse = poids_vif * rendement
            
            if condition_corporelle >= 4:
                pct_viande, pct_graisse, pct_os = 0.55, 0.28, 0.17
            elif condition_corporelle <= 2:
                pct_viande, pct_graisse, pct_os = 0.62, 0.18, 0.20
            else:
                pct_viande, pct_graisse, pct_os = 0.58, 0.23, 0.19
            
            if race == "Ouled Djellal":
                pct_viande += 0.02
                pct_graisse -= 0.01
            
            return {
                "poids_vif": poids_vif,
                "poids_carcasse": round(poids_carcasse, 2),
                "rendement": round(rendement * 100, 1),
                "viande": {"kg": round(poids_carcasse * pct_viande, 2), "pct": round(pct_viande * 100, 1)},
                "graisse": {"kg": round(poids_carcasse * pct_graisse, 2), "pct": round(pct_graisse * 100, 1)},
                "os": {"kg": round(poids_carcasse * pct_os, 2), "pct": round(pct_os * 100, 1)},
                "decoupes": {
                    "gigot": round(poids_carcasse * 0.22, 2),
                    "epaule": round(poids_carcasse * 0.17, 2),
                    "cotelette": round(poids_carcasse * 0.14, 2),
                    "poitrine": round(poids_carcasse * 0.12, 2)
                },
                "qualite": {
                    "conformation": min(15, max(1, 8 + int((condition_corporelle - 3) * 1.5) + (2 if race == "Ouled Djellal" else 0))),
                    "gras": int(condition_corporelle)
                }
            }
        except Exception as e:
            return {"erreur": str(e)}
    
    @staticmethod
    def besoins_nutritionnels(poids: float, etat: str, lactation: float = 0) -> Dict:
        besoins = {
            "maintenance": {"uem": 0.5, "pdin": 45, "ms": 1.0},
            "gestation": {"uem": 0.7, "pdin": 70, "ms": 1.2},
            "lactation": {"uem": 1.2, "pdin": 120, "ms": 2.5},
            "tarie": {"uem": 0.55, "pdin": 50, "ms": 1.1},
            "engraissement": {"uem": 0.8, "pdin": 60, "ms": 1.5}
        }
        base = besoins.get("maintenance")
        for key in besoins:
            if key in etat.lower():
                base = besoins[key]
                break
        if lactation > 0:
            base["uem"] += lactation * 0.4
            base["pdin"] += lactation * 8
        return {k: round(v, 2) for k, v in base.items()}

class MachineLearning:
    @staticmethod
    def predire_lait(score_mam: float, score_morpho: float, race: str, age: int) -> Dict:
        base = 0.5
        if score_mam >= 8: base += 1.5
        elif score_mam >= 6: base += 0.8
        if score_morpho >= 80: base += 0.3
        if race == "Lacaune": base *= 1.3
        if 3 <= age <= 6: base *= 1.2
        return {
            "litres_jour": round(base, 2),
            "litres_lactation": round(base * 180, 2),
            "niveau": "Élite" if base > 1.5 else "Bon" if base > 1.0 else "Standard"
        }

class NCBIApi:
    def __init__(self):
        self.base_url = Config.NCBI_EUTILS_BASE
    
    def search_gene(self, gene_name: str, organism: str = "Ovis aries") -> List[Dict]:
        try:
            url = f"{self.base_url}/esearch.fcgi"
            params = {
                "db": "gene",
                "term": f"{gene_name}[Gene] AND {organism}[Organism]",
                "retmode": "json",
                "retmax": 5
            }
            with st.spinner(f"Recherche {gene_name} dans NCBI..."):
                response = requests.get(url, params=params, timeout=30)
                data = response.json()
            gene_ids = data.get("esearchresult", {}).get("idlist", [])
            if gene_ids:
                return self.fetch_gene_details(gene_ids)
            return []
        except Exception as e:
            st.error(f"Erreur API NCBI: {e}")
            return []
    
    def fetch_gene_details(self, gene_ids: List[str]) -> List[Dict]:
        try:
            url = f"{self.base_url}/esummary.fcgi"
            params = {"db": "gene", "id": ",".join(gene_ids), "retmode": "json"}
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            results = []
            for gid in gene_ids:
                summary = data.get("result", {}).get(gid, {})
                results.append({
                    "gene_id": gid,
                    "name": summary.get("name", "N/A"),
                    "description": summary.get("description", "N/A"),
                    "chromosome": summary.get("chromosome", "N/A"),
                    "map_location": summary.get("maplocation", "N/A")
                })
            return results
        except Exception as e:
            st.error(f"Erreur détails gènes: {e}")
            return []
    
    def fetch_fasta(self, accession: str) -> Optional[str]:
        try:
            url = f"{self.base_url}/efetch.fcgi"
            params = {"db": "nucleotide", "id": accession, "rettype": "fasta", "retmode": "text"}
            response = requests.get(url, params=params, timeout=30)
            return response.text if response.status_code == 200 else None
        except Exception as e:
            st.error(f"Erreur FASTA: {e}")
            return None

class GenomicAnalyzer:
    def __init__(self):
        self.ncbi = NCBIApi()
    
    def analyze_race_profile(self, race: str) -> Dict:
        genes_race = Config.RACES.get(race, {}).get("genes", [])
        results = {
            "race": race,
            "genes": [],
            "score_reproduction": 0,
            "score_croissance": 0,
            "score_lait": 0,
            "recommandations": []
        }
        for gene in genes_race:
            info = Config.GENES_ECONOMIQUES.get(gene, {})
            results["genes"].append({
                "symbole": gene,
                "nom": info.get("nom", ""),
                "effet": info.get("effet", ""),
                "chromosome": info.get("chr", "")
            })
            if gene in ["BMP15", "GDF9", "BMPR1B"]:
                results["score_reproduction"] += 33
            if gene in ["MSTN", "IGF2", "GH"]:
                results["score_croissance"] += 33
            if gene in ["LALBA", "CSN3", "DGAT1"]:
                results["score_lait"] += 33
        results["score_reproduction"] = min(100, results["score_reproduction"])
        results["score_croissance"] = min(100, results["score_croissance"])
        results["score_lait"] = min(100, results["score_lait"])
        if results["score_reproduction"] > 70:
            results["recommandations"].append("✅ Excellente valeur reproductive")
        if results["score_croissance"] > 70:
            results["recommandations"].append("✅ Excellente conformation viande")
        if results["score_lait"] > 70:
            results["recommandations"].append("✅ Excellent potentiel laitier")
        return results

# -----------------------------------------------------------------------------
# FONCTIONS ML
# -----------------------------------------------------------------------------
def train_lait_model():
    """Entraîne un modèle RandomForest pour prédire la production laitière."""
    query = """
        SELECT p.quantite, b.race, b.date_naissance, 
               AVG(m.score_global) as score_morpho,
               AVG(m2.score_total) as score_mamelle,
               COUNT(DISTINCT p.id) as nb_mesures
        FROM productions p
        JOIN brebis b ON p.brebis_id = b.id
        LEFT JOIN mesures_morpho m ON b.id = m.brebis_id
        LEFT JOIN mesures_mamelles m2 ON b.id = m2.brebis_id
        GROUP BY b.id
        HAVING nb_mesures > 0
    """
    df = pd.read_sql_query(query, db.conn)
    if len(df) < 20:
        return None  # Pas assez de données
    
    # Features
    df['age'] = (datetime.now() - pd.to_datetime(df['date_naissance'])).dt.days / 365
    df = pd.get_dummies(df, columns=['race'], prefix='race')
    feature_cols = [c for c in df.columns if c not in ['quantite', 'date_naissance', 'nb_mesures']]
    X = df[feature_cols].fillna(0)
    y = df['quantite']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    
    # Sauvegarde
    joblib.dump(model, os.path.join(MODEL_DIR, 'lait_model.pkl'))
    joblib.dump(feature_cols, os.path.join(MODEL_DIR, 'lait_features.pkl'))
    return model, score

def predict_lait_ml(brebis_id):
    """Prédit la production laitière pour une brebis donnée en utilisant le modèle entraîné."""
    model_path = os.path.join(MODEL_DIR, 'lait_model.pkl')
    features_path = os.path.join(MODEL_DIR, 'lait_features.pkl')
    if not os.path.exists(model_path) or not os.path.exists(features_path):
        return None
    
    model = joblib.load(model_path)
    feature_cols = joblib.load(features_path)
    
    # Récupérer les infos de la brebis
    query = """
        SELECT b.race, b.date_naissance,
               AVG(m.score_global) as score_morpho,
               AVG(m2.score_total) as score_mamelle
        FROM brebis b
        LEFT JOIN mesures_morpho m ON b.id = m.brebis_id
        LEFT JOIN mesures_mamelles m2 ON b.id = m2.brebis_id
        WHERE b.id = ?
        GROUP BY b.id
    """
    row = db.fetchone(query, (brebis_id,))
    if not row:
        return None
    
    race, date_naiss, score_morpho, score_mamelle = row
    age = (datetime.now() - datetime.strptime(date_naiss, "%Y-%m-%d")).days / 365 if date_naiss else 0
    
    # Créer un DataFrame avec les bonnes colonnes
    data = {'score_morpho': score_morpho or 0, 'score_mamelle': score_mamelle or 0, 'age': age}
    # Encodage one-hot de la race
    for col in feature_cols:
        if col.startswith('race_'):
            data[col] = 1 if col == f"race_{race}" else 0
        elif col not in data:
            data[col] = 0
    
    X = pd.DataFrame([data])[feature_cols].fillna(0)
    pred = model.predict(X)[0]
    return pred

def cluster_brebis(df, n_clusters=3):
    """Applique un clustering KMeans sur les brebis."""
    features = ['prod_moy (L/j)', 'score_morpho', 'poids', 'viande_estimee (kg)']
    # Sélectionner les colonnes existantes
    avail = [f for f in features if f in df.columns]
    if len(avail) < 2:
        return None
    X = df[avail].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    return clusters, kmeans.cluster_centers_, avail

def detect_anomalies(df, contamination=0.1):
    """Détecte les anomalies avec IsolationForest."""
    features = ['prod_moy (L/j)', 'score_morpho', 'poids', 'viande_estimee (kg)']
    avail = [f for f in features if f in df.columns]
    if len(avail) < 2:
        return None
    X = df[avail].fillna(0)
    model = IsolationForest(contamination=contamination, random_state=42)
    preds = model.fit_predict(X)  # -1 pour anomalies, 1 pour normaux
    return preds

# -----------------------------------------------------------------------------
# FONCTIONS DE DÉTECTION D'ÉTALON
# -----------------------------------------------------------------------------
def detecter_baton(image, seuil_canny1=50, seuil_canny2=150):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, seuil_canny1, seuil_canny2)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
    if lines is not None:
        max_len = 0
        best_line = None
        for line in lines:
            x1, y1, x2, y2 = line[0]
            length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
            if length > max_len:
                max_len = length
                best_line = (x1, y1, x2, y2)
        return best_line, max_len
    return None, 0

def detecter_feuille(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        if len(approx) == 4:  # rectangle
            (x, y, w, h) = cv2.boundingRect(approx)
            long_cote = max(w, h)
            return approx, long_cote
    return None, 0

def detecter_piece(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=100,
                               param1=50, param2=30, minRadius=10, maxRadius=100)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        max_radius = 0
        best_circle = None
        for (x, y, r) in circles:
            if r > max_radius:
                max_radius = r
                best_circle = (x, y, r)
        return best_circle, 2 * max_radius
    return None, 0

# -----------------------------------------------------------------------------
# FONCTIONS POUR L'APPRENTISSAGE
# -----------------------------------------------------------------------------
def enregistrer_donnees_apprentissage(image, points, facteur_echelle, race, age_mois, mesures, type_animal="corps"):
    """Enregistre l'image, les points, les mesures et métadonnées pour l'entraînement."""
    img_resized = cv2.resize(image, (256, 256))
    h, w = image.shape[:2]
    points_norm = {k: (v[0]/w, v[1]/h) for k, v in points.items()}
    data = {
        'image': img_resized,
        'points_norm': points_norm,
        'facteur_echelle': facteur_echelle,
        'race': race,
        'age_mois': age_mois,
        'type': type_animal,
        'mesures': mesures
    }
    filename = os.path.join(DATASET_DIR, f"{uuid.uuid4().hex}.npz")
    np.savez(filename, **data)
    return filename

def charger_dataset():
    """Charge toutes les images et points du dossier dataset."""
    images = []
    points_list = []
    metadatas = []
    for f in os.listdir(DATASET_DIR):
        if f.endswith('.npz'):
            data = np.load(os.path.join(DATASET_DIR, f), allow_pickle=True)
            images.append(data['image'])
            pts = data['points_norm'].item()
            # Ordre : garrot, sol, epaule, fesse, queue, bassin_g, bassin_d, thorax_g, thorax_d, canon_h, canon_b
            # Mais pour simplifier, on suppose un ordre fixe
            # Ici on crée un vecteur de 22 coordonnées (11 points *2)
            vec = []
            for key in ['garrot', 'sol', 'epaule', 'fesse', 'queue', 'bassin_g', 'bassin_d', 'thorax_g', 'thorax_d', 'canon_h', 'canon_b']:
                if key in pts:
                    vec.extend([pts[key][0], pts[key][1]])
                else:
                    vec.extend([0,0])
            points_list.append(vec)
            metadatas.append(data['metadata'].item() if 'metadata' in data else {})
    if len(images) == 0:
        return None, None, None
    X = np.array(images, dtype=np.float32) / 255.0
    y = np.array(points_list, dtype=np.float32)
    return X, y, metadatas

def entrainer_modele():
    """Entraîne un modèle CNN pour la prédiction des points clés."""
    X, y, _ = charger_dataset()
    if X is None or len(X) < 10:
        return None, "Pas assez de données (minimum 10 images)."
    
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    
    model = models.Sequential([
        layers.Conv2D(32, (3,3), activation='relu', input_shape=(256,256,3)),
        layers.MaxPooling2D(2,2),
        layers.Conv2D(64, (3,3), activation='relu'),
        layers.MaxPooling2D(2,2),
        layers.Conv2D(128, (3,3), activation='relu'),
        layers.MaxPooling2D(2,2),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(22)  # 11 points * 2
    ])
    
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    history = model.fit(X_train, y_train, epochs=50, validation_data=(X_test, y_test), verbose=0)
    
    model.save(os.path.join(MODEL_DIR, 'keypoints_model.h5'))
    return model, history

# -----------------------------------------------------------------------------
# PAGES DE L'APPLICATION
# -----------------------------------------------------------------------------
def page_login():
    st.markdown('<p class="main-header">🐑 Ovin Manager Pro</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Laboratoire {Config.LABORATOIRE} - Système Expert de Génétique Ovine</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["Connexion", "Inscription"])
        
        with tab1:
            username = st.text_input("Nom d'utilisateur", key="login_user")
            password = st.text_input("Mot de passe", type="password", key="login_pass")
            
            if st.button("Se connecter", use_container_width=True):
                user = db.fetchone(
                    "SELECT id FROM users WHERE username=? AND password_hash=?",
                    (username, OvinScience.hash_password(password))
                )
                if user:
                    st.session_state.user_id = user[0]
                    st.session_state.current_page = "dashboard"
                    st.rerun()
                else:
                    st.error("Identifiants incorrects")
        
        with tab2:
            new_user = st.text_input("Nouvel utilisateur", key="new_user")
            new_pass = st.text_input("Mot de passe", type="password", key="new_pass")
            confirm_pass = st.text_input("Confirmer mot de passe", type="password")
            
            if st.button("Créer compte", use_container_width=True):
                if new_pass != confirm_pass:
                    st.error("Les mots de passe ne correspondent pas")
                elif not new_user or not new_pass:
                    st.error("Remplissez tous les champs")
                else:
                    try:
                        db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                                  (new_user, OvinScience.hash_password(new_pass)))
                        st.success("Compte créé ! Connectez-vous")
                    except:
                        st.error("Nom d'utilisateur déjà pris")

def page_dashboard():
    st.title(f"📊 Tableau de Bord - {Config.LABORATOIRE}")
    
    stats = db.fetchone("""
        SELECT 
            (SELECT COUNT(*) FROM eleveurs WHERE user_id=?),
            (SELECT COUNT(*) FROM brebis b JOIN elevages e ON b.elevage_id = e.id 
             JOIN eleveurs el ON e.eleveur_id = el.id WHERE el.user_id=?),
            (SELECT COUNT(*) FROM composition_corporelle cc 
             JOIN brebis b ON cc.brebis_id = b.id JOIN elevages e ON b.elevage_id = e.id
             JOIN eleveurs el ON e.eleveur_id = el.id WHERE el.user_id=?)
    """, (st.session_state.user_id, st.session_state.user_id, st.session_state.user_id))
    
    cols = st.columns(4)
    metrics = [
        ("👨‍🌾 Éleveurs", stats[0], Config.VERT),
        ("🐑 Brebis", stats[1], Config.BLEU),
        ("🧬 Analyses", stats[2], Config.CYAN),
        ("📈 Données", stats[0] + stats[1] + stats[2], Config.ORANGE)
    ]
    
    for col, (label, value, color) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div style="background-color: {color}20; border-radius: 10px; padding: 20px; text-align: center; border-left: 5px solid {color}">
                <h3 style="color: {color}; margin: 0;">{value}</h3>
                <p style="margin: 0; color: #666;">{label}</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("🚀 Modules Génomiques & Analytiques")
    
    modules = [
        ("🧬 Analyse NCBI/GenBank", "Recherche gènes, SNPs, BLAST", "genomique", Config.CYAN),
        ("🥩 Composition Corporelle", "Estimation viande/graisse/os", "composition", Config.ORANGE),
        ("📸 Photogrammétrie", "Mesures morphométriques IA", "analyse", Config.VERT),
        ("🥛 Prédiction Lait", "ML potentiel laitier", "prediction", Config.VIOLET),
        ("🌾 Nutrition", "Formulation rations", "nutrition_avancee", Config.BLEU),
        ("🧠 IA & Data Mining", "Analyses avancées, clustering, anomalies", "ia", Config.ROUGE),
    ]
    
    cols = st.columns(3)
    for i, (title, desc, page, color) in enumerate(modules):
        with cols[i % 3]:
            with st.container():
                st.markdown(f"""
                <div style="background-color: white; border-radius: 10px; padding: 20px; 
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px;
                            border-top: 4px solid {color};">
                    <h4 style="color: {color}; margin-top: 0;">{title}</h4>
                    <p style="color: #666; font-size: 0.9rem;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Ouvrir →", key=f"btn_{page}", use_container_width=True):
                    st.session_state.current_page = page
                    st.rerun()

def page_genomique():
    st.title("🧬 Analyse Génomique - NCBI/GenBank")
    
    tab1, tab2, tab3 = st.tabs(["🔍 Recherche Gène", "🏆 Profil Race", "🧪 SNPs/QTN"])
    
    with tab1:
        st.subheader("Recherche dans NCBI Gene")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            gene_search = st.text_input("Nom du gène", "BMP15", 
                                       help="Ex: BMP15, MSTN, DGAT1, CAST...")
        with col2:
            organism = st.selectbox("Organisme", ["Ovis aries (Mouton)", "Capra hircus (Chèvre)", "Bos taurus (Bovin)"])
        
        if st.button("🔍 Rechercher dans NCBI", use_container_width=True):
            results = genomic_analyzer.ncbi.search_gene(gene_search, "Ovis aries")
            
            if results:
                for gene in results:
                    with st.container():
                        st.markdown(f"""
                        <div class="gene-card">
                            <h4>🧬 {gene['name']} (ID: {gene['gene_id']})</h4>
                            <p><strong>Description:</strong> {gene['description']}</p>
                            <p><strong>Chromosome:</strong> {gene['chromosome']} | <strong>Position:</strong> {gene['map_location']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        local_info = Config.GENES_ECONOMIQUES.get(gene_search.upper())
                        if local_info:
                            st.info(f"**Effet économique:** {local_info['effet']}")
            else:
                local = Config.GENES_ECONOMIQUES.get(gene_search.upper())
                if local:
                    st.success("Informations depuis la base locale GenApAgiE")
                    st.json(local)
                else:
                    st.warning("Gène non trouvé. Essayez: BMP15, MSTN, DGAT1, CAST, CAPN1...")
    
    with tab2:
        st.subheader("Profil Génétique par Race")
        
        race_selected = st.selectbox("Sélectionner une race", list(Config.RACES.keys()))
        
        if st.button("🧬 Analyser le profil génétique"):
            analysis = genomic_analyzer.analyze_race_profile(race_selected)
            
            fig = go.Figure(data=go.Scatterpolar(
                r=[analysis['score_reproduction'], analysis['score_croissance'], 
                   analysis['score_lait'], analysis['score_reproduction']],
                theta=['Reproduction', 'Croissance/Viande', 'Lait', 'Reproduction'],
                fill='toself',
                name=race_selected
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=False,
                title=f"Profil Génétique: {race_selected}"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Gènes Majeurs")
            for gene in analysis['genes']:
                with st.expander(f"🧬 {gene['symbole']} - {gene['nom'][:40]}..."):
                    st.write(f"**Effet:** {gene['effet']}")
                    st.write(f"**Chromosome:** {gene['chromosome']}")
            
            if analysis['recommandations']:
                st.success("### ✅ Recommandations")
                for rec in analysis['recommandations']:
                    st.write(rec)
    
    with tab3:
        st.subheader("Base de données SNPs et QTN économiques")
        
        categorie = st.selectbox("Filtrer par catégorie", 
                                ["Tous", "Reproduction", "Croissance/Viande", "Lait", "Résistance", "Qualité viande"])
        
        genes_filtres = []
        for sym, info in Config.GENES_ECONOMIQUES.items():
            if categorie == "Tous":
                genes_filtres.append((sym, info))
            elif categorie == "Reproduction" and any(x in sym for x in ["BMP", "GDF"]):
                genes_filtres.append((sym, info))
            elif categorie == "Croissance/Viande" and any(x in sym for x in ["MSTN", "IGF", "GH"]):
                genes_filtres.append((sym, info))
            elif categorie == "Lait" and any(x in sym for x in ["LALBA", "CSN", "DGAT", "SCD"]):
                genes_filtres.append((sym, info))
            elif categorie == "Résistance" and any(x in sym for x in ["TLR", "MHC", "PRNP"]):
                genes_filtres.append((sym, info))
            elif categorie == "Qualité viande" and any(x in sym for x in ["CAST", "CAPN", "FABP"]):
                genes_filtres.append((sym, info))
        
        df_genes = pd.DataFrame([
            {
                "Symbole": sym,
                "Nom": info["nom"][:50] + "...",
                "Chr": info["chr"],
                "Effet": info["effet"][:60] + "...",
                "Type": "QTN" if sym in ["BMP15", "MSTN", "DGAT1", "BMPR1B"] else "SNP"
            }
            for sym, info in genes_filtres
        ])
        
        st.dataframe(df_genes, use_container_width=True, hide_index=True)
        
        gene_detail = st.selectbox("Voir détails", [sym for sym, _ in genes_filtres])
        if gene_detail:
            info = Config.GENES_ECONOMIQUES[gene_detail]
            st.json(info)

def page_composition():
    st.title("🥩 Composition Corporelle Estimée")
    st.markdown("Estimation détaillée de la répartition viande/graisse/os basée sur les équations zootechniques")

    # Récupération des brebis selon l'éleveur actif
    params = [st.session_state.user_id]
    query_brebis = """
        SELECT b.id, b.numero_id, b.nom, b.race, e.nom
        FROM brebis b
        JOIN elevages e ON b.elevage_id = e.id
        JOIN eleveurs el ON e.eleveur_id = el.id
        WHERE el.user_id=?
    """
    query_brebis, params = filtrer_par_eleveur(query_brebis, params, join_eleveur=True)
    brebis_list = db.fetchall(query_brebis, params)
    
    brebis_options = {f"{b[0]} - {b[1]} {b[2]} ({b[4]})": b[0] for b in brebis_list}
    brebis_options["Saisie manuelle (animal non enregistré)"] = None

    mode = st.radio("Mode de saisie", ["Sélectionner une brebis existante", "Saisie manuelle"])

    if mode == "Sélectionner une brebis existante":
        selected = st.selectbox("Choisir une brebis", list(brebis_options.keys()))
        brebis_id = brebis_options[selected]
        if brebis_id is not None:
            info = db.fetchone("SELECT poids_vif, race, etat_physio FROM brebis WHERE id=?", (brebis_id,))
            if info:
                poids_def = info[0] if info[0] is not None else 45.0
                race_def = info[1] if info[1] else "Autre"
                etat_def = info[2] if info[2] else "Tarie"
            else:
                poids_def = 45.0
                race_def = "Autre"
                etat_def = "Tarie"
        else:
            poids_def = 45.0
            race_def = "Autre"
            etat_def = "Tarie"
    else:
        brebis_id = None
        poids_def = 45.0
        race_def = "Autre"
        etat_def = "Tarie"

    col1, col2, col3 = st.columns(3)
    with col1:
        poids_vif = st.number_input("Poids vif (kg)", min_value=10.0, max_value=150.0, value=poids_def, step=0.5)
    with col2:
        race = st.selectbox("Race", list(Config.RACES.keys()), index=list(Config.RACES.keys()).index(race_def) if race_def in Config.RACES else 0)
    with col3:
        cc = st.slider("Condition Corporelle (1-5)", min_value=1.0, max_value=5.0, value=3.0, step=0.5,
                      help="1=Très maigre, 3=Idéal, 5=Très gras")

    if st.button("🧮 Calculer la composition", use_container_width=True):
        comp = OvinScience.estimer_composition(poids_vif, race, cc)

        if "erreur" in comp:
            st.error(comp["erreur"])
            return

        st.subheader("📊 Résultats")

        cols = st.columns(4)
        metrics = [
            ("🥩 Viande", comp['viande']['kg'], comp['viande']['pct'], Config.VERT),
            ("🥓 Graisse", comp['graisse']['kg'], comp['graisse']['pct'], Config.ORANGE),
            ("🦴 Os", comp['os']['kg'], comp['os']['pct'], "grey"),
            ("📦 Carcasse", comp['poids_carcasse'], comp['rendement'], Config.BLEU)
        ]
        for col, (label, kg, pct, color) in zip(cols, metrics):
            with col:
                st.markdown(f"""
                <div style="background-color: {color}15; border-radius: 10px; padding: 20px; 
                            text-align: center; border-left: 4px solid {color};">
                    <h4 style="color: {color}; margin: 0;">{kg} kg</h4>
                    <p style="margin: 0; font-size: 0.9rem;">{label}</p>
                    <p style="margin: 0; font-size: 0.8rem; color: #666;">{pct}%</p>
                </div>
                """, unsafe_allow_html=True)

        fig = go.Figure(data=[go.Pie(
            labels=['Viande', 'Graisse', 'Os'],
            values=[comp['viande']['kg'], comp['graisse']['kg'], comp['os']['kg']],
            marker_colors=[Config.VERT, Config.ORANGE, 'grey'],
            hole=0.4
        )])
        fig.update_layout(title="Composition de la carcasse (kg)")
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("🔪 Détails des découpes"):
            decoupes_data = {
                "Découpe": ["Gigot", "Épaule", "Côtelettes", "Poitrine"],
                "Poids (kg)": [comp['decoupes']['gigot'], comp['decoupes']['epaule'],
                              comp['decoupes']['cotelette'], comp['decoupes']['poitrine']],
                "% Carcasse": [22, 17, 14, 12]
            }
            df_decoupes = pd.DataFrame(decoupes_data)
            st.dataframe(df_decoupes, hide_index=True, use_container_width=True)

        if brebis_id is not None:
            if st.button("💾 Enregistrer cette composition dans la base"):
                db.execute("""
                    INSERT INTO composition_corporelle 
                    (brebis_id, date_estimation, poids_vif, poids_carcasse, rendement_carcasse,
                     poids_viande, pct_viande, poids_graisse, pct_graisse, poids_os, pct_os,
                     gigot_poids, epaule_poids, cotelette_poids)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    brebis_id, datetime.now().isoformat(),
                    poids_vif, comp['poids_carcasse'], comp['rendement'],
                    comp['viande']['kg'], comp['viande']['pct'],
                    comp['graisse']['kg'], comp['graisse']['pct'],
                    comp['os']['kg'], comp['os']['pct'],
                    comp['decoupes']['gigot'], comp['decoupes']['epaule'], comp['decoupes']['cotelette']
                ))
                st.success("Composition enregistrée pour cette brebis !")

    # Section de comparaison
    st.divider()
    st.subheader("🔍 Comparer plusieurs brebis")

    if len(brebis_list) >= 2:
        selected_ids = st.multiselect(
            "Choisir les brebis à comparer",
            options=list(brebis_options.keys()),
            default=list(brebis_options.keys())[:min(2, len(brebis_options))]
        )
        selected_ids = [brebis_options[id_str] for id_str in selected_ids if brebis_options[id_str] is not None]

        if len(selected_ids) >= 2:
            comp_data = []
            for bid in selected_ids:
                row = db.fetchone("""
                    SELECT poids_vif, poids_carcasse, rendement_carcasse,
                           poids_viande, poids_graisse, poids_os, date_estimation
                    FROM composition_corporelle
                    WHERE brebis_id=?
                    ORDER BY date_estimation DESC
                    LIMIT 1
                """, (bid,))
                if row:
                    name = db.fetchone("SELECT numero_id, nom FROM brebis WHERE id=?", (bid,))
                    label = f"{name[0]} {name[1]}" if name else f"Brebis {bid}"
                    comp_data.append({
                        "id": bid,
                        "nom": label,
                        "poids_vif": row[0],
                        "poids_carcasse": row[1],
                        "rendement": row[2],
                        "viande": row[3],
                        "graisse": row[4],
                        "os": row[5],
                        "date": row[6]
                    })
            if comp_data:
                df_comp = pd.DataFrame(comp_data)
                fig_comp = go.Figure()
                for animal in comp_data:
                    fig_comp.add_trace(go.Bar(
                        name=animal['nom'],
                        x=['Viande', 'Graisse', 'Os'],
                        y=[animal['viande'], animal['graisse'], animal['os']],
                        text=[f"{animal['viande']} kg", f"{animal['graisse']} kg", f"{animal['os']} kg"],
                        textposition='auto'
                    ))
                fig_comp.update_layout(
                    title="Comparaison des compositions (kg)",
                    barmode='group',
                    yaxis_title="Poids (kg)"
                )
                st.plotly_chart(fig_comp, use_container_width=True)

                st.dataframe(df_comp[['nom', 'poids_vif', 'poids_carcasse', 'rendement', 'viande', 'graisse', 'os']].round(2),
                           use_container_width=True, hide_index=True)
            else:
                st.warning("Aucune composition enregistrée pour ces brebis. Calculez d'abord une composition et enregistrez-la.")
    else:
        st.info("Ajoutez au moins deux brebis et enregistrez leurs compositions pour activer la comparaison.")

def page_prediction():
    st.title("🔮 Prédiction par Machine Learning")
    
    st.subheader("Potentiel laitier estimé")
    
    col1, col2 = st.columns(2)
    
    with col1:
        score_mam = st.slider("Score mamelles", 1.0, 10.0, 7.0, 0.5)
        score_morpho = st.slider("Score morphologique", 0, 100, 75)
    
    with col2:
        race = st.selectbox("Race", list(Config.RACES.keys()))
        age = st.number_input("Âge (années)", 1, 15, 4)
    
    if st.button("🔮 Prédire production (formule simple)"):
        pred = MachineLearning.predire_lait(score_mam, score_morpho, race, age)
        
        cols = st.columns(3)
        cols[0].metric("Production/jour", f"{pred['litres_jour']} L")
        cols[1].metric("Production/lactation", f"{pred['litres_lactation']} L")
        cols[2].metric("Niveau", pred['niveau'])
        
        fig = px.bar(
            x=["Potentiel estimé", "Moyenne race", "Record élite"],
            y=[pred['litres_jour'], 1.2, 2.5],
            color=[pred['niveau'], "Moyenne", "Élite"],
            title="Comparaison production laitière (L/jour)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    st.subheader("Prédiction avancée par modèle ML")
    
    model_path = os.path.join(MODEL_DIR, 'lait_model.pkl')
    if os.path.exists(model_path):
        st.success("Un modèle ML est disponible.")
        params = [st.session_state.user_id]
        query_brebis = """
            SELECT b.id, b.numero_id, b.nom, e.nom
            FROM brebis b
            JOIN elevages e ON b.elevage_id = e.id
            JOIN eleveurs el ON e.eleveur_id = el.id
            WHERE el.user_id=?
        """
        query_brebis, params = filtrer_par_eleveur(query_brebis, params, join_eleveur=True)
        brebis_list = db.fetchall(query_brebis, params)
        brebis_dict = {f"{b[0]} - {b[1]} {b[2]} ({b[3]})": b[0] for b in brebis_list}
        
        if brebis_dict:
            selected = st.selectbox("Choisir une brebis", list(brebis_dict.keys()), key="ml_brebis")
            bid = brebis_dict[selected]
            if st.button("Prédire avec ML"):
                pred = predict_lait_ml(bid)
                if pred is not None:
                    st.metric("Production prédite (L/j)", f"{pred:.2f}")
                else:
                    st.warning("Impossible de faire la prédiction (données manquantes).")
        else:
            st.warning("Aucune brebis disponible.")
    else:
        st.info("Aucun modèle ML entraîné. Vous pouvez en entraîner un si vous avez suffisamment de données de production.")
        if st.button("Entraîner un modèle ML"):
            with st.spinner("Entraînement en cours..."):
                result = train_lait_model()
                if result is None:
                    st.error("Pas assez de données (minimum 20 brebis avec productions).")
                else:
                    model, score = result
                    st.success(f"Modèle entraîné avec un score R² de {score:.2f} sur le test.")

# -----------------------------------------------------------------------------
# NOUVELLE VERSION DE LA PHOTOGRAMMÉTRIE (intégrée)
# -----------------------------------------------------------------------------
def page_analyse():
    st.title("📸 Analyse Photogrammétrique")

    # Initialisation des variables de session pour le guidage séquentiel
    if 'etape_corps' not in st.session_state:
        st.session_state.etape_corps = 0  # 0: droite, 1: gauche, 2: arriere, 3: mamelles, 4: terminé
    if 'photos_corps' not in st.session_state:
        st.session_state.photos_corps = {}  # clé = vue, valeur = image
    if 'points_par_vue' not in st.session_state:
        st.session_state.points_par_vue = {}  # pour stocker les points de chaque vue
    if 'facteur_global' not in st.session_state:
        st.session_state.facteur_global = None

    # Valeurs par défaut pour les mesures (corps et mamelles)
    for k, v in [('longueur_corps', 70.0), ('hauteur_garrot', 65.0), ('tour_poitrine', 80.0),
                 ('circonf_canon', 8.0), ('largeur_bassin', 20.0), ('longueur_queue', 20.0),
                 ('largeur_thorax', 25.0), ('profondeur_thorax', 30.0)]:
        if k not in st.session_state:
            st.session_state[k] = v
    for k, v in [('long_trayon_g', 5.0), ('long_trayon_d', 5.0), ('diam_trayon', 2.5),
                 ('attache', 10.0), ('symetrie', 'Symétrique'), ('forme', 'Globuleuse')]:
        if k not in st.session_state:
            st.session_state[k] = v

    # Variables factices pour l'exemple (remplacez-les par les vraies valeurs de votre sélection de brebis)
    age_mois = 24
    race_brebis = "Ouled Djellal"
    brebis_id = 1

    # -------------------------------------------------------------------------
    # MORPHOMÉTRIE CORPS ET MAMELLES (guidage séquentiel)
    # -------------------------------------------------------------------------
    st.header("Morphométrie Corps et Mamelles")

    vues_ordre = ["droite", "gauche", "arriere", "mamelles"]
    noms_vues = ["côté droit", "côté gauche", "arrière (bassin/queue)", "arrière (mamelles)"]
    points_par_vue = {
        "droite": {"noms": ["Garrot", "Sol", "Épaule", "Fesse", "Queue", "Canon haut", "Canon bas"], "total": 7},
        "gauche": {"noms": ["Garrot", "Sol", "Épaule", "Fesse", "Queue", "Canon haut", "Canon bas"], "total": 7},
        "arriere": {"noms": ["Bassin gauche", "Bassin droit", "Thorax gauche", "Thorax droit"], "total": 4},
        "mamelles": {"noms": ["Base trayon gauche", "Extrémité trayon gauche", "Base trayon droit",
                               "Extrémité trayon droit", "Attache gauche", "Attache droite"], "total": 6}
    }

    # Barre de progression
    st.progress(st.session_state.etape_corps / len(vues_ordre))

    if st.session_state.etape_corps < len(vues_ordre):
        vue_courante = vues_ordre[st.session_state.etape_corps]
        nom_vue = noms_vues[st.session_state.etape_corps]
        st.write(f"### Étape {st.session_state.etape_corps+1}/{len(vues_ordre)} : Photo {nom_vue}")

        # Si la photo pour cette vue n'est pas encore chargée
        if vue_courante not in st.session_state.photos_corps:
            st.write(f"Veuillez fournir une photo de {nom_vue}.")
            source = st.radio("Source", ["Télécharger un fichier", "Prendre une photo"], key=f"source_{vue_courante}")
            img = None
            if source == "Télécharger un fichier":
                uploaded = st.file_uploader("Choisir une photo", type=['jpg','png','jpeg'], key=f"upload_{vue_courante}")
                if uploaded:
                    img_pil = Image.open(uploaded)
                    img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            else:
                cam = st.camera_input("Prendre une photo", key=f"cam_{vue_courante}")
                if cam:
                    img_pil = Image.open(cam)
                    img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            if img is not None:
                st.session_state.photos_corps[vue_courante] = img
                st.success(f"Photo {nom_vue} enregistrée.")
                st.rerun()
        else:
            # La photo est déjà chargée, on affiche et on passe à la collecte des points
            img = st.session_state.photos_corps[vue_courante]
            st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), use_column_width=True)

            # Facteur d'échelle (si pas encore défini)
            if st.session_state.facteur_global is None:
                st.info("Définissez le facteur d'échelle (une seule fois).")
                etalon = st.selectbox("Étalon de calibration", list(Config.ETALONS.keys()),
                                       format_func=lambda x: Config.ETALONS[x]['nom'], key=f"etalon_{vue_courante}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔍 Détecter l'étalon sur cette image"):
                        facteur = None
                        if etalon == "baton_1m":
                            line, len_px = detecter_baton(img)
                            if line is not None:
                                facteur = len_px / 100
                        elif etalon == "a4":
                            rect, long_px = detecter_feuille(img)
                            if rect is not None:
                                facteur = long_px / 29.7
                        elif etalon == "piece_100da":
                            circle, diam_px = detecter_piece(img)
                            if circle is not None:
                                facteur = diam_px / 2.95
                        if facteur:
                            st.session_state.facteur_global = facteur
                            st.success(f"Facteur d'échelle : {facteur:.2f} px/cm")
                            st.rerun()
                        else:
                            st.error("Étalon non détecté.")
                with col2:
                    facteur_manuel = st.number_input("Ou saisir manuellement (px/cm)", value=10.0, step=0.1)
                    if st.button("Utiliser ce facteur"):
                        st.session_state.facteur_global = facteur_manuel
                        st.rerun()
            else:
                st.info(f"Facteur d'échelle actuel : {st.session_state.facteur_global:.2f} px/cm")

                # Collecte des points pour cette vue
                if f"points_{vue_courante}" not in st.session_state:
                    st.session_state[f"points_{vue_courante}"] = []
                if f"etape_{vue_courante}" not in st.session_state:
                    st.session_state[f"etape_{vue_courante}"] = 0

                points_clic = st.session_state[f"points_{vue_courante}"]
                etape = st.session_state[f"etape_{vue_courante}"]
                noms_points = points_par_vue[vue_courante]["noms"]
                total_points = points_par_vue[vue_courante]["total"]

                # Redimensionnement pour l'affichage
                h_orig, w_orig = img.shape[:2]
                max_display = 600
                if w_orig > max_display:
                    scale = max_display / w_orig
                    display_w = max_display
                    display_h = int(h_orig * scale)
                    img_display = cv2.resize(img, (display_w, display_h))
                else:
                    img_display = img
                    display_w, display_h = w_orig, h_orig
                img_rgb = cv2.cvtColor(img_display, cv2.COLOR_BGR2RGB)

                if etape < total_points:
                    st.write(f"**Étape {etape+1}/{total_points}** : cliquez sur **{noms_points[etape]}**")
                else:
                    st.success("Tous les points pour cette vue ont été collectés.")

                coord = streamlit_image_coordinates(img_rgb, key=f"coord_{vue_courante}")
                if coord:
                    x_display, y_display = coord["x"], coord["y"]
                    x_orig = int(x_display * w_orig / display_w)
                    y_orig = int(y_display * h_orig / display_h)

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Valider ce point", key=f"valider_{vue_courante}_{etape}"):
                            points_clic.append((x_orig, y_orig))
                            if etape < total_points - 1:
                                st.session_state[f"etape_{vue_courante}"] = etape + 1
                            else:
                                st.session_state[f"etape_{vue_courante}"] = total_points
                            st.rerun()
                    with col2:
                        if st.button("⬅️ Annuler dernier point", key=f"annuler_{vue_courante}"):
                            if points_clic:
                                points_clic.pop()
                                if etape > 0:
                                    st.session_state[f"etape_{vue_courante}"] = etape - 1
                            st.rerun()

                if points_clic:
                    st.write("Points enregistrés :")
                    for i, (px, py) in enumerate(points_clic):
                        nom = noms_points[i] if i < len(noms_points) else f"Point {i+1}"
                        st.write(f"{nom}: ({px}, {py})")

                # Si la vue est terminée, on propose de passer à la suivante
                if st.session_state[f"etape_{vue_courante}"] >= total_points:
                    if st.button(f"✅ Vue {nom_vue} terminée, passer à la suivante"):
                        st.session_state.points_par_vue[vue_courante] = points_clic
                        st.session_state.etape_corps += 1
                        st.rerun()

    else:
        # Toutes les vues sont traitées, on calcule les mesures finales
        st.success("Toutes les photos ont été traitées.")
        if st.session_state.facteur_global is None:
            st.error("Facteur d'échelle non défini.")
        else:
            points_gauche = st.session_state.points_par_vue.get('gauche', [])
            points_droite = st.session_state.points_par_vue.get('droite', [])
            points_arriere = st.session_state.points_par_vue.get('arriere', [])
            points_mamelles = st.session_state.points_par_vue.get('mamelles', [])

            # On utilise le profil qui a le plus de points
            profil_points = points_gauche if len(points_gauche) >= len(points_droite) else points_droite
            facteur = st.session_state.facteur_global

            mesures = {}
            if len(profil_points) >= 7:
                hauteur_px = np.sqrt((profil_points[0][0]-profil_points[1][0])**2 + (profil_points[0][1]-profil_points[1][1])**2)
                mesures['hauteur_garrot'] = hauteur_px / facteur
                long_px = np.sqrt((profil_points[2][0]-profil_points[3][0])**2 + (profil_points[2][1]-profil_points[3][1])**2)
                mesures['longueur_corps'] = long_px / facteur
                queue_px = np.sqrt((profil_points[3][0]-profil_points[4][0])**2 + (profil_points[3][1]-profil_points[4][1])**2)
                mesures['longueur_queue'] = queue_px / facteur
                canon_px = np.sqrt((profil_points[5][0]-profil_points[6][0])**2 + (profil_points[5][1]-profil_points[6][1])**2)
                mesures['circonf_canon'] = canon_px / facteur

            if len(points_arriere) >= 4:
                bassin_px = np.sqrt((points_arriere[0][0]-points_arriere[1][0])**2 + (points_arriere[0][1]-points_arriere[1][1])**2)
                mesures['largeur_bassin'] = bassin_px / facteur
                thorax_px = np.sqrt((points_arriere[2][0]-points_arriere[3][0])**2 + (points_arriere[2][1]-points_arriere[3][1])**2)
                mesures['largeur_thorax'] = thorax_px / facteur
                profondeur_estimee = mesures['largeur_thorax'] * 0.8
                mesures['profondeur_thorax'] = profondeur_estimee
                tour_px = np.pi * np.sqrt((mesures['largeur_thorax']**2 + profondeur_estimee**2) / 2)
                mesures['tour_poitrine'] = max(40.0, tour_px)

            if len(points_mamelles) >= 6:
                long_trayon_g = np.sqrt((points_mamelles[0][0]-points_mamelles[1][0])**2 + (points_mamelles[0][1]-points_mamelles[1][1])**2) / facteur
                long_trayon_d = np.sqrt((points_mamelles[2][0]-points_mamelles[3][0])**2 + (points_mamelles[2][1]-points_mamelles[3][1])**2) / facteur
                # Bornes pour respecter les limites
                long_trayon_g = min(15.0, long_trayon_g)
                long_trayon_d = min(15.0, long_trayon_d)
                diam_trayon = (long_trayon_g + long_trayon_d) / 4
                diam_trayon = min(5.0, diam_trayon)  # ne pas dépasser 5 cm
                attache_px = np.sqrt((points_mamelles[4][0]-points_mamelles[5][0])**2 + (points_mamelles[4][1]-points_mamelles[5][1])**2) / facteur
                attache_px = min(30.0, attache_px)  # limite optionnelle
                symetrie = "Symétrique" if abs(long_trayon_g - long_trayon_d) < 0.5 else "Asymétrique"
                mesures['long_trayon_g'] = long_trayon_g
                mesures['long_trayon_d'] = long_trayon_d
                mesures['diam_trayon'] = diam_trayon
                mesures['attache'] = attache_px
                mesures['symetrie'] = symetrie

            # Mettre à jour session_state
            for k, v in mesures.items():
                st.session_state[k] = v

            st.write("Mesures calculées :")
            st.json(mesures)

            if st.button("🔄 Recommencer les photos"):
                st.session_state.etape_corps = 0
                st.session_state.photos_corps = {}
                st.session_state.points_par_vue = {}
                st.session_state.facteur_global = None
                for vue in vues_ordre:
                    if f"points_{vue}" in st.session_state:
                        del st.session_state[f"points_{vue}"]
                    if f"etape_{vue}" in st.session_state:
                        del st.session_state[f"etape_{vue}"]
                st.rerun()

    # -------------------------------------------------------------------------
    # SAISIE MANUELLE (toujours disponible, pré-remplie avec les valeurs calculées)
    # -------------------------------------------------------------------------
    st.header("📏 Saisie manuelle (sécurité)")

    col1, col2 = st.columns(2)
    with col1:
        longueur = st.number_input("Longueur corps (cm)", min_value=30.0, max_value=120.0,
                                   value=max(30.0, min(120.0, st.session_state.get('longueur_corps', 70.0))), key="longueur_corps_input")
        hauteur = st.number_input("Hauteur garrot (cm)", min_value=30.0, max_value=90.0,
                                  value=max(30.0, min(90.0, st.session_state.get('hauteur_garrot', 65.0))), key="hauteur_garrot_input")
        poitrine = st.number_input("Tour de poitrine (cm)", min_value=40.0, max_value=130.0,
                                   value=max(40.0, min(130.0, st.session_state.get('tour_poitrine', 80.0))), key="tour_poitrine_input")
        canon = st.number_input("Circonférence canon (cm)", min_value=5.0, max_value=15.0,
                                value=max(5.0, min(15.0, st.session_state.get('circonf_canon', 8.0))), key="circonf_canon_input")
    with col2:
        bassin = st.number_input("Largeur bassin (cm)", min_value=10.0, max_value=40.0,
                                 value=max(10.0, min(40.0, st.session_state.get('largeur_bassin', 20.0))), key="largeur_bassin_input")
        queue = st.number_input("Longueur queue (cm)", min_value=0.0, max_value=50.0,
                                value=st.session_state.get('longueur_queue', 20.0), key="longueur_queue_input")
        largeur_thorax = st.number_input("Largeur thorax (cm)", min_value=10.0, max_value=50.0,
                                         value=max(10.0, min(50.0, st.session_state.get('largeur_thorax', 25.0))), key="largeur_thorax_input")
        profondeur_thorax = st.number_input("Profondeur thorax (cm)", min_value=10.0, max_value=50.0,
                                            value=max(10.0, min(50.0, st.session_state.get('profondeur_thorax', 30.0))), key="profondeur_thorax_input")

    st.subheader("🥛 Mesures mamelles manuelles")
    col3, col4 = st.columns(2)
    with col3:
        long_trayon_g = st.number_input("Longueur trayon gauche (cm)", min_value=1.0, max_value=15.0,
                                        value=max(1.0, min(15.0, st.session_state.get('long_trayon_g', 5.0))), key="long_trayon_g_input")
        long_trayon_d = st.number_input("Longueur trayon droit (cm)", min_value=1.0, max_value=15.0,
                                        value=max(1.0, min(15.0, st.session_state.get('long_trayon_d', 5.0))), key="long_trayon_d_input")
        diam_trayon = st.number_input("Diamètre trayon (cm)", min_value=0.5, max_value=5.0,
                                      value=max(0.5, min(5.0, st.session_state.get('diam_trayon', 2.5))), key="diam_trayon_input")
    with col4:
        attache = st.number_input("Largeur attache (cm)", min_value=0.0, max_value=30.0,
                                  value=st.session_state.get('attache', 10.0), key="attache_input")
        symetrie = st.selectbox("Symétrie", ["Symétrique", "Asymétrique"],
                                index=0 if st.session_state.get('symetrie','Symétrique')=="Symétrique" else 1, key="symetrie_input")
        forme = st.selectbox("Forme", ["Globuleuse", "Bifide", "Poire"],
                             index=0 if st.session_state.get('forme','Globuleuse')=="Globuleuse" else 1 if st.session_state.get('forme')=="Bifide" else 2, key="forme_input")

    if st.button("🧮 Calculer les scores"):
        score_morpho = OvinScience.calcul_score_morpho(longueur, hauteur, poitrine, canon, bassin)
        score_mam = OvinScience.calcul_score_mamelle(long_trayon_g, diam_trayon, symetrie, attache, forme)
        st.metric("Score morphologique", f"{score_morpho}/100")
        st.metric("Score mamelles", f"{score_mam}/10")
        # Vous pouvez ajouter ici la sauvegarde en base avec brebis_id, par exemple :
        # if st.button("💾 Enregistrer dans la base"):
        #     db.execute(...)
       

# -----------------------------------------------------------------------------
# Les autres pages (gestion élevage, production, génomique avancée, santé, reproduction, nutrition, export, élite, IA, apprentissage)
# Sont reprises ici, mais pour des raisons de longueur, nous ne les recopions pas intégralement.
# Vous devez conserver les versions précédentes de ces pages (elles fonctionnent).
# -----------------------------------------------------------------------------

def page_gestion_elevage():
    # ... (code existant)
    st.write("Page Gestion élevage")  # placeholder, remplacez par votre code
    pass

def page_production():
    st.write("Page Production laitière")
    pass

def page_genomique_avancee():
    st.write("Page Génomique avancée")
    pass

def page_sante():
    st.write("Page Santé")
    pass

def page_reproduction():
    st.write("Page Reproduction")
    pass

def page_nutrition_avancee():
    st.write("Page Nutrition avancée")
    pass

def page_export():
    st.write("Page Export")
    pass

def page_elite():
    st.write("Page Élite")
    pass

def page_ia():
    st.write("Page IA & Data Mining")
    pass

def page_apprentissage():
    st.write("Page Apprentissage automatique")
    pass

# -----------------------------------------------------------------------------
# SIDEBAR ET MAIN
# -----------------------------------------------------------------------------
def sidebar():
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/sheep.png", width=80)
        st.title(f"🐑 {Config.APP_NAME}")
        st.caption(f"**{Config.LABORATOIRE}** v{Config.VERSION}")
        st.divider()
        
        if st.session_state.user_id:
            eleveurs = db.fetchall(
                "SELECT id, nom FROM eleveurs WHERE user_id=? ORDER BY nom",
                (st.session_state.user_id,)
            )
            eleveurs_options = {"Tous les éleveurs": None}
            eleveurs_options.update({f"{e[1]} (ID {e[0]})": e[0] for e in eleveurs})
            
            current = st.session_state.get("eleveur_id", None)
            default_index = 0
            for i, (label, eid) in enumerate(eleveurs_options.items()):
                if eid == current:
                    default_index = i
                    break
            
            selected_label = st.selectbox(
                "👨‍🌾 Éleveur actif",
                options=list(eleveurs_options.keys()),
                index=default_index,
                key="eleveur_selector"
            )
            st.session_state.eleveur_id = eleveurs_options[selected_label]
            st.divider()
            
            menu = st.radio(
                "Navigation",
                ["📊 Tableau de bord", 
                 "🐑 Gestion élevage",
                 "🧬 Génomique NCBI", 
                 "🥩 Composition", 
                 "📸 Photogrammétrie", 
                 "🔮 Prédictions", 
                 "🌾 Nutrition avancée",
                 "🥛 Production laitière",
                 "🧬 Génomique avancée",
                 "🏥 Santé",
                 "🤰 Reproduction",
                 "📤 Export données",
                 "🏆 Élite et comparaison",
                 "🧠 IA & Data Mining",
                 "🧠 Apprentissage automatique",
                 "🚪 Déconnexion"],
                label_visibility="collapsed"
            )
            
            st.divider()
            
            if st.button("💾 Sauvegarde rapide", use_container_width=True):
                st.download_button(
                    label="Télécharger JSON",
                    data=json.dumps({"user_id": st.session_state.user_id, "date": datetime.now().isoformat()}),
                    file_name=f"ovin_backup_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            
            page_map = {
                "📊 Tableau de bord": "dashboard",
                "🐑 Gestion élevage": "gestion_elevage",
                "🧬 Génomique NCBI": "genomique",
                "🥩 Composition": "composition",
                "📸 Photogrammétrie": "analyse",
                "🔮 Prédictions": "prediction",
                "🌾 Nutrition avancée": "nutrition_avancee",
                "🥛 Production laitière": "production",
                "🧬 Génomique avancée": "genomique_avancee",
                "🏥 Santé": "sante",
                "🤰 Reproduction": "reproduction",
                "📤 Export données": "export",
                "🏆 Élite et comparaison": "elite",
                "🧠 IA & Data Mining": "ia",
                "🧠 Apprentissage automatique": "apprentissage",
                "🚪 Déconnexion": "logout"
            }
            
            selected_page = page_map.get(menu, "dashboard")
            
            if selected_page == "logout":
                st.session_state.user_id = None
                st.session_state.current_page = "login"
                st.rerun()
            elif selected_page != st.session_state.current_page:
                st.session_state.current_page = selected_page
                st.rerun()

def main():
    sidebar()
    
    if st.session_state.current_page == "login":
        page_login()
    elif st.session_state.current_page == "dashboard":
        page_dashboard()
    elif st.session_state.current_page == "genomique":
        page_genomique()
    elif st.session_state.current_page == "composition":
        page_composition()
    elif st.session_state.current_page == "analyse":
        page_analyse()
    elif st.session_state.current_page == "prediction":
        page_prediction()
    elif st.session_state.current_page == "nutrition_avancee":
        page_nutrition_avancee()
    elif st.session_state.current_page == "production":
        page_production()
    elif st.session_state.current_page == "genomique_avancee":
        page_genomique_avancee()
    elif st.session_state.current_page == "gestion_elevage":
        page_gestion_elevage()
    elif st.session_state.current_page == "sante":
        page_sante()
    elif st.session_state.current_page == "reproduction":
        page_reproduction()
    elif st.session_state.current_page == "export":
        page_export()
    elif st.session_state.current_page == "elite":
        page_elite()
    elif st.session_state.current_page == "ia":
        page_ia()
    elif st.session_state.current_page == "apprentissage":
        page_apprentissage()

# -----------------------------------------------------------------------------
# POINT D'ENTRÉE
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    db = get_database()
    genomic_analyzer = GenomicAnalyzer()
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
        st.session_state.current_page = "login"
        st.session_state.eleveur_id = None
    
    st.set_page_config(
        page_title="Ovin Manager Pro",
        page_icon="🐑",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #2E7D32;
            text-align: center;
        }
        .sub-header {
            font-size: 1.2rem;
            color: #666;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        .gene-card {
            background-color: #e3f2fd;
            border-left: 5px solid #00838F;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .meat-card {
            background-color: #fff3e0;
            border-left: 5px solid #FF6F00;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    main()
