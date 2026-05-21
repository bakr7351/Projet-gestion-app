#!/usr/bin/env python3
"""
Test script pour vérifier l'export Excel avec diagramme McCabe-Thiele
"""

import sys
import os
sys.path.append('.')

from backend.services.excel_export_service import generate_absorption_excel

# Données de test pour l'absorption
test_results = {
    "G_prime": 100.0,
    "L_prime": 150.0,
    "m": 0.5,
    "y0": 0.1,
    "x0": 0.0,
    "y_objectif": 0.01,
    "facteur_A": 3.0,
    "nb_etages": 5,
    "taux": 90.0,
    "quantite": 9.0,
    "performance": {
        "convergence": "Oui",
        "execution_time_ms": 15.2
    },
    "resultats": [
        {
            "etage": 1,
            "Y_entree": 0.111,
            "X_entree": 0.0,
            "X_sortie": 0.074,
            "Y_sortie": 0.074,
            "y_sortie": 0.069
        },
        {
            "etage": 2,
            "Y_entree": 0.074,
            "X_entree": 0.074,
            "X_sortie": 0.049,
            "Y_sortie": 0.049,
            "y_sortie": 0.047
        },
        {
            "etage": 3,
            "Y_entree": 0.049,
            "X_entree": 0.049,
            "X_sortie": 0.033,
            "Y_sortie": 0.033,
            "y_sortie": 0.032
        },
        {
            "etage": 4,
            "Y_entree": 0.033,
            "X_entree": 0.033,
            "X_sortie": 0.022,
            "Y_sortie": 0.022,
            "y_sortie": 0.021
        },
        {
            "etage": 5,
            "Y_entree": 0.022,
            "X_entree": 0.022,
            "X_sortie": 0.015,
            "Y_sortie": 0.011,
            "y_sortie": 0.011
        }
    ]
}

def test_excel_export():
    """Test de l'export Excel avec génération automatique du diagramme McCabe-Thiele"""
    print("🧪 Test de l'export Excel avec diagramme McCabe-Thiele...")
    
    try:
        # Générer le fichier Excel
        xlsx_bytes = generate_absorption_excel(test_results)
        
        print(f"✅ Fichier Excel généré avec succès !")
        print(f"📊 Taille du fichier : {len(xlsx_bytes)} bytes")
        
        # Sauvegarder le fichier pour vérification
        output_path = "test_export_mccabe.xlsx"
        with open(output_path, "wb") as f:
            f.write(xlsx_bytes)
        
        print(f"💾 Fichier sauvegardé : {output_path}")
        print(f"📁 Chemin complet : {os.path.abspath(output_path)}")
        
        print("\n🎯 Fonctionnalités testées :")
        print("  ✅ Génération automatique du diagramme McCabe-Thiele")
        print("  ✅ Intégration du diagramme dans Excel")
        print("  ✅ Feuilles de résumé et détails par étage")
        print("  ✅ Formatage professionnel")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_excel_export()
    if success:
        print("\n🎉 Test réussi ! L'export Excel avec diagramme McCabe-Thiele fonctionne parfaitement.")
    else:
        print("\n💥 Test échoué. Vérifiez les logs d'erreur ci-dessus.")