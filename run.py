#!/usr/bin/env python3
"""
Script de lancement pour l'application Extracteur de CV
"""

import subprocess
import sys
import os

def check_dependencies():
    """Vérifie si les dépendances sont installées"""
    try:
        import streamlit
        import pdfplumber
        import docx
        import pandas
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("💡 Installez les dépendances avec: pip install -r requirements.txt")
        return False

def main():
    """Fonction principale"""
    print("🚀 Lancement de l'Extracteur de CV - Lizia")
    print("=" * 50)
    
    # Vérifier les dépendances
    if not check_dependencies():
        sys.exit(1)
    
    print("✅ Toutes les dépendances sont installées")
    print("🌐 Lancement de l'application...")
    print("📱 L'application s'ouvrira dans votre navigateur")
    print("🛑 Appuyez sur Ctrl+C pour arrêter l'application")
    print("-" * 50)
    
    try:
        # Lancer Streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 Application arrêtée")
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")

if __name__ == "__main__":
    main() 