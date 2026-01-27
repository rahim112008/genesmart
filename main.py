import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="BioGenExpert v6.0", layout="wide", page_icon="🧬")

# --- 2. INITIALISATION DE LA MÉMOIRE (Évite les erreurs d'écran noir) ---
if 'db_data' not in st.session_state:
    st.session_state.db_data = pd.DataFrame(columns=[
        "ID", "Age", "GMQ", "Poids", "Hauteur", "Robe", "Sante", "Date"
    ])

# --- 3. BARRE LATÉRALE ---
st.sidebar.title("🧬 Menu Expert")
st.sidebar.info("Expertise Génomique & Morphométrique")
menu = st.sidebar.radio("Navigation", [
    "🆔 Identification (30 Car.)", 
    "💉 Suivi & Reproduction",
    "📊 Base de Données & Export"
])

# --- PAGE 1 : IDENTIFICATION (LES 30 CARACTÈRES) ---
if menu == "🆔 Identification (30 Car.)":
    st.title("🆔 Caractérisation Phénotypique")
    st.markdown("---")

    # ENTÊTE : ID & AGE
    c_h1, c_h2 = st.columns([2, 1])
    with c_h1:
        id_an = st.text_input("Identifiant Unique de l'animal", "DZ-2026-001")
    with c_h2:
        age_an = st.number_input("Âge de l'animal (mois)", min_value=1, max_value=240, value=12)

    col_quant, col_qual = st.columns(2)

    with col_quant:
        st.subheader("📏 15 Caractères Quantitatifs")
        v1 = st.number_input("1. Poids vif (kg)", 5.0, 150.0, 45.0)
        v2 = st.number_input("2. Hauteur au garrot (cm)", 30.0, 110.0, 75.0)
        v3 = st.number_input("3. Hauteur à la croupe (cm)", 30.0, 110.0, 74.0)
        v4 = st.number_input("4. Longueur du corps (cm)", 30.0, 130.0, 82.0)
        v5 = st.number_input("5. Périmètre thoracique (cm)", 40.0, 150.0, 92.0)
        v6 = st.number_input("6. Largeur de la poitrine (cm)", 10.0, 50.0, 28.0)
        v7 = st.number_input("7. Largeur aux hanches (cm)", 10.0, 45.0, 24.0)
        v8 = st.number_input("8. Largeur aux trochanters (cm)", 10.0, 45.0, 22.0)
        v9 = st.number_input("9. Longueur de la tête (cm)", 10.0, 40.0, 25.0)
        v10 = st.number_input("10. Largeur du front (cm)", 5.0, 25.0, 12.0)
        v11 = st.number_input("11. Longueur des oreilles (cm)", 5.0, 35.0, 18.0)
        v12 = st.number_input("12. Longueur des cornes (cm)", 0.0, 60.0, 15.0)
        v13 = st.number_input("13. Tour du canon (cm)", 5.0, 20.0, 10.5)
        v14 = st.number_input("14. Longueur de la queue (cm)", 5.0, 60.0, 30.0)
        v15 = st.number_input("15. Profondeur de poitrine (cm)", 15.0, 60.0, 35.0)

    with col_qual:
        st.subheader("🎨 15 Caractères Qualitatifs")
        q1 = st.selectbox("16. Couleur de la robe", ["Blanc pur", "Noir", "Fauve", "Pie-rouge"])
        q2 = st.selectbox("17. Type de laine", ["Mèche longue", "Mèche courte", "Lisse", "Jarreuse"])
        q3 = st.selectbox("18. Couverture de laine", ["Totale", "Ventre nu", "Tête et pattes nues"])
        q4 = st.selectbox("19. Pigmentation muqueuses", ["Rose", "Noire", "Tachetée"])
        q5 = st.selectbox("20. Profil de la tête", ["Droit", "Busqué", "Ultra-busqué"])
        q6 = st.selectbox("21. Port des oreilles", ["Tombantes", "Semi-tombantes", "Dressées"])
        q7 = st.selectbox("22. Présence de cornes", ["Spiralées", "Rudimentaires", "Absentes"])
        q8 = st.selectbox("23. Forme des cornes", ["Prismatiques", "Rondes", "Néant"])
        q9 = st.selectbox("24. Type de queue", ["Fine", "Grasse (base)", "Semi-grasse"])
        q10 = st.selectbox("25. Ligne de dos", ["Droite", "Ensellée", "Voûtée"])
        q11 = st.selectbox("26. Inclinaison croupe", ["Horizontale", "Inclinée"])
        q12 = st.selectbox("27. Aplombs antérieurs", ["Corrects", "Panards", "Cagneux"])
        q13 = st.selectbox("28. Aplombs postérieurs", ["Corrects", "Crochus", "Ouverts"])
        q14 = st.selectbox("29. Développement fanon", ["Absent", "Réduit", "Marqué"])
        q15 = st.selectbox("30. État trayons/scrotum", ["Normal", "Asymétrique", "Anomalie"])

    st.markdown("---")

    if st.button("💾 Analyser & Enregistrer", use_container_width=True, type="primary"):
        # Calcul GMQ (Gain Moyen Quotidien)
        jours = age_an * 30.44
        gmq = (v1 - 4.0) / jours * 1000
        
        # Enregistrement
        new_row = {"ID": id_an, "Age": age_an, "GMQ": round(gmq, 2), "Poids": v1, "Hauteur": v2, "Robe": q1, "Sante": "N/A", "Date": datetime.now().date()}
        st.session_state.db_data = pd.concat([st.session_state.db_data, pd.DataFrame([new_row])], ignore_index=True)
        
        # Affichage Radar
        categories = ['H. Garrot', 'H. Croupe', 'Long. Corps', 'Périm. Thor.', 'Larg. Poitrine']
        fig = go.Figure(data=go.Scatterpolar(r=[v2, v3, v4, v5, v6], theta=categories, fill='toself', line_color='teal'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 120])), title=f"Profil de {id_an}")
        st.plotly_chart(fig, use_container_width=True)
        
        
        st.success(f"Analyse terminée : GMQ = {gmq:.1f} g/j")
        st.balloons()

# --- PAGE 2 : REPRODUCTION ---
elif menu == "💉 Suivi & Reproduction":
    st.title("💉 Gestion Sanitaire")
    col_v, col_r = st.columns(2)
    with col_v:
        st.subheader("📝 Diagnostic")
        id_v = st.text_input("ID Animal", "DZ-")
        etat = st.select_slider("Santé", options=["Mauvais", "Moyen", "Bon", "Parfait"])
        if st.button("Sauvegarder l'état"):
            st.success(f"Santé de {id_v} mise à jour.")
    with col_r:
        st.subheader("🤰 Prédiction Gestation")
        d_e = st.date_input("Date Pose Éponge", datetime.now())
        st.warning(f"Mise bas prévue : {(d_e + timedelta(days=166)).strftime('%d/%m/%Y')}")

# --- PAGE 3 : BASE DE DONNÉES & EXPORT ---
elif menu == "📊 Base de Données & Export":
    st.title("📊 Registre & Data Export")
    if st.session_state.db_data.empty:
        st.info("Aucune donnée enregistrée pour le moment.")
    else:
        st.dataframe(st.session_state.db_data, use_container_width=True)
        
        # Exportation CSV
        csv = st.session_state.db_data.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Télécharger la base (CSV)", data=csv, file_name="BioGen_Database.csv", mime="text/csv")
        
        # Graphique de synthèse
        st.subheader("📈 Évolution du GMQ par individu")
        fig_bar = go.Figure([go.Bar(x=st.session_state.db_data['ID'], y=st.session_state.db_data['GMQ'], marker_color='teal')])
        fig_bar.update_layout(title="Comparaison des performances de croissance (g/j)")
        st.plotly_chart(fig_bar, use_container_width=True)
