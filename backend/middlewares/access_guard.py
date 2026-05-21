"""
Middleware pour contrôler l'accès aux calculs
L'utilisateur doit être connecté OU avoir choisi l'accès anonyme
"""
from functools import wraps
from flask import request, jsonify, session
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def require_access_choice(f):
    """
    Décorateur qui vérifie que l'utilisateur a fait un choix d'accès:
    - Soit il est connecté (JWT valide)
    - Soit il a choisi l'accès anonyme (session ou header spécial)
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Vérifier si l'utilisateur est connecté (JWT)
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                # Utilisateur connecté, accès autorisé
                return f(*args, **kwargs)
        except Exception:
            pass  # JWT invalide ou absent, continuer la vérification
        
        # Vérifier l'accès anonyme via header
        anonymous_access = request.headers.get('X-Anonymous-Access')
        if anonymous_access == 'true':
            # Accès anonyme autorisé
            return f(*args, **kwargs)
        
        # Vérifier l'accès anonyme via referer (vient de la page publique)
        referer = request.headers.get('Referer', '')
        if '/public/' in referer:
            # Vient de la page publique, accès autorisé
            return f(*args, **kwargs)
        
        # Aucun accès valide trouvé
        return jsonify({
            'success': False,
            'message': 'Accès non autorisé. Veuillez vous connecter ou choisir l\'accès anonyme.',
            'redirect': '/'
        }), 401
    
    return decorated_function

def check_user_access():
    """
    Fonction utilitaire pour vérifier le type d'accès de l'utilisateur
    Retourne: 'authenticated', 'anonymous', ou None
    """
    # Vérifier JWT
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
        if user_id:
            return 'authenticated'
    except Exception:
        pass
    
    # Vérifier accès anonyme
    anonymous_access = request.headers.get('X-Anonymous-Access')
    if anonymous_access == 'true':
        return 'anonymous'
    
    # Vérifier referer
    referer = request.headers.get('Referer', '')
    if '/public/' in referer:
        return 'anonymous'
    
    return None