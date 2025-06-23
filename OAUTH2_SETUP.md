# 🔐 Configuration OAuth 2.0 - Extracteur de CV

Ce guide vous explique comment configurer OAuth 2.0 pour l'intégration Google Meet dans l'application.

## 📋 Prérequis

1. **Compte Google** avec accès à Google Calendar
2. **Projet Google Cloud** avec API Calendar activée
3. **Application OAuth 2.0** configurée dans Google Cloud Console

## 🚀 Configuration étape par étape

### 1. Créer un projet Google Cloud

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Activez la facturation (requis pour les API)

### 2. Activer l'API Google Calendar

1. Dans la console Google Cloud, allez dans "APIs & Services" > "Library"
2. Recherchez "Google Calendar API"
3. Cliquez sur "Enable"

### 3. Configurer OAuth 2.0

1. Allez dans "APIs & Services" > "Credentials"
2. Cliquez sur "Create Credentials" > "OAuth client ID"
3. Si c'est la première fois, configurez l'écran de consentement OAuth :
   - **User Type** : External (ou Internal si vous avez Google Workspace)
   - **App name** : "Extracteur de CV - Lizia"
   - **User support email** : Votre email
   - **Developer contact information** : Votre email
   - **Scopes** : Ajoutez les scopes Google Calendar

4. Créez l'ID client OAuth :
   - **Application type** : Desktop application
   - **Name** : "Extracteur de CV Desktop"
   - Cliquez sur "Create"

5. Notez le **Client ID** et **Client Secret** générés

### 4. Configurer l'application

1. Modifiez le fichier `app.py` :
   ```python
   # Configuration OAuth 2.0 Google
   GOOGLE_CLIENT_ID = "votre_client_id_ici"
   GOOGLE_CLIENT_SECRET = "votre_client_secret_ici"
   GOOGLE_REDIRECT_URI = "http://localhost:8501"
   ```

2. Remplacez les valeurs par vos vraies credentials

## 🔑 Utilisation

### Première utilisation

1. Lancez l'application
2. Lors de la première planification d'entretien, l'application ouvrira automatiquement :
   - Une fenêtre de navigateur pour l'authentification Google
   - Une page de consentement OAuth
   - Une redirection vers l'application

3. Autorisez l'accès à votre Google Calendar
4. L'application créera automatiquement des liens Meet réels

### Authentification persistante

- Les tokens OAuth sont sauvegardés dans `token.pickle`
- L'authentification reste valide jusqu'à expiration
- Renouvellement automatique des tokens

## 🔒 Sécurité

### Bonnes pratiques

1. **Ne committez jamais** vos Client ID et Client Secret
2. **Utilisez des variables d'environnement** :
   ```bash
   export GOOGLE_CLIENT_ID="votre_client_id"
   export GOOGLE_CLIENT_SECRET="votre_client_secret"
   ```
3. **Restreignez les scopes** aux minimums nécessaires
4. **Surveillez l'utilisation** dans Google Cloud Console

### Variables d'environnement

Modifiez `app.py` pour utiliser les variables d'environnement :
```python
import os

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your_client_id_here")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your_client_secret_here")
```

## 🐛 Dépannage

### Erreur "Invalid client"
- Vérifiez que le Client ID et Client Secret sont corrects
- Assurez-vous que l'application OAuth est bien configurée

### Erreur "Redirect URI mismatch"
- Vérifiez que l'URI de redirection dans Google Cloud correspond à `http://localhost:8501`
- Ajoutez `http://localhost:8501/` dans les URIs autorisés

### Erreur "Access denied"
- Vérifiez que l'API Google Calendar est activée
- Assurez-vous que les scopes sont correctement configurés

### Problème de port
- Si le port 8501 est occupé, modifiez `GOOGLE_REDIRECT_URI` et le port dans le flow OAuth

## 🔄 Gestion des tokens

### Supprimer les tokens
```python
from google_meet_config import clear_oauth_tokens
clear_oauth_tokens()
```

### Renouveler l'authentification
1. Supprimez le fichier `token.pickle`
2. Relancez l'application
3. Réauthentifiez-vous

## 📊 Avantages OAuth 2.0

### vs Clé API
- **Accès complet** au calendrier utilisateur
- **Création d'événements** dans le calendrier personnel
- **Gestion des permissions** granulaire
- **Sécurité renforcée** avec authentification utilisateur

### Fonctionnalités
- **Liens Meet réels** créés automatiquement
- **Synchronisation calendrier** complète
- **Gestion des conflits** de créneaux
- **Notifications** automatiques

## 🔮 Améliorations futures

- **Interface d'authentification** intégrée dans Streamlit
- **Gestion multi-comptes** Google
- **Synchronisation bidirectionnelle** avec le calendrier
- **Notifications push** pour les entretiens

## 📞 Support

En cas de problème :
1. Vérifiez la configuration OAuth dans Google Cloud Console
2. Consultez les logs de l'application
3. Supprimez et régénérez les tokens si nécessaire
4. Contactez l'équipe de développement

---

*Configuration OAuth 2.0 pour l'Extracteur de CV - Lizia* 