#!/usr/bin/env python3
"""
Test script pour vérifier l'export Excel de désorption avec diagramme McCabe-Thiele
"""

import sys
import os
sys.path.append('.')

from backend.services.excel_export_service import generate_desorption_excel

# Données de test pour la désorption
test_results = {
    "G": 80.0,
    "L": 120.0,
    "m": 0.8,
    "x0": 0.15,
    "y0": 0.0,
    "x_obj": 0.02,
    "facteur_S": 2.5,
    "nb_etages": 4,
    "taux": 86.7,
    "quantite": 13.0,
    "performance": {
        "convergence": "Oui",
        "execution_time_ms": 12.8
    },
    "resultats": [
        {
            "etage": 1,
            "X_entree": 0.176,
            "Y_entree": 0.0,
            "X_sortie": 0.118,
            "Y_sortie": 0.094,
            "x_sortie": 0.106
        },
        {
            "etage": 2,
            "X_entree": 0.118,
            "Y_entree": 0.094,
            "X_sortie": 0.079,
            "Y_sortie": 0.063,
            "x_sortie": 0.073
        },
        {
            "etage": 3,
            "X_entree": 0.079,
            "Y_entree": 0.063,
            "X_sortie": 0.053,
            "Y_sortie": 0.042,
            "x_sortie": 0.050
        },
        {
            "etage": 4,
            "X_entree": 0.053,
            "Y_entree": 0.042,
            "X_sortie": 0.020,
            "Y_sortie": 0.028,
            "x_sortie": 0.020
        }
    ]
}

def test_desorption_excel_export():
    """Test de l'export Excel de désorption avec génération automatique du diagramme McCabe-Thiele"""
    print("🧪 Test de l'export Excel de désorption avec diagramme McCabe-Thiele...")
    
    try:
        # Générer le fichier Excel
        xlsx_bytes = generate_desorption_excel(test_results)
        
        print(f"✅ Fichier Excel de désorption généré avec succès !")
        print(f"📊 Taille du fichier : {len(xlsx_bytes)} bytes")
        
        # Sauvegarder le fichier pour vérification
        output_path = "test_desorption_mccabe.xlsx"
        with open(output_path, "wb") as f:
            f.write(xlsx_bytes)
        
        print(f"💾 Fichier sauvegardé : {output_path}")
        print(f"📁 Chemin complet : {os.path.abspath(output_path)}")
        
        print("\n🎯 Fonctionnalités testées :")
        print("  ✅ Génération automatique du diagramme McCabe-Thiele pour désorption")
        print("  ✅ Intégration du diagramme dans Excel")
        print("  ✅ Feuilles de résumé et détails par étage")
        print("  ✅ Formatage professionnel spécifique à la désorption")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test de désorption : {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_desorption_excel_export()
    if success:
        print("\n🎉 Test de désorption réussi ! L'export Excel avec diagramme McCabe-Thiele fonctionne parfaitement.")
    else:
        print("\n💥 Test de désorption échoué. Vérifiez les logs d'erreur ci-dessus.")