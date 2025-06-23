import streamlit as st
import pdfplumber
import docx
import re
import pandas as pd
from io import BytesIO
import tempfile
import os
from datetime import datetime, timedelta
import uuid
import json

# Import de la configuration Google Meet
try:
    from google_meet_config import (
        create_google_calendar_service, 
        create_google_meet_event, 
        get_available_slots,
        handle_oauth_authentication,
        check_oauth_status,
        clear_oauth_tokens,
        send_gmail_message,
        create_gmail_service
    )
    GOOGLE_MEET_AVAILABLE = True
except ImportError:
    GOOGLE_MEET_AVAILABLE = False
    st.warning("⚠️ Module Google Meet non disponible. Installation des dépendances requise.")

# Configuration de la page
st.set_page_config(
    page_title="Extracteur de CV - Lizia",
    page_icon="📄",
    layout="wide"
)

# Titre de l'application
st.title("📄 Extracteur Automatique de CV")
st.markdown("---")

# Affichage du bouton Se déconnecter en haut de page (plus de sidebar)
if GOOGLE_MEET_AVAILABLE:
    is_authenticated, status_message = check_oauth_status()
    if is_authenticated:
        st.success(status_message)
        if st.button("🔓 Se déconnecter"):
            clear_oauth_tokens()
            st.rerun()
    else:
        st.warning(status_message)
        credentials = handle_oauth_authentication()
        if credentials:
            st.rerun()

def extract_text_from_pdf(pdf_file):
    """Extrait le texte d'un fichier PDF"""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Erreur lors de la lecture du PDF: {e}")
        return ""

def extract_text_from_docx(docx_file):
    """Extrait le texte d'un fichier DOCX"""
    try:
        doc = docx.Document(docx_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        st.error(f"Erreur lors de la lecture du DOCX: {e}")
        return ""

def extract_email(text):
    """Extrait l'adresse email du texte"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else ""

def extract_phone(text):
    """Extrait le numéro de téléphone du texte"""
    # Patterns pour différents formats de téléphone
    phone_patterns = [
        r'(\+33|0)[1-9](\d{8})',  # Format français
        r'(\+33|0)[1-9][\s.-]?(\d{2}[\s.-]?){4}',  # Avec espaces/points/tirets
        r'(\+33|0)[1-9][\s.-]?(\d{2}[\s.-]?){3}\d{2}',  # Format alternatif
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        if phones:
            # Nettoyer et formater le numéro
            phone = ''.join(phones[0])
            phone = re.sub(r'[\s.-]', '', phone)
            if phone.startswith('0'):
                phone = '+33' + phone[1:]
            return phone
    
    return ""

def detect_contract_type(text):
    """Détecte le type de contrat dans le texte"""
    text_lower = text.lower()
    
    contract_keywords = {
        'Alternance': ['alternance', 'apprentissage', 'contrat d\'apprentissage'],
        'Stage': ['stage', 'internship', 'stagiare'],
        'CDI': ['cdi', 'contrat à durée indéterminée', 'permanent'],
        'CDD': ['cdd', 'contrat à durée déterminée', 'temporaire', 'mission'],
        'Freelance': ['freelance', 'freelancer', 'indépendant', 'consultant'],
        'Intérim': ['intérim', 'interim', 'temporaire']
    }
    
    for contract_type, keywords in contract_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return contract_type
    
    return "À compléter"

def extract_duration(text):
    """Extrait la durée mentionnée dans le texte"""
    duration_patterns = [
        r'(\d+)\s*(mois|month)',  # 6 mois, 3 months
        r'(\d+)\s*(semaines?|weeks?)',  # 2 semaines, 1 week
        r'(\d+)\s*(jours?|days?)',  # 5 jours, 3 days
        r'(\d+)\s*(ans?|years?)',  # 2 ans, 1 year
    ]
    
    text_lower = text.lower()
    for pattern in duration_patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            number, unit = matches[0]
            return f"{number} {unit}"
    
    return "À compléter"

def generate_message(email, contract_type, duration):
    """Génère un message automatique"""
    if contract_type == "À compléter":
        contract_phrase = "un poste"
    else:
        contract_phrase = f"un poste en {contract_type}"
    
    message = f"""Bonjour,

Merci pour votre candidature. Nous avons bien reçu votre CV pour {contract_phrase}."""
    
    
    
    message += """

Nous reviendrons vers vous sous peu.

Cordialement,
L'équipe RH"""
    
    return message

def generate_interview_message(email, contract_type, interview_date, interview_time, visio_link, interviewer_name="Marie Dupont"):
    """Génère un message pour un entretien avec lien Visio"""
    if contract_type == "À compléter":
        contract_phrase = "un poste"
    else:
        contract_phrase = f"un poste en {contract_type}"
    
    # Formatage de la date
    date_obj = datetime.strptime(interview_date, "%Y-%m-%d")
    formatted_date = date_obj.strftime("%d/%m/%Y")
    
    message = f"""Bonjour,

Merci pour votre candidature pour {contract_phrase}.

Nous avons le plaisir de vous convier à un entretien :
📅 Date : {formatted_date}
🕐 Heure : {interview_time}
👤 Avec : {interviewer_name}

🔗 Lien Visio : {visio_link}

En cas d'impossibilité, merci de nous contacter au plus vite.

Cordialement,
L'équipe RH"""
    
    return message

def generate_visio_link():
    """Génère un lien Visio fictif (fallback)"""
    meeting_id = str(uuid.uuid4())[:8]
    return f"https://meet.google.com/{meeting_id}"

def create_google_meet_link(meeting_title, start_time, duration_minutes=60):
    """
    Crée un lien Google Meet via OAuth 2.0
    """
    if not GOOGLE_MEET_AVAILABLE:
        st.warning("⚠️ Module Google Meet non disponible. Utilisation d'un lien fictif.")
        return generate_visio_link()
    
    try:
        # Créer le service Google Calendar avec OAuth 2.0
        service = create_google_calendar_service()
        
        if service:
            # Créer l'événement Meet
            meet_link = create_google_meet_event(
                service=service,
                meeting_title=meeting_title,
                start_time=start_time,
                duration_minutes=duration_minutes
            )
            
            if meet_link:
                return meet_link
            else:
                st.warning("⚠️ Impossible de créer le lien Meet. Utilisation d'un lien fictif.")
                return generate_visio_link()
        else:
            st.warning("⚠️ Impossible de se connecter à Google Calendar. Utilisation d'un lien fictif.")
            return generate_visio_link()
            
    except Exception as e:
        st.warning(f"⚠️ Erreur lors de la création du lien Google Meet: {e}")
        return generate_visio_link()

def is_working_day(date):
    """Vérifie si la date est un jour ouvrable"""
    return date.weekday() < 5  # Lundi à vendredi

def get_available_hours():
    """Retourne les heures disponibles pour les entretiens (9h à 20h, toutes les 15 minutes)"""
    hours = []
    for hour in range(9, 21):  # 9h à 20h
        for minute in [0, 15, 30, 45]:  # Toutes les 15 minutes
            time_str = f"{hour:02d}:{minute:02d}"
            hours.append(time_str)
    return hours

def get_available_slots_for_date(date):
    """Récupère les créneaux disponibles pour une date donnée via OAuth 2.0"""
    try:
        if not GOOGLE_MEET_AVAILABLE:
            return get_available_hours()
        
        # Tentative de récupération depuis Google Calendar avec OAuth 2.0
        service = create_google_calendar_service()
        
        if service:
            try:
                available_slots = get_available_slots(service, date.strftime("%Y-%m-%d"))
                if available_slots:
                    return available_slots
                else:
                    return get_available_hours()
            except Exception as e:
                # En cas d'erreur, on utilise les créneaux par défaut
                st.info("ℹ️ Utilisation des créneaux par défaut (Google Calendar non accessible)")
                return get_available_hours()
        else:
            return get_available_hours()
    except Exception as e:
        # En cas d'erreur, on utilise les créneaux par défaut
        st.info("ℹ️ Utilisation des créneaux par défaut (Google Calendar non accessible)")
        return get_available_hours()

def save_to_csv(data, filename="cv_extracted_data.csv"):
    """Sauvegarde les données dans un fichier CSV"""
    df = pd.DataFrame([data])
    return df.to_csv(index=False)

def save_interview_to_csv(data, filename="entretiens.csv"):
    """Sauvegarde les données d'entretien dans un fichier CSV"""
    df = pd.DataFrame([data])
    return df.to_csv(index=False)

# Interface principale
uploaded_file = st.file_uploader(
    "Choisissez un fichier CV (PDF ou DOCX)",
    type=['pdf', 'docx'],
    help="Formats acceptés : PDF, DOCX"
)

if uploaded_file is not None:
    # Extraction du texte
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        text = extract_text_from_pdf(uploaded_file)
    elif file_extension == 'docx':
        text = extract_text_from_docx(uploaded_file)
    else:
        st.error("Format de fichier non supporté")
        st.stop()
    
    if text:
        # Affichage du texte extrait (optionnel)
        with st.expander("📄 Texte extrait du CV"):
            st.text_area("Contenu du CV", text, height=200)
        
        # Extraction automatique des informations
        extracted_email = extract_email(text)
        extracted_phone = extract_phone(text)
        detected_contract = detect_contract_type(text)
        detected_duration = extract_duration(text)
        
        # Formulaire avec les données extraites
        st.subheader("📋 Informations extraites")
        
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input(
                "📧 Adresse e-mail",
                value=extracted_email,
                placeholder="exemple@email.com"
            )
            
            contract_type = st.selectbox(
                "📝 Type de contrat",
                options=["À compléter", "Alternance", "Stage", "CDI", "CDD", "Freelance", "Intérim"],
                index=0 if detected_contract == "À compléter" else ["À compléter", "Alternance", "Stage", "CDI", "CDD", "Freelance", "Intérim"].index(detected_contract)
            )
        
        with col2:
            phone = st.text_input(
                "📞 Numéro de téléphone",
                value=extracted_phone,
                placeholder="+33 1 23 45 67 89"
            )
            
            duration = st.text_input(
                "⏱️ Durée",
                value=detected_duration,
                placeholder="ex: 6 mois, 3 semaines"
            )
        
        # Section entretien
        st.markdown("---")
        st.subheader("🎯 Planifier un entretien")
        
        # Avant la section entretien, initialise l'état si besoin
        if 'show_plan_entretien' not in st.session_state:
            st.session_state['show_plan_entretien'] = False
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Titre de la réunion
            meeting_title = st.text_input(
                "📝 Titre de la réunion",
                value="Entretien - Marie Dupont",
                help="Titre qui apparaîtra dans Google Meet"
            )
            
            # Sélection de la date avec un calendrier
            min_date = datetime.now().date() + timedelta(days=1)
            max_date = datetime.now().date() + timedelta(days=30)
            
            selected_date = st.date_input(
                "📅 Choisir une date",
                min_value=min_date,
                max_value=max_date,
                value=min_date,
                help="Sélectionnez une date pour l'entretien (jours ouvrables uniquement)"
            )
            
            # Vérification que la date sélectionnée est un jour ouvrable
            if selected_date:
                if not is_working_day(selected_date):
                    st.warning("⚠️ Attention : La date sélectionnée n'est pas un jour ouvrable. Veuillez choisir un jour de semaine.")
            
            # Sélection de l'heure (avec créneaux disponibles)
            available_hours = get_available_slots_for_date(selected_date)
            
            selected_time = st.selectbox(
                "🕐 Choisir une heure",
                options=available_hours,
                help="Sélectionnez une heure pour l'entretien (9h à 20h, toutes les 15 minutes)"
            )
            
            # Nom de l'interviewer
            interviewer_name = st.text_input(
                "👤 Nom de l'interviewer",
                value="Marie Dupont",
                placeholder="Nom de la personne qui mènera l'entretien"
            )
        
        with col2:
            # Durée de l'entretien
            interview_duration = st.selectbox(
                "⏱️ Durée de l'entretien",
                options=["15 minutes","30 minutes", "45 minutes", "1 heure", "1h30"],
                index=2
            )
            
            # Type d'entretien
            interview_type = st.selectbox(
                "🎯 Type d'entretien",
                options=["Premier entretien", "Entretien technique", "Entretien final", "Entretien RH"]
            )
            
            # Mise à jour du titre de la réunion
            if 'interviewer_name' in locals() and 'interview_type' in locals():
                meeting_title = f"Entretien {interview_type} - {interviewer_name}"
        
        # Boutons d'action
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Générer le message et le stocker dans la session
            if st.button("💬 Message réception CV", type="primary"):
                st.session_state['msg_auto'] = generate_message(email, contract_type, duration)
                st.session_state['show_msg_auto'] = True
        
        with col2:
            if st.button("📅 Planifier entretien", type="secondary"):
                if selected_date and selected_time and email and is_working_day(selected_date):
                    # Calculer la durée en minutes
                    duration_map = {
                        "15 minutes": 15,
                        "30 minutes": 30,
                        "45 minutes": 45,
                        "1 heure": 60,
                        "1h30": 90
                    }
                    duration_minutes = duration_map.get(interview_duration, 60)
                    
                    # Générer le lien Visio (Google Meet automatiquement)
                    visio_link = create_google_meet_link(
                        meeting_title, 
                        f"{selected_date} {selected_time}",
                        duration_minutes
                    )
                    
                    # Générer le message d'entretien
                    interview_message = generate_interview_message(
                        email, contract_type, selected_date.strftime("%Y-%m-%d"), selected_time, 
                        visio_link, interviewer_name
                    )
                    st.session_state['msg_entretien'] = interview_message
                    st.session_state['show_msg_entretien'] = True
                    st.session_state['show_plan_entretien'] = True
                else:
                    if not is_working_day(selected_date):
                        st.error("❌ Veuillez sélectionner un jour ouvrable (lundi à vendredi)")
                    elif not email:
                        st.error("❌ Veuillez renseigner l'adresse email du candidat")
                    else:
                        st.error("❌ Veuillez sélectionner une date et une heure valides")
        
        with col3:
            if st.button("💾 Sauvegarder en CSV"):
                data = {
                    'Email': email,
                    'Téléphone': phone,
                    'Type de contrat': contract_type,
                    'Durée': duration,
                    'Fichier source': uploaded_file.name
                }
                
                csv = save_to_csv(data)
                st.download_button(
                    label="📥 Télécharger CSV",
                    data=csv,
                    file_name="cv_extracted_data.csv",
                    mime="text/csv"
                )
        
        with col4:
            if st.button("🔄 Réinitialiser"):
                st.rerun()

        # Affichage des messages côte à côte
        if st.session_state.get('show_msg_auto') or st.session_state.get('show_plan_entretien'):
            st.markdown("---")
            st.subheader("📝 Messages générés")
            
            # Créer deux colonnes pour les messages
            msg_col1, msg_col2 = st.columns(2)
            
            # Message de réception CV (colonne gauche)
            with msg_col1:
                if st.session_state.get('show_msg_auto') and st.session_state.get('msg_auto'):
                    st.markdown("**💬 Message de réception CV**")
                    message = st.session_state['msg_auto']
                    st.text_area("", message, height=200, key="msg_auto_display")
                    
                    col_btn1, col_btn2 = st.columns([1, 3])
                    with col_btn1:
                        st.button("📋", key="copy_msg_auto")
                    with col_btn2:
                        if GOOGLE_MEET_AVAILABLE and email:
                            if st.button("✉️ Envoyer par email", key="send_msg_auto"):
                                with st.spinner("Envoi de l'email en cours..."):
                                    service = create_gmail_service()
                                    if service:
                                        subject = "Votre candidature chez Lizia"
                                        success = send_gmail_message(service, email, subject, message)
                                        if success:
                                            st.success(f"✉️ Email envoyé à {email}")
                                        else:
                                            st.error("❌ L'envoi de l'email a échoué.")
                                    else:
                                        st.error("❌ Service Google non disponible.")
                    
                    if GOOGLE_MEET_AVAILABLE and email:
                        st.markdown(f"**📧 Email :** `{email}`")
            
            # Message d'entretien (colonne droite)
            with msg_col2:
                if st.session_state.get('show_plan_entretien') and st.session_state.get('msg_entretien'):
                    st.markdown("**📅 Message d'entretien**")
                    interview_message = st.session_state['msg_entretien']
                    st.text_area("", interview_message, height=200, key="msg_entretien_display")
                    
                    col_btn3, col_btn4 = st.columns([1, 3])
                    with col_btn3:
                        st.button("📋", key="copy_msg_entretien")
                    with col_btn4:
                        if GOOGLE_MEET_AVAILABLE and email:
                            if st.button("✉️ Envoyer par email", key="send_msg_entretien"):
                                with st.spinner("Envoi de l'email en cours..."):
                                    service = create_gmail_service()
                                    if service:
                                        subject = "Convocation à un entretien chez Lizia"
                                        success = send_gmail_message(service, email, subject, interview_message)
                                        if success:
                                            st.success(f"✉️ Email d'entretien envoyé à {email}")
                                        else:
                                            st.error("❌ L'envoi de l'email d'entretien a échoué.")
                                    else:
                                        st.error("❌ Service Google non disponible.")
                    
                    if GOOGLE_MEET_AVAILABLE and email:
                        st.markdown(f"**📧 Email :** `{email}`")
                    
                    # Bouton pour sauvegarder l'entretien
                    if st.button("💾 Sauvegarder l'entretien", key="save_entretien"):
                        interview_data = {
                            'Email': email,
                            'Téléphone': phone,
                            'Type de contrat': contract_type,
                            'Date entretien': selected_date.strftime("%Y-%m-%d"),
                            'Heure entretien': selected_time,
                            'Durée': interview_duration,
                            'Type entretien': interview_type,
                            'Interviewer': interviewer_name,
                            'Lien Visio': visio_link,
                            'Fichier source': uploaded_file.name
                        }
                        csv = save_interview_to_csv(interview_data)
                        st.download_button(
                            label="📥 Télécharger CSV entretien",
                            data=csv,
                            file_name="entretien_planifie.csv",
                            mime="text/csv"
                        )

else:
    # Page d'accueil
    st.markdown("""
    ### 🎯 Comment utiliser l'application :
    
    1. **Uploadez votre CV** : Glissez-déposez ou sélectionnez un fichier PDF ou DOCX
    2. **Vérifiez les données** : Les informations seront extraites automatiquement
    3. **Complétez si nécessaire** : Modifiez les champs vides ou incorrects
    4. **Planifiez un entretien** : Choisissez une date et une heure dans le calendrier
    5. **Générez le message** : Créez un message automatique pour le candidat
    6. **Sauvegardez** : Exportez les données en CSV si besoin
    
    ---
    
    ### 🔧 Fonctionnalités :
    - ✅ Extraction automatique d'emails et téléphones
    - ✅ Détection du type de contrat (CDI, CDD, Stage, etc.)
    - ✅ Identification de la durée mentionnée
    - ✅ Planification d'entretiens avec calendrier interactif
    - ✅ Génération automatique de liens Visio (Google Meet avec OAuth 2.0)
    - ✅ Messages automatiques personnalisés
    - ✅ Export en CSV
    - ✅ Interface intuitive et responsive
    """)
