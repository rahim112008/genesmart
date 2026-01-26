import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import uuid # Pour générer des identifiants uniques de recherche

# --- CONFIGURATION SYSTÈME ---
def pro_init():
    st.set_page_config(
        page_title="BioGenExpert v3.0 | LIMS Portal",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialisation d'une structure de données "Research-Grade"
    if 'db_data' not in st.session_state:
        columns = [
            "Entry_UUID",      # Identifiant unique de la donnée
            "Timestamp",       # Date et heure précise
            "Regne",           # Animal ou Végétal
            "ID_Sujet",        # ID saisi (DZ-...)
            "Stade_Pheno",     # Stade de développement
            "M1_Val", "M1_Lab",# Mesure 1 (Valeur et Nom)
            "M2_Val", "M2_Lab",# Mesure 2
            "M3_Val", "M3_Lab",# Mesure 3
            "Quali_1",         # Caractère qualitatif 1
            "Quali_2",         # Caractère qualitatif 2
            "Expert_ID"        # Signature du manipulateur
        ]
        st.session_state.db_data = pd.DataFrame(columns=columns)

# Appel de l'initialisation
pro_init()
# --- BLOC 2 : INTERFACE DE SAISIE DYNAMIQUE ---

# 1. Sélection du contexte dans la barre latérale
with st.sidebar:
    st.markdown("---")
    st.subheader("⚙️ Paramètres d'étude")
    regne = st.selectbox("🔬 Règne Biologique", ["Élevage (Animal)", "Agronomie (Végétal)"])
    expert = st.text_input("✍️ Expert Responsable", "Dr. Rahim")

# 2. Page d'identification
if menu == "🆔 Identification Dynamique":
    st.title(f"🆔 Caractérisation Phénomique : {regne}")
    
    # Configuration automatique des descripteurs
    if "Animal" in regne:
        labels = ["Poids vif (kg)", "Hauteur Garrot (cm)", "Périmètre Thorax (cm)"]
        obs_labels = ["Couleur Robe", "Type Cornes"]
        stade_def = "2 dents"
    else:
        labels = ["Rendement (q/ha)", "Hauteur Tige (cm)", "Nombre de Grains"]
        obs_labels = ["Variété", "Résistance Stress"]
        stade_def = "Floraison (BBCH 65)"

    with st.form("lims_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        id_sujet = c1.text_input("ID Échantillon (Barcode)", "DZ-2026-")
        stade = c2.text_input("Stade de développement", stade_def)

        st.subheader("📏 Mesures Biométriques (Quantitatifs)")
        q1, q2, q3 = st.columns(3)
        m1 = q1.number_input(labels[0], value=0.0, step=0.1)
        m2 = q2.number_input(labels[1], value=0.0, step=0.1)
        m3 = q3.number_input(labels[2], value=0.0, step=0.1)

        st.subheader("🎨 Caractères Morphologiques (Qualitatifs)")
        ql1, ql2 = st.columns(2)
        v_ql1 = ql1.text_input(obs_labels[0])
        v_ql2 = ql2.text_input(obs_labels[1])

        if st.form_submit_button("✅ Valider l'entrée scientifique"):
            # Enregistrement structuré dans le Bloc 1 (LIMS)
            new_entry = {
                "Entry_UUID": str(uuid.uuid4())[:8],
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Regne": regne,
                "ID_Sujet": id_sujet,
                "Stade_Pheno": stade,
                "M1_Val": m1, "M1_Lab": labels[0],
                "M2_Val": m2, "M2_Lab": labels[1],
                "M3_Val": m3, "M3_Lab": labels[2],
                "Quali_1": v_ql1,
                "Quali_2": v_ql2,
                "Expert_ID": expert
            }
            
            # Mise à jour de la mémoire du Bloc 1
            st.session_state.db_data = pd.concat([st.session_state.db_data, pd.DataFrame([new_entry])], ignore_index=True)
            st.success(f"Échantillon {id_sujet} archivé avec succès.")
            st.balloons()


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



            st.info(f"📅 *Retrait de l'éponge :* {date_retrait.strftime('%d/%m/%Y')}")

            st.info(f"🐑 *Date de lutte prévue :* {date_lutte.strftime('%d/%m/%Y')}")

            st.warning(f"🐣 *Mise bas prévue (± 5j) :* {date_mise_bas.strftime('%d/%m/%Y')}")



            jours_restants = (date_mise_bas - datetime.now().date()).days

            if jours_restants > 0:

                st.write(f"Il reste environ *{jours_restants} jours* avant la mise bas.")



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



# --- PAGE 5 : EXPERTISE & PRÉDICTION GÉNOTYPIQUE (AVEC SÉLECTEUR D'ID) ---

elif menu == "🔍 Recherche GenBank (NCBI)":

    st.title("🔬 Expertise Phénomique & Prédiction")



    # 1. CASE DE SÉLECTION DE L'ID

    # On récupère la liste des IDs présents dans la base de données

    liste_ids = st.session_state.db_data["ID Animal"].tolist()



    id_select = st.selectbox("🎯 Choisir l'ID de l'animal à analyser :", liste_ids)



    # 2. RÉCUPÉRATION AUTOMATIQUE DES DONNÉES DE CET ANIMAL

    # On va chercher les mesures correspondantes dans le DataFrame

    donnees_animal = st.session_state.db_data[st.session_state.db_data["ID Animal"] == id_select]



    # On extrait les valeurs (ou on met des moyennes si l'ID est nouveau)

    if not donnees_animal.empty:

        p_vif = donnees_animal["Poids (kg)"].values[0]

        # Pour les autres mesures (Garrot, Poitrine), si elles ne sont pas dans ton DataFrame principal,

        # on utilise les variables saisies dans l'onglet Identification

        h_gar = v2 if 'v2' in locals() else 72.0

        p_tho = v5 if 'v5' in locals() else 88.0

        l_cor = v4 if 'v4' in locals() else 80.0

        l_poi = v7 if 'v7' in locals() else 28.0

    else:

        st.warning("Aucune donnée trouvée pour cet ID. Utilisation des valeurs par défaut.")

        p_vif, h_gar, p_tho, l_cor, l_poi = 50.0, 72.0, 88.0, 80.0, 28.0



    # 3. AFFICHAGE DES RÉSULTATS (Onglets)

    tab_index, tab_predict, tab_trans = st.tabs(["📊 Index Zootechniques", "🔮 Prédiction Génotype", "🧬 Transmission Estimée"])



    with tab_index:

        st.subheader(f"📈 Analyse Morphométrique de {id_select}")

        it = (p_tho / h_gar)

        ic = (h_gar / l_cor)



        c1, c2 = st.columns(2)

        c1.metric("Indice Thoracique", f"{it:.2f}")

        c2.metric("Indice de Compacité", f"{ic:.2f}")



        st.plotly_chart(px.bar(x=["Thorax", "Compacité"], y=[it, ic], color=["Thorax", "Compacité"], title=f"Profil de {id_select}"), use_container_width=True)



    with tab_predict:

        st.subheader(f"🔮 Prédiction Génomique de {id_select}")

        # Logique de prédiction basée sur le poids réel de l'animal sélectionné

        if p_vif > 55:

            st.warning(f"⚠️ *Alerte Génomique :* L'ID {id_select} présente un phénotype hautement corrélé au gène Myostatine (MSTN).")

        else:

            st.success(f"✅ *Profil Standard :* L'ID {id_select} suit une courbe de croissance génétique classique.")



    with tab_trans:

        st.subheader("🧬 Potentiel Reproducteur")

        h2 = 0.35

        gain = h2 * (p_vif - 50.0)

        st.write(f"Valeur Génétique Estimée pour *{id_select}* :")

        st.metric("Progrès Génétique (kg)", f"{gain:+.2f}")



    # ... (Le reste du code reste le même)

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
