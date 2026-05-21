"""
Routes pour l'Assistant AI
Gère les interactions avec l'assistant intelligent pour les calculs chimiques
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.ai_assistant_service import ai_assistant_service
from backend.middlewares.rate_limiter import require_rate_limit
import logging

logger = logging.getLogger(__name__)

assistant_bp = Blueprint('assistant', __name__)

@assistant_bp.route('/chat', methods=['POST'])
@jwt_required()
@require_rate_limit('assistant_chat')
def chat_with_assistant():
    """
    Endpoint pour discuter avec l'assistant AI
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'message': 'Message requis'
            }), 400
        
        user_id = get_jwt_identity()
        message = data['message'].strip()
        conversation_history = data.get('conversation_history', [])
        
        if not message:
            return jsonify({
                'success': False,
                'message': 'Message vide'
            }), 400
        
        if len(message) > 1000:
            return jsonify({
                'success': False,
                'message': 'Message trop long (max 1000 caractères)'
            }), 400
        
        logger.info(f"Assistant AI - User {user_id}: {message[:100]}...")
        
        # Générer la réponse avec l'assistant AI
        response = ai_assistant_service.get_response(message, conversation_history)
        
        logger.info(f"Assistant AI - Response length: {len(response)} chars")
        
        return jsonify({
            'success': True,
            'response': response,
            'timestamp': int(__import__('time').time())
        })
        
    except Exception as e:
        logger.error(f"Erreur dans chat_with_assistant: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Erreur interne du serveur'
        }), 500

@assistant_bp.route('/suggestions', methods=['GET'])
@jwt_required()
@require_rate_limit('assistant_suggestions')
def get_suggestions():
    """
    Endpoint pour obtenir des suggestions de questions
    """
    try:
        suggestions = [
            {
                'category': 'Calculs',
                'questions': [
                    'Comment calculer le nombre d\'étages théoriques ?',
                    'Quelle formule utiliser pour le facteur d\'absorption ?',
                    'Comment déterminer le débit optimal de solvant ?',
                    'Quelle est la relation entre Y et y ?'
                ]
            },
            {
                'category': 'Procédés',
                'questions': [
                    'Quelle est la différence entre absorption et désorption ?',
                    'Quand utiliser le contre-courant vs courant croisé ?',
                    'Comment choisir le bon solvant pour l\'absorption ?',
                    'Qu\'est-ce qui influence l\'efficacité d\'une colonne ?'
                ]
            },
            {
                'category': 'Diagrammes',
                'questions': [
                    'Comment interpréter un diagramme McCabe-Thiele ?',
                    'Que représente la courbe d\'équilibre ?',
                    'Comment tracer la droite opératoire ?',
                    'Pourquoi construire des marches d\'escalier ?'
                ]
            },
            {
                'category': 'Optimisation',
                'questions': [
                    'Comment optimiser l\'efficacité d\'une colonne ?',
                    'Quel impact du rapport L\'/G\' sur les performances ?',
                    'Comment réduire le nombre d\'étages nécessaires ?',
                    'Quels paramètres ajuster pour améliorer le taux d\'absorption ?'
                ]
            }
        ]
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        logger.error(f"Erreur dans get_suggestions: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Erreur interne du serveur'
        }), 500

@assistant_bp.route('/knowledge', methods=['GET'])
@jwt_required()
@require_rate_limit('assistant_knowledge')
def get_knowledge_topics():
    """
    Endpoint pour obtenir les sujets de la base de connaissances
    """
    try:
        topics = {
            'absorption': {
                'title': 'Absorption',
                'description': 'Procédé de capture d\'un composant gazeux dans un liquide',
                'subtopics': ['Définition', 'Calculs', 'Paramètres', 'Applications']
            },
            'desorption': {
                'title': 'Désorption',
                'description': 'Procédé d\'extraction d\'un composant du liquide vers le gaz',
                'subtopics': ['Définition', 'Calculs', 'Paramètres', 'Applications']
            },
            'mccabe_thiele': {
                'title': 'Diagramme McCabe-Thiele',
                'description': 'Méthode graphique pour déterminer les étages théoriques',
                'subtopics': ['Construction', 'Interprétation', 'Éléments', 'Utilisation']
            },
            'optimisation': {
                'title': 'Optimisation',
                'description': 'Amélioration des performances des procédés',
                'subtopics': ['Paramètres', 'Stratégies', 'Critères', 'Outils']
            }
        }
        
        return jsonify({
            'success': True,
            'topics': topics
        })
        
    except Exception as e:
        logger.error(f"Erreur dans get_knowledge_topics: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Erreur interne du serveur'
        }), 500

@assistant_bp.route('/feedback', methods=['POST'])
@jwt_required()
@require_rate_limit('assistant_feedback')
def submit_feedback():
    """
    Endpoint pour soumettre un feedback sur les réponses de l'assistant
    """
    try:
        data = request.get_json()
        
        if not data or 'rating' not in data:
            return jsonify({
                'success': False,
                'message': 'Rating requis'
            }), 400
        
        user_id = get_jwt_identity()
        rating = data['rating']  # 1-5
        message = data.get('message', '')
        response_id = data.get('response_id', '')
        
        if rating not in [1, 2, 3, 4, 5]:
            return jsonify({
                'success': False,
                'message': 'Rating doit être entre 1 et 5'
            }), 400
        
        logger.info(f"Assistant AI Feedback - User {user_id}: Rating {rating}")
        
        # Ici on pourrait sauvegarder le feedback en base de données
        # pour améliorer l'assistant au fil du temps
        
        return jsonify({
            'success': True,
            'message': 'Merci pour votre feedback !'
        })
        
    except Exception as e:
        logger.error(f"Erreur dans submit_feedback: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Erreur interne du serveur'
        }), 500