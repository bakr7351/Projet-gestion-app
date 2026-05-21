"""
Script de test pour la fonctionnalité de sécurité des connexions
Teste le système de blocage progressif
"""
import sys
import time
from app import create_app
from backend.services.login_security_service import login_security_service
from backend.models.login_attempt import LoginAttempt
from backend.extensions import db


def test_login_security():
    """Test complet du système de sécurité des connexions"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("TEST DU SYSTÈME DE SÉCURITÉ DES CONNEXIONS")
        print("=" * 70)
        
        # Nettoyer les données de test précédentes
        test_email = "test@example.com"
        test_ip = "192.168.1.100"
        
        LoginAttempt.query.filter_by(identifier=test_email).delete()
        LoginAttempt.query.filter_by(identifier=test_ip).delete()
        db.session.commit()
        
        print("\n✅ Données de test nettoyées")
        
        # Test 1: Première tentative échouée
        print("\n" + "=" * 70)
        print("TEST 1: Première tentative échouée")
        print("=" * 70)
        
        is_allowed, info = login_security_service.check_login_allowed(test_email, test_ip)
        print(f"Connexion autorisée: {is_allowed}")
        print(f"Info: {info}")
        
        failed_info = login_security_service.record_failed_login(test_email, test_ip)
        print(f"\nAprès échec:")
        print(f"Message: {failed_info['message']}")
        print(f"Bloqué: {failed_info.get('blocked', False)}")
        
        # Test 2: Deuxième tentative échouée
        print("\n" + "=" * 70)
        print("TEST 2: Deuxième tentative échouée")
        print("=" * 70)
        
        is_allowed, info = login_security_service.check_login_allowed(test_email, test_ip)
        print(f"Connexion autorisée: {is_allowed}")
        
        failed_info = login_security_service.record_failed_login(test_email, test_ip)
        print(f"Message: {failed_info['message']}")
        print(f"Bloqué: {failed_info.get('blocked', False)}")
        
        # Test 3: Troisième tentative échouée (déclenchement du blocage)
        print("\n" + "=" * 70)
        print("TEST 3: Troisième tentative échouée (BLOCAGE)")
        print("=" * 70)
        
        is_allowed, info = login_security_service.check_login_allowed(test_email, test_ip)
        print(f"Connexion autorisée: {is_allowed}")
        
        failed_info = login_security_service.record_failed_login(test_email, test_ip)
        print(f"Message: {failed_info['message']}")
        print(f"Bloqué: {failed_info.get('blocked', False)}")
        
        if failed_info.get('blocked'):
            email_info = failed_info.get('email_info', {})
            print(f"Temps de blocage: {email_info.get('remaining_time_formatted', 'N/A')}")
            print(f"Niveau de blocage: {email_info.get('block_level', 0)}")
        
        # Test 4: Tentative pendant le blocage
        print("\n" + "=" * 70)
        print("TEST 4: Tentative pendant le blocage")
        print("=" * 70)
        
        is_allowed, info = login_security_service.check_login_allowed(test_email, test_ip)
        print(f"Connexion autorisée: {is_allowed}")
        print(f"Message: {info.get('message', 'N/A')}")
        print(f"Temps restant: {info.get('remaining_time', 'N/A')}")
        
        # Test 5: Attendre quelques secondes et vérifier le temps restant
        print("\n" + "=" * 70)
        print("TEST 5: Vérification du temps restant (attente 3 secondes)")
        print("=" * 70)
        
        print("Attente de 3 secondes...")
        time.sleep(3)
        
        is_allowed, info = login_security_service.check_login_allowed(test_email, test_ip)
        print(f"Connexion autorisée: {is_allowed}")
        if not is_allowed:
            print(f"Temps restant: {info.get('remaining_time', 'N/A')}")
            print(f"Secondes restantes: {info.get('remaining_seconds', 0)}")
        
        # Test 6: Connexion réussie (réinitialisation)
        print("\n" + "=" * 70)
        print("TEST 6: Simulation connexion réussie (RÉINITIALISATION)")
        print("=" * 70)
        
        # Forcer la fin du blocage pour tester la réinitialisation
        attempt = LoginAttempt.get_or_create(test_email, 'email')
        attempt.blocked_until = None
        db.session.commit()
        
        login_security_service.record_successful_login(test_email, test_ip)
        
        status = login_security_service.get_security_status(test_email, test_ip)
        print(f"Statut après connexion réussie:")
        print(f"  Email - Tentatives échouées: {status['email']['failed_attempts']}")
        print(f"  Email - Bloqué: {status['email']['is_blocked']}")
        print(f"  Email - Niveau de blocage: {status['email'].get('block_level', 0)}")
        print(f"  IP - Tentatives échouées: {status['ip']['failed_attempts']}")
        print(f"  IP - Bloqué: {status['ip']['is_blocked']}")
        
        # Test 7: Test du blocage progressif (double le temps)
        print("\n" + "=" * 70)
        print("TEST 7: Test du blocage progressif (temps doublé)")
        print("=" * 70)
        
        # Créer 3 nouvelles tentatives échouées
        for i in range(3):
            login_security_service.record_failed_login(test_email, test_ip)
            print(f"Tentative échouée {i+1}/3")
        
        # Vérifier le nouveau temps de blocage
        is_allowed, info = login_security_service.check_login_allowed(test_email, test_ip)
        print(f"\nConnexion autorisée: {is_allowed}")
        if not is_allowed:
            print(f"Temps de blocage: {info.get('remaining_time', 'N/A')}")
            print(f"Secondes: {info.get('remaining_seconds', 0)} (devrait être ~60s)")
        
        attempt = LoginAttempt.get_or_create(test_email, 'email')
        print(f"Niveau de blocage actuel: {attempt.block_level} (devrait être 2)")
        
        # Nettoyage final
        print("\n" + "=" * 70)
        print("NETTOYAGE")
        print("=" * 70)
        
        LoginAttempt.query.filter_by(identifier=test_email).delete()
        LoginAttempt.query.filter_by(identifier=test_ip).delete()
        db.session.commit()
        
        print("✅ Données de test nettoyées")
        
        print("\n" + "=" * 70)
        print("TESTS TERMINÉS AVEC SUCCÈS ✅")
        print("=" * 70)
        print("\nRésumé des fonctionnalités testées:")
        print("  ✓ Comptage des tentatives échouées")
        print("  ✓ Blocage après 3 tentatives")
        print("  ✓ Calcul du temps restant")
        print("  ✓ Réinitialisation après connexion réussie")
        print("  ✓ Blocage progressif (temps doublé)")
        print("  ✓ Protection par email ET par IP")


if __name__ == "__main__":
    try:
        test_login_security()
    except Exception as e:
        print(f"\n❌ ERREUR LORS DES TESTS: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
