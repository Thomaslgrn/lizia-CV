"""
Configuration pour l'intégration Google Meet avec OAuth 2.0 adapté à Streamlit
"""

import os
import json
import pickle
import streamlit as st
from google.oauth2 import service_account
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import base64
import secrets
import random
import string
from email.mime.text import MIMEText

# Configuration des scopes nécessaires pour Google Calendar
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/gmail.send'
]

# Fichier pour stocker les tokens OAuth
TOKEN_FILE = 'google_oauth_token.pickle'

# Fichier pour stocker l'état OAuth
STATE_FILE = '.oauth_state'

def init_oauth_config():
    """Initialise la configuration OAuth dans Streamlit session state"""
    if 'oauth_config' not in st.session_state:
        st.session_state.oauth_config = {
            'client_id': "512171466562-41dvpnbkktkclpqn3r1gjbacf9bbj1sc.apps.googleusercontent.com",
            'client_secret': "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",
            'auth_uri': "https://accounts.google.com/o/oauth2/auth",
            'token_uri': "https://oauth2.googleapis.com/token",
            'redirect_uri': "http://localhost:8503",
            'scopes': SCOPES
        }

def get_stored_credentials():
    """Récupère les credentials stockés localement"""
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'rb') as token:
                credentials = pickle.load(token)
                if credentials and credentials.valid:
                    return credentials
                elif credentials and credentials.expired and credentials.refresh_token:
                    try:
                        credentials.refresh(Request())
                        # Sauvegarder les credentials rafraîchis
                        with open(TOKEN_FILE, 'wb') as token:
                            pickle.dump(credentials, token)
                        return credentials
                    except Exception as e:
                        st.warning(f"⚠️ Erreur lors du refresh du token: {e}")
        except Exception as e:
            st.warning(f"⚠️ Erreur lors du chargement du token: {e}")
    return None

def get_persistent_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return f.read().strip()
    else:
        state = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        with open(STATE_FILE, 'w') as f:
            f.write(state)
        return state

def create_oauth_url(state):
    """Crée l'URL d'authentification OAuth 2.0 avec le state fourni"""
    init_oauth_config()
    config = st.session_state.oauth_config
    auth_url = (
        f"{config['auth_uri']}?"
        f"client_id={config['client_id']}&"
        f"redirect_uri={config['redirect_uri']}&"
        f"scope={'%20'.join(config['scopes'])}&"
        f"response_type=code&"
        f"state={state}&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    return auth_url

def exchange_code_for_token(auth_code):
    """Échange le code d'autorisation contre un token"""
    import requests
    
    init_oauth_config()
    config = st.session_state.oauth_config
    
    token_data = {
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': config['redirect_uri']
    }
    
    try:
        response = requests.post(config['token_uri'], data=token_data)
        response.raise_for_status()
        
        token_info = response.json()
        
        # Créer un objet credentials compatible avec google-auth
        from google.oauth2.credentials import Credentials
        
        credentials = Credentials(
            token=token_info['access_token'],
            refresh_token=token_info.get('refresh_token'),
            token_uri=config['token_uri'],
            client_id=config['client_id'],
            client_secret=config['client_secret'],
            scopes=config['scopes']
        )
        
        # Sauvegarder les credentials
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(credentials, token)
        
        return credentials
        
    except Exception as e:
        st.error(f"❌ Erreur lors de l'échange du code: {e}")
        return None

def create_google_calendar_service(client_id=None, client_secret=None, redirect_uri=None, credentials_file=None):
    """
    Crée un service Google Calendar avec OAuth 2.0 ou Service Account
    
    Args:
        client_id: Client ID OAuth 2.0
        client_secret: Client Secret OAuth 2.0
        redirect_uri: URI de redirection OAuth 2.0
        credentials_file: Chemin vers le fichier de credentials de service
    
    Returns:
        Service Google Calendar ou None si erreur
    """
    try:
        if credentials_file and os.path.exists(credentials_file):
            # Utilisation d'un fichier de credentials de service
            credentials = service_account.Credentials.from_service_account_file(
                credentials_file, scopes=SCOPES
            )
            service = build('calendar', 'v3', credentials=credentials)
            return service
        else:
            # Utilisation d'OAuth 2.0 avec gestion Streamlit
            credentials = get_stored_credentials()
            
            if credentials:
                service = build('calendar', 'v3', credentials=credentials)
                return service
            else:
                # Pas de credentials stockés, demander l'authentification
                st.warning("⚠️ Authentification Google requise")
                return None
                
    except Exception as e:
        st.error(f"❌ Erreur lors de la création du service Google Calendar: {e}")
        return None

def handle_oauth_authentication():
    """Gère l'authentification OAuth 2.0 dans Streamlit"""
    state = get_persistent_state()

    # Vérifier si on a déjà des credentials valides
    credentials = get_stored_credentials()
    if credentials:
        st.success("✅ Authentification Google active")
        return credentials

    # Toujours utiliser le même state pour l'URL d'auth
    auth_url = create_oauth_url(state)
    st.write(f"DEBUG: State généré (avant bouton) : {state}")

    # Vérifier si on a reçu un code d'autorisation
    query_params = st.query_params
    st.write(f"DEBUG: URL complète de retour : {query_params}")
    auth_code = query_params.get('code', None)
    state_received = query_params.get('state', None)

    st.write(f"State attendu (session) : {state}")
    st.write(f"State reçu (URL) : {state_received}")

    if auth_code and state_received:
        if state_received == state:
            st.info("🔄 Échange du code d'autorisation...")
            credentials = exchange_code_for_token(auth_code)
            if credentials:
                st.success("✅ Authentification réussie !")
                st.query_params.clear()
                if os.path.exists(STATE_FILE):
                    os.remove(STATE_FILE)
                return credentials
            else:
                st.error("❌ Échec de l'authentification")
        else:
            st.error("❌ State invalide")
        return None

    # Redirection immédiate lors du clic sur le bouton
    if st.button("🔐 Se connecter avec Google"):
        st.write(f'<meta http-equiv="refresh" content="0;URL={auth_url}">', unsafe_allow_html=True)
        st.stop()

    st.warning("🔐 Authentification Google requise pour utiliser Google Meet")
    st.info("💡 Cliquez sur le bouton ci-dessus pour vous authentifier avec Google")
    return None

def create_google_meet_event(service, meeting_title, start_time, duration_minutes=60, timezone='Europe/Paris'):
    """
    Crée un événement Google Calendar avec lien Meet
    
    Args:
        service: Service Google Calendar
        meeting_title: Titre de la réunion
        start_time: Heure de début (format: "YYYY-MM-DD HH:MM")
        duration_minutes: Durée en minutes
        timezone: Fuseau horaire
    
    Returns:
        Lien Meet ou None si erreur
    """
    try:
        # Parser la date et heure
        start_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        
        # Format pour l'API Google Calendar (sans 'Z', on précise le timeZone)
        start_time_rfc = start_datetime.isoformat()
        end_time_rfc = end_datetime.isoformat()
        
        # Créer l'événement
        event = {
            'summary': meeting_title,
            'start': {
                'dateTime': start_time_rfc,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time_rfc,
                'timeZone': timezone,
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meet-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            }
        }
        
        # Insérer l'événement
        event = service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1
        ).execute()
        
        # Extraire le lien Meet
        if 'conferenceData' in event and 'entryPoints' in event['conferenceData']:
            for entry_point in event['conferenceData']['entryPoints']:
                if entry_point['entryPointType'] == 'video':
                    return entry_point['uri']
        
        return None
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la création de l'événement Meet: {e}")
        return None

def get_available_slots(service, date, start_hour=9, end_hour=20):
    """
    Récupère les créneaux disponibles pour une date donnée
    
    Args:
        service: Service Google Calendar
        date: Date au format YYYY-MM-DD
        start_hour: Heure de début (défaut: 9)
        end_hour: Heure de fin (défaut: 20)
    
    Returns:
        Liste des créneaux disponibles
    """
    try:
        # Créer la plage de temps pour la journée
        start_date = f"{date}T00:00:00Z"
        end_date = f"{date}T23:59:59Z"
        
        # Récupérer les événements existants
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_date,
            timeMax=end_date,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Créer tous les créneaux possibles
        all_slots = []
        for hour in range(start_hour, end_hour):
            for minute in [0, 15, 30, 45]:
                slot_time = f"{hour:02d}:{minute:02d}"
                all_slots.append(slot_time)
        
        # Filtrer les créneaux occupés
        available_slots = all_slots.copy()
        
        for event in events:
            if 'start' in event and 'dateTime' in event['start']:
                event_start = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00')).replace(tzinfo=None)
                event_end = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00')).replace(tzinfo=None)
                
                # Supprimer les créneaux qui chevauchent cet événement
                for slot in all_slots:
                    slot_hour, slot_minute = map(int, slot.split(':'))
                    slot_datetime = datetime.strptime(f"{date} {slot_hour:02d}:{slot_minute:02d}", "%Y-%m-%d %H:%M")
                    
                    if slot_datetime < event_end and slot_datetime + timedelta(minutes=15) > event_start:
                        if slot in available_slots:
                            available_slots.remove(slot)
        
        return available_slots
        
    except Exception as e:
        st.error(f"❌ Erreur lors de la récupération des créneaux: {e}")
        return []

def clear_oauth_tokens():
    """
    Supprime les tokens OAuth stockés
    """
    try:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
            st.success("✅ Tokens OAuth supprimés")
            # Nettoyer la session state
            if 'oauth_state' in st.session_state:
                del st.session_state.oauth_state
    except Exception as e:
        st.error(f"❌ Erreur lors de la suppression des tokens: {e}")

def check_oauth_status():
    """Vérifie le statut de l'authentification OAuth"""
    credentials = get_stored_credentials()
    if credentials:
        return True, "✅ Authentification Google active"
    else:
        return False, "❌ Authentification Google requise"

# Configuration par défaut
DEFAULT_TIMEZONE = 'Europe/Paris'
DEFAULT_CALENDAR_ID = 'primary'

def send_gmail_message(service, to, subject, body, sender=None):
    """
    Envoie un email via l'API Gmail
    Args:
        service: service Gmail authentifié
        to: destinataire
        subject: sujet
        body: corps du message
        sender: adresse de l'expéditeur (optionnel)
    Returns:
        True si succès, False sinon
    """
    try:
        message = MIMEText(body, "plain", "utf-8")
        message["to"] = to
        message["subject"] = subject
        if sender:
            message["from"] = sender
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        message_body = {"raw": raw}
        sent_message = service.users().messages().send(userId="me", body=message_body).execute()
        return True
    except Exception as e:
        import streamlit as st
        import traceback
        st.error(f"❌ Erreur lors de l'envoi de l'email : {e}")
        st.exception(e)
        st.text(traceback.format_exc())
        return False

def create_gmail_service():
    credentials = get_stored_credentials()
    if credentials:
        return build('gmail', 'v1', credentials=credentials)
    else:
        import streamlit as st
        st.error("❌ Authentification Google requise pour Gmail")
        return None 