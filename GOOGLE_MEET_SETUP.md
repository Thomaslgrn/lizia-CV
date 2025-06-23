# 🔧 Configuration Google Meet - Extracteur de CV

Ce guide vous explique comment configurer l'intégration Google Meet pour créer automatiquement des liens de visioconférence.

## 📋 Prérequis

1. **Compte Google** avec accès à Google Calendar
2. **Projet Google Cloud** avec API Calendar activée
3. **Clé API** ou **fichier de credentials de service**

## 🚀 Configuration étape par étape

### 1. Créer un projet Google Cloud

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Activez la facturation (requis pour les API)

### 2. Activer l'API Google Calendar

1. Dans la console Google Cloud, allez dans "APIs & Services" > "Library"
2. Recherchez "Google Calendar API"
3. Cliquez sur "Enable"

### 3. Créer des credentials

#### Option A : Clé API simple (recommandée pour les tests)

1. Allez dans "APIs & Services" > "Credentials"
2. Cliquez sur "Create Credentials" > "API Key"
3. Copiez la clé API générée
4. (Optionnel) Restreignez la clé à l'API Calendar

#### Option B : Fichier de credentials de service (recommandée pour la production)

1. Allez dans "APIs & Services" > "Credentials"
2. Cliquez sur "Create Credentials" > "Service Account"
3. Remplissez les informations du compte de service
4. Cliquez sur "Create and Continue"
5. Dans "Grant this service account access to project", sélectionnez "Editor"
6. Cliquez sur "Done"
7. Cliquez sur le compte de service créé
8. Allez dans l'onglet "Keys"
9. Cliquez sur "Add Key" > "Create new key"
10. Sélectionnez "JSON" et téléchargez le fichier

### 4. Configurer les permissions Google Calendar

#### Pour la clé API simple :
- Aucune configuration supplémentaire requise
- Les liens Meet seront créés dans le calendrier principal de l'utilisateur

#### Pour le compte de service :
1. Partagez votre calendrier principal avec l'email du compte de service
2. Donnez les permissions "Make changes to events"

## 🔑 Utilisation dans l'application

### Avec une clé API :

1. Lancez l'application
2. Dans la section "Configuration Google Meet"
3. Collez votre clé API dans le champ "Clé API Google"
4. L'application créera automatiquement des liens Meet réels

### Avec un fichier de credentials :

1. Placez le fichier JSON dans le répertoire du projet
2. Modifiez le code pour utiliser le fichier de credentials
3. L'application utilisera le compte de service

## 📝 Exemple de configuration

```python
# Dans app.py, modifiez la fonction create_google_meet_link :

def create_google_meet_link(api_key, meeting_title, start_time, duration_minutes=60):
    if api_key:
        # Utilisation de la clé API
        service = create_google_calendar_service(api_key=api_key)
    else:
        # Utilisation du fichier de credentials
        service = create_google_calendar_service(credentials_file="path/to/credentials.json")
    
    if service:
        return create_google_meet_event(service, meeting_title, start_time, duration_minutes)
    else:
        return generate_visio_link()  # Fallback
```

## 🔒 Sécurité

### Bonnes pratiques :

1. **Ne committez jamais** votre clé API ou fichier de credentials
2. **Utilisez des variables d'environnement** pour les clés sensibles
3. **Restreignez les permissions** de votre clé API
4. **Surveillez l'utilisation** de votre API

### Variables d'environnement :

```bash
# Ajoutez dans votre .env ou variables d'environnement
GOOGLE_API_KEY=AIzaSyC7AFo-fPwQqLDk-4s32W9Bo4uFxL3MjQA
GOOGLE_CREDENTIALS_FILE=path/to/credentials.json
```

## 🐛 Dépannage

### Erreur "API not enabled"
- Vérifiez que l'API Google Calendar est activée dans votre projet

### Erreur "Invalid credentials"
- Vérifiez que votre clé API est correcte
- Assurez-vous que les permissions sont suffisantes

### Erreur "Calendar access denied"
- Vérifiez que le calendrier est partagé avec le compte de service
- Assurez-vous que les permissions sont correctes

### Lien Meet non créé
- Vérifiez que Google Meet est activé dans votre organisation
- Assurez-vous que l'utilisateur a les permissions pour créer des réunions

## 📊 Limites et quotas

- **Quota gratuit** : 10,000 requêtes par jour
- **Limite de rate** : 1,000 requêtes par 100 secondes
- **Création de réunions** : Limité par les permissions de votre compte

## 🔄 Mise à jour

Pour mettre à jour la configuration :

1. Modifiez les credentials si nécessaire
2. Redémarrez l'application
3. Testez la création d'un lien Meet

## 📞 Support

En cas de problème :
1. Vérifiez les logs de l'application
2. Consultez la documentation Google Calendar API
3. Contactez l'équipe de développement

---

*Configuration Google Meet pour l'Extracteur de CV - Lizia* 