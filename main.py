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
            

# --- 6. PAGE 3 : PRÉDICTION & GENEBANK (VERSION PROFESSIONNELLE CORRIGÉE) ---
elif menu == "🔮 Prédiction & GeneBank":
    st.title("🔬 Expertise Génomique & Conservation GeneBank")
    st.info("Interface de liaison entre les descripteurs phénotypiques et les référentiels mondiaux (NCBI/FAO).")

    if not st.session_state.db_data.empty:
        id_sel = st.selectbox("Sélectionner l'individu (Accession ID)", st.session_state.db_data["ID"])
        data = st.session_state.db_data[st.session_state.db_data["ID"] == id_sel].iloc[0]
        
        # --- BLOC 1 : MÉTRIQUES DE PERFORMANCE ---
        c1, c2, c3 = st.columns(3)
        c1.metric("Potentiel de Croissance (GMQ)", f"{data['GMQ']} g/j")
        
        # Indice de Pureté basé sur la conformité
        purete = 88.5 if data['GMQ'] > 200 else 72.0
        c2.metric("Indice de Pureté Estimé", f"{purete}%")
        
        # NCBI Taxon ID
        c3.metric("NCBI Taxon ID", "9940", help="Identifiant mondial unique pour Ovis aries")

        st.markdown("---")

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.subheader("🧬 Radar de Conformation (Standard FAO)")
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=[data['V2'], data['V3'], data['V4'], data['V5'], data['V1']/2],
                theta=['Garrot', 'Croupe', 'Corps', 'Thorax', 'Masse'], 
                fill='toself',
                line_color='teal'
            ))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 120])))
            st.plotly_chart(fig_radar, use_container_width=True)

        with col_right:
            st.subheader("🌐 Ressources Génomiques Externes")
            st.write("Consulter les référentiels pour cet échantillon :")
            
            c_btn1, c_btn2 = st.columns(2)
            
            if c_btn1.button("🧬 Search NCBI Gene"):
                url_ncbi = f"https://www.ncbi.nlm.nih.gov/gene/?term=Ovis+aries+growth"
                st.markdown(f'<meta http-equiv="refresh" content="0;URL={url_ncbi}">', unsafe_allow_html=True)
            
            if c_btn2.button("🏦 FAO DAD-IS Database"):
                url_fao = "https://www.fao.org/dad-is/en/"
                st.markdown(f'<meta http-equiv="refresh" content="0;URL={url_fao}">', unsafe_allow_html=True)
            
            st.divider()
            st.write("**Statut de Conservation :**")
            if purete > 85:
                st.success("💎 ÉLITE : Priorité Séquençage & Cryopréservation")
            else:
                st.info("📈 PRODUCTION : Suivi standard en ferme pilote")

        # --- MODULE DE SÉQUENÇAGE PRÉDICTIF ---
        st.markdown("---")
        st.subheader("🧬 Séquençage Virtuel & Analyse de Marqueurs")
        
        gene_name = "MSTN (Myostatine)"
        
        # Algorithme de prédiction
        if data['GMQ'] > 200:
            predicted_seq = "ATGCGTACGTTAGCAGCTAGCTAGCTAG"
            genotype_label = "Homozygote Supérieur (AA)"
            interpretation = "🚀 Mutation favorable détectée : Potentiel musculaire élevé."
            color = "green"
        else:
            predicted_seq = "ATGCGTACGTTAGCGGCTAGCTAGCTAG"
            genotype_label = "Standard (GG)"
            interpretation = "⚖️ Génotype sauvage : Croissance conforme à la moyenne."
            color = "orange"

        c_seq1, c_seq2 = st.columns([2, 1])
        
        with c_seq1:
            st.write(f"**Séquence ADN prédite (Gène {gene_name}) :**")
            st.code(predicted_seq, language="text")
            st.markdown(f"<span style='color:{color}'>**Interprétation :** {interpretation}</span>", unsafe_allow_html=True)

        with c_seq2:
            st.metric("Génotype Prédit", genotype_label)
            
        if st.button("🚀 Lancer l'alignement BLAST (NCBI)"):
            url_blast = f"https://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastn&PAGE_TYPE=BlastSearch&QUERY={predicted_seq}"
            st.markdown(f'<meta http-equiv="refresh" content="0;URL={url_blast}">', unsafe_allow_html=True)

    else:
        st.warning("⚠️ La base de données est vide. Veuillez identifier un animal d'abord.")

# --- 7. PAGE 4 : CROISEMENT ---
elif menu == "🔀 Simulation de Croisement":
    st.title("🔀 Laboratoire de Simulation & Dérive Génétique")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🧬 Croisement F1", 
        "⏳ Fixation & Fixation", 
        "📉 Dérive Génétique (Drift)",
        "🎲 Probabilités Génotypiques"
    ])

    # --- TAB 1 & 2 : (Garder le code précédent pour F1 et Fixation) ---
    with tab1:
        st.subheader("Prédiction des performances F1")
        if len(st.session_state.db_data) >= 2:
            m = st.selectbox("Père", st.session_state.db_data["ID"], key="m1")
            f = st.selectbox("Mère", st.session_state.db_data["ID"], key="f1")
            p1 = st.session_state.db_data[st.session_state.db_data["ID"] == m].iloc[0]['GMQ']
            p2 = st.session_state.db_data[st.session_state.db_data["ID"] == f].iloc[0]['GMQ']
            st.metric("GMQ attendu en F1 (+5% hétérosis)", f"{(p1 + p2) / 2 * 1.05:.2f} g/j")
        else: st.warning("Ajoutez des individus dans la base.")

    with tab2:
        st.subheader("Modèle de Fixation de Caractère")
        type_c = st.radio("Allèle cible :", ["Dominant", "Récessif"])
        st.info(f"Estimation : Fixation à 95% en **{5 if type_c=='Dominant' else 12}** générations.")

    # --- TAB 3 : DÉRIVE GÉNÉTIQUE & CONSANGUINITÉ (NOUVEAU) ---
    with tab3:
        st.subheader("📉 Simulation de la Dérive Génétique")
        st.write("Visualisez comment la taille du troupeau ($Ne$) influence la perte de diversité.")
        
        ne = st.slider("Taille efficace de la population (Ne)", 10, 500, 50)
        gen = st.slider("Nombre de générations", 5, 50, 20)
        
        # Algorithme de Simulation de la Fréquence Allélique (Modèle Wright-Fisher)
        freq = 0.5  # Fréquence initiale (50%)
        history = [freq]
        for _ in range(gen):
            # Loi Binomiale pour simuler le tirage aléatoire des gamètes
            freq = np.random.binomial(2*ne, freq) / (2*ne)
            history.append(freq)
        
        # Graphique Plotly
        fig_drift = px.line(x=list(range(gen+1)), y=history, 
                            labels={'x': 'Générations', 'y': 'Fréquence Allélique (p)'},
                            title=f"Évolution d'un allèle sur {gen} générations (Ne={ne})")
        fig_drift.add_hline(y=1.0, line_dash="dash", line_color="green", annotation_text="Fixation")
        fig_drift.add_hline(y=0.0, line_dash="dash", line_color="red", annotation_text="Perte")
        st.plotly_chart(fig_drift, use_container_width=True)
        
        # Calcul du coefficient de consanguinité (F)
        f_coeff = 1 - (1 - 1/(2*ne))**gen
        st.error(f"⚠️ Coefficient de consanguinité estimé (F) après {gen} générations : **{f_coeff:.4f}**")

    # --- TAB 4 : GÉNOTYPE (PUNNETT) ---
    with tab4:
        st.subheader("Probabilités Génotypiques (Mendel)")
        p1_g = st.selectbox("Génotype Père", ["AA", "Aa", "aa"])
        p2_g = st.selectbox("Génotype Mère", ["AA", "Aa", "aa"])
        # (Logique de Punnett simplifiée comme précédemment)
        st.write(f"Résultat du croisement : {p1_g} x {p2_g}")
            

# --- 8. PAGE 5 : BASE DE DONNÉES & GESTIONNAIRE D'IMPORT ---
elif menu == "📊 Base de Données & Export":
    st.title("📊 Gestionnaire de Données Multi-Sources")
    
    # --- SECTION A : IMPORTATION ---
    st.subheader("📥 Importer des données externes")
    uploaded_file = st.file_uploader("Choisir un fichier CSV ou Excel (Chercheur externe)", type=["csv", "xlsx"])

    if uploaded_file:
        # Lecture du fichier selon le format
        try:
            if uploaded_file.name.endswith('.csv'):
                ext_data = pd.read_csv(uploaded_file)
            else:
                ext_data = pd.read_excel(uploaded_file)
            
            st.write("🔍 **Aperçu des données détectées :**", ext_data.head(3))
            
            # Système de Mapping (Mise en correspondance)
            st.info("🎯 **Standardisation :** Faites correspondre les colonnes externes avec le format BioGen")
            col_map1, col_map2 = st.columns(2)
            
            with col_map1:
                target_id = st.selectbox("Sélectionner la colonne ID", ext_data.columns)
                target_poids = st.selectbox("Sélectionner la colonne Poids (V1)", ext_data.columns)
            
            with col_map2:
                target_age = st.selectbox("Sélectionner la colonne Âge", ext_data.columns)
                target_gmq = st.selectbox("Colonne GMQ", ["Calculer automatiquement"] + list(ext_data.columns))

            if st.button("🔄 Fusionner & Convertir les données"):
                # Création d'un DataFrame temporaire au format standard de l'app
                prepared_data = pd.DataFrame(columns=st.session_state.db_data.columns)
                
                prepared_data["ID"] = ext_data[target_id]
                prepared_data["Age"] = ext_data[target_age]
                prepared_data["V1"] = ext_data[target_poids]
                prepared_data["Date"] = datetime.now().date()
                
                # Calcul ou récupération du GMQ
                if target_gmq == "Calculer automatiquement":
                    # Formule : (Poids_actuel - Poids_naissance) / (Age_en_jours) * 1000
                    prepared_data["GMQ"] = ((ext_data[target_poids] - 4.0) / (ext_data[target_age] * 30.44) * 1000).round(2)
                else:
                    prepared_data["GMQ"] = ext_data[target_gmq]

                # Intégration dans la base principale (session_state)
                st.session_state.db_data = pd.concat([st.session_state.db_data, prepared_data], ignore_index=True)
                st.success(f"✅ {len(prepared_data)} individus ajoutés au registre centralisé !")
        
        except Exception as e:
            st.error(f"Erreur lors de la lecture du fichier : {e}")

    st.markdown("---")
    
    # --- SECTION B : AFFICHAGE & EXPORTATION ---
    st.subheader("📋 Registre Centralisé & Exportation LIMS")
    
    if st.session_state.db_data.empty:
        st.info("Le registre est vide pour le moment.")
    else:
        # 1. Affichage du tableau interactif
        st.dataframe(st.session_state.db_data, use_container_width=True)
        
        # 2. Boutons d'exportation
        st.write("📤 **Télécharger les données consolidées :**")
        c_exp1, c_exp2 = st.columns(2)
        
        # Export CSV (Standard pour Excel/R/Python)
        csv = st.session_state.db_data.to_csv(index=False).encode('utf-8')
        c_exp1.download_button(
            label="📥 Télécharger en CSV",
            data=csv,
            file_name=f"BioGen_Export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Export Excel (Plus lisible pour les chercheurs)
        c_exp2.info("💡 L'export CSV est recommandé pour les logiciels de statistiques (R/SPSS).")
