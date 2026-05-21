#!/usr/bin/env python3
"""
Point d'entrée principal de l'application Absorption
Application web pour calculs d'absorption et désorption
"""

import sys
import os

# Ajouter le répertoire racine au path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import create_app

if __name__ == "__main__":
    app = create_app()
    
    print("🚀 APPLICATION CALCULS CHIMIQUES")
    print("   👉 http://127.0.0.1:5000")
    print("   📊 Absorption • Désorption • Export Excel")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
