"""
Service de sécurité pour les tentatives de connexion
Gère le blocage progressif et la protection contre les attaques par force brute
"""
import logging
from typing import Tuple, Dict, Any
from backend.models.login_attempt import LoginAttempt
from backend.extensions import db

logger = logging.getLogger(__name__)


class LoginSecurityService:
    """
    Service pour gérer la sécurité des connexions avec blocage progressif
    """
    
    @staticmethod
    def check_login_allowed(email: str, ip_address: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Vérifie si une tentative de connexion est autorisée
        
        Args:
            email: Adresse email de l'utilisateur
            ip_address: Adresse IP de la requête
            
        Returns:
            Tuple (is_allowed: bool, info: dict)
        """
        try:
            # Vérification par email (plus restrictif)
            email_attempt = LoginAttempt.get_or_create(email, 'email')
            email_info = email_attempt.get_block_info()
            
            # Vérification par IP (protection générale)
            ip_attempt = LoginAttempt.get_or_create(ip_address, 'ip')
            ip_info = ip_attempt.get_block_info()
            
            # Si l'email OU l'IP est bloqué, refuser la connexion
            if email_info['is_blocked'] or ip_info['is_blocked']:
                # Retourner les informations du blocage le plus restrictif
                if email_info['is_blocked'] and ip_info['is_blocked']:
                    # Prendre le blocage avec le plus de temps restant
                    if email_info['remaining_seconds'] >= ip_info['remaining_seconds']:
                        block_info = email_info
                        block_reason = 'email'
                    else:
                        block_info = ip_info
                        block_reason = 'ip'
                elif email_info['is_blocked']:
                    block_info = email_info
                    block_reason = 'email'
                else:
                    block_info = ip_info
                    block_reason = 'ip'
                
                logger.warning(
                    f"Login blocked for {email} from {ip_address} - "
                    f"Reason: {block_reason}, Time remaining: {block_info['remaining_seconds']}s"
                )
                
                return False, {
                    'blocked': True,
                    'reason': block_reason,
                    'remaining_seconds': block_info['remaining_seconds'],
                    'remaining_time': block_info['remaining_time_formatted'],
                    'message': f"Trop de tentatives échouées. Réessayez dans {block_info['remaining_time_formatted']}."
                }
            
            # Connexion autorisée, retourner les informations d'état
            return True, {
                'blocked': False,
                'email_attempts': email_info['failed_attempts'],
                'ip_attempts': ip_info['failed_attempts'],
                'email_attempts_remaining': email_info.get('attempts_remaining', 3),
                'ip_attempts_remaining': ip_info.get('attempts_remaining', 3)
            }
            
        except Exception as e:
            logger.error(f"Error checking login security for {email}: {e}")
            # En cas d'erreur, autoriser la connexion mais logger l'erreur
            return True, {'blocked': False, 'error': 'Security check failed'}
    
    @staticmethod
    def record_failed_login(email: str, ip_address: str) -> Dict[str, Any]:
        """
        Enregistre une tentative de connexion échouée
        
        Args:
            email: Adresse email de l'utilisateur
            ip_address: Adresse IP de la requête
            
        Returns:
            Dict avec les informations de blocage mises à jour
        """
        try:
            # Enregistrer l'échec pour l'email
            email_attempt = LoginAttempt.get_or_create(email, 'email')
            email_attempt.record_failed_attempt()
            
            # Enregistrer l'échec pour l'IP
            ip_attempt = LoginAttempt.get_or_create(ip_address, 'ip')
            ip_attempt.record_failed_attempt()
            
            # Récupérer les informations mises à jour
            email_info = email_attempt.get_block_info()
            ip_info = ip_attempt.get_block_info()
            
            logger.warning(
                f"Failed login recorded for {email} from {ip_address} - "
                f"Email attempts: {email_info['failed_attempts']}, "
                f"IP attempts: {ip_info['failed_attempts']}"
            )
            
            # Déterminer le message à afficher
            message = "Identifiants incorrects."
            
            if email_info['is_blocked'] or ip_info['is_blocked']:
                # Prendre le blocage le plus restrictif
                if email_info['is_blocked'] and ip_info['is_blocked']:
                    block_info = email_info if email_info['remaining_seconds'] >= ip_info['remaining_seconds'] else ip_info
                elif email_info['is_blocked']:
                    block_info = email_info
                else:
                    block_info = ip_info
                
                message = f"Trop de tentatives échouées. Compte bloqué pendant {block_info['remaining_time_formatted']}."
            else:
                # Avertir l'utilisateur du nombre de tentatives restantes
                remaining = min(
                    email_info.get('attempts_remaining', 3),
                    ip_info.get('attempts_remaining', 3)
                )
                if remaining <= 1:
                    message = f"Identifiants incorrects. Attention : {remaining} tentative restante avant blocage temporaire."
                elif remaining <= 2:
                    message = f"Identifiants incorrects. Attention : {remaining} tentatives restantes avant blocage temporaire."
            
            return {
                'message': message,
                'email_info': email_info,
                'ip_info': ip_info,
                'blocked': email_info['is_blocked'] or ip_info['is_blocked']
            }
            
        except Exception as e:
            logger.error(f"Error recording failed login for {email}: {e}")
            return {
                'message': "Identifiants incorrects.",
                'error': 'Failed to record attempt'
            }
    
    @staticmethod
    def record_successful_login(email: str, ip_address: str) -> None:
        """
        Enregistre une connexion réussie et réinitialise les compteurs
        
        Args:
            email: Adresse email de l'utilisateur
            ip_address: Adresse IP de la requête
        """
        try:
            # Réinitialiser les tentatives pour l'email
            email_attempt = LoginAttempt.get_or_create(email, 'email')
            email_attempt.record_successful_login()
            
            # Réinitialiser les tentatives pour l'IP
            ip_attempt = LoginAttempt.get_or_create(ip_address, 'ip')
            ip_attempt.record_successful_login()
            
            logger.info(f"Successful login recorded for {email} from {ip_address} - Counters reset")
            
        except Exception as e:
            logger.error(f"Error recording successful login for {email}: {e}")
    
    @staticmethod
    def get_security_status(email: str, ip_address: str) -> Dict[str, Any]:
        """
        Récupère le statut de sécurité actuel pour un email/IP
        
        Args:
            email: Adresse email de l'utilisateur
            ip_address: Adresse IP de la requête
            
        Returns:
            Dict avec les informations de sécurité
        """
        try:
            email_attempt = LoginAttempt.get_or_create(email, 'email')
            ip_attempt = LoginAttempt.get_or_create(ip_address, 'ip')
            
            return {
                'email': email_attempt.get_block_info(),
                'ip': ip_attempt.get_block_info(),
                'overall_blocked': email_attempt.is_blocked() or ip_attempt.is_blocked()
            }
            
        except Exception as e:
            logger.error(f"Error getting security status for {email}: {e}")
            return {
                'email': {'is_blocked': False, 'failed_attempts': 0},
                'ip': {'is_blocked': False, 'failed_attempts': 0},
                'overall_blocked': False,
                'error': 'Failed to get status'
            }
    
    @staticmethod
    def cleanup_expired_attempts() -> int:
        """
        Nettoie les anciennes tentatives expirées
        Méthode utilitaire pour maintenance
        
        Returns:
            Nombre d'enregistrements supprimés
        """
        try:
            cleaned_count = LoginAttempt.cleanup_expired_blocks()
            logger.info(f"Cleaned up {cleaned_count} expired login attempt records")
            return cleaned_count
        except Exception as e:
            logger.error(f"Error cleaning up expired attempts: {e}")
            return 0


# Instance globale du service
login_security_service = LoginSecurityService()