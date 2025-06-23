# 📄 Extracteur Automatique de CV - Lizia

Application Streamlit pour automatiser l'extraction d'informations depuis des CVs et planifier des entretiens avec intégration Google Meet via OAuth 2.0.

## 🚀 Fonctionnalités

### 📋 Extraction automatique
- **Emails** : Détection automatique des adresses email
- **Téléphones** : Extraction des numéros de téléphone (format français)
- **Type de contrat** : Détection automatique (CDI, CDD, Stage, Alternance, etc.)
- **Durée** : Identification de la durée mentionnée dans le CV

### 🎯 Planification d'entretiens
- **Calendrier interactif** : Sélection de date avec validation des jours ouvrables
- **Créneaux horaires** : 9h à 20h, toutes les 15 minutes
- **Intégration Google Meet** : Création automatique de liens Visio réels via OAuth 2.0
- **Synchronisation calendrier** : Vérification des créneaux disponibles

### 💬 Génération de messages
- **Messages automatiques** : Génération de messages personnalisés pour les candidats
- **Messages d'entretien** : Incluant les détails de l'entretien et le lien Visio
- **Personnalisation** : Adaptation selon le type de contrat et la durée

### 📊 Export et sauvegarde
- **Export CSV** : Sauvegarde des données extraites
- **Export entretiens** : Liste des entretiens planifiés
- **Interface intuitive** : Correction manuelle des données extraites

## 🔐 Configuration OAuth 2.0

L'application utilise OAuth 2.0 pour l'intégration Google Meet, offrant un accès sécurisé et complet au calendrier Google.

### Configuration requise

1. **Projet Google Cloud** avec API Calendar activée
2. **Application OAuth 2.0** configurée
3. **Client ID et Client Secret** Google

### Guide de configuration

Consultez le fichier `OAUTH2_SETUP.md` pour la configuration détaillée.

### Configuration rapide

1. Modifiez `app.py` :
```python
GOOGLE_CLIENT_ID = "votre_client_id_ici"
GOOGLE_CLIENT_SECRET = "votre_client_secret_ici"
```

2. Ou utilisez des variables d'environnement :
```bash
export GOOGLE_CLIENT_ID="votre_client_id"
export GOOGLE_CLIENT_SECRET="votre_client_secret"
```

## 📦 Installation

### Prérequis
- Python 3.8+
- Compte Google avec accès à Google Calendar

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Dépendances principales
- `streamlit` : Interface utilisateur
- `pdfplumber` : Extraction de texte PDF
- `python-docx` : Extraction de texte DOCX
- `google-auth-oauthlib` : Authentification OAuth 2.0
- `google-api-python-client` : API Google Calendar

## 🚀 Lancement

```bash
streamlit run app.py
```

L'application sera accessible sur `http://localhost:8501`

## 📖 Utilisation

### 1. Upload du CV
- Glissez-déposez ou sélectionnez un fichier PDF ou DOCX
- L'application extrait automatiquement le texte

### 2. Vérification des données
- Les informations sont extraites automatiquement
- Corrigez manuellement si nécessaire
- Complétez les champs manquants

### 3. Planification d'entretien
- Sélectionnez une date dans le calendrier
- Choisissez un créneau horaire disponible
- L'application crée automatiquement un lien Google Meet

### 4. Génération de messages
- Générez un message automatique pour le candidat
- Incluant les détails de l'entretien et le lien Visio

### 5. Export
- Sauvegardez les données en CSV
- Exportez la liste des entretiens planifiés

## 🔧 Configuration avancée

### Personnalisation des créneaux
Modifiez la fonction `get_available_hours()` dans `app.py` :
```python
def get_available_hours():
    # Personnalisez les heures disponibles
    hours = []
    for hour in range(9, 21):  # 9h à 20h
        for minute in [0, 15, 30, 45]:  # Toutes les 15 minutes
            time_str = f"{hour:02d}:{minute:02d}"
            hours.append(time_str)
    return hours
```

### Modification des patterns de détection
Ajustez les expressions régulières dans les fonctions d'extraction :
```python
def extract_phone(text):
    # Ajoutez vos patterns personnalisés
    phone_patterns = [
        r'(\+33|0)[1-9](\d{8})',
        # Vos patterns...
    ]
```

## 🔒 Sécurité

### OAuth 2.0
- Authentification sécurisée via Google
- Tokens stockés localement dans `token.pickle`
- Renouvellement automatique des tokens
- Accès limité aux scopes nécessaires

### Bonnes pratiques
- Ne committez jamais vos credentials
- Utilisez des variables d'environnement
- Surveillez l'utilisation dans Google Cloud Console
- Supprimez régulièrement les tokens expirés

## 🐛 Dépannage

### Problèmes d'authentification OAuth
1. Vérifiez la configuration dans Google Cloud Console
2. Supprimez le fichier `token.pickle` et réauthentifiez-vous
3. Vérifiez que l'API Calendar est activée

### Erreurs d'extraction
1. Vérifiez le format du fichier (PDF/DOCX)
2. Assurez-vous que le texte est bien extrait
3. Ajustez les patterns regex si nécessaire

### Problèmes de port
1. Changez le port dans `GOOGLE_REDIRECT_URI`
2. Vérifiez qu'aucune autre application n'utilise le port 8501

## 📊 Fonctionnalités techniques

### Extraction de texte
- **PDF** : Utilisation de `pdfplumber` pour l'extraction
- **DOCX** : Utilisation de `python-docx` pour l'extraction
- **Fallback** : Gestion des erreurs d'extraction

### Intégration Google
- **OAuth 2.0** : Authentification sécurisée
- **Calendar API** : Création d'événements et récupération de créneaux
- **Meet API** : Génération automatique de liens Visio

### Interface utilisateur
- **Streamlit** : Interface moderne et responsive
- **Validation** : Vérification des données saisies
- **Feedback** : Messages d'information et d'erreur

## 🔮 Améliorations futures

- [ ] Interface d'authentification OAuth intégrée
- [ ] Gestion multi-comptes Google
- [ ] Synchronisation bidirectionnelle calendrier
- [ ] Notifications push pour les entretiens
- [ ] Support d'autres formats de CV
- [ ] Intégration avec d'autres outils de visioconférence

## 📞 Support

Pour toute question ou problème :
1. Consultez le guide de configuration OAuth 2.0
2. Vérifiez les logs de l'application
3. Contactez l'équipe de développement

---

*Développé avec ❤️ par l'équipe Lizia* 