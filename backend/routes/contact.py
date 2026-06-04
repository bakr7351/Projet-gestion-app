"""
Route pour gérer les messages de contact
Utilise Gmail avec la configuration définie dans .env
"""
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from backend.extensions import mail
from flask_mail import Message
import os

contact_bp = Blueprint('contact', __name__)


@contact_bp.route('/api/contact', methods=['POST'])
def send_contact_message():
    """
    Endpoint pour recevoir et traiter les messages de contact
    Envoie un email via Gmail en utilisant la configuration Flask-Mail
    """
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = ['name', 'email', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'error': f'Le champ {field} est requis'
                }), 400
        
        name = data['name']
        email = data['email']
        subject = data['subject']
        message_text = data['message']
        
        # Vérifier si l'email est configuré
        if not current_app.config.get('MAIL_USERNAME'):
            print(f"\n{'='*50}")
            print("📧 MESSAGE DE CONTACT (Mode développement)")
            print(f"{'='*50}")
            print(f"De: {name} ({email})")
            print(f"Sujet: {subject}")
            print(f"Message:\n{message_text}")
            print(f"{'='*50}\n")
            
            return jsonify({
                'success': True,
                'message': 'Message enregistré (mode développement)'
            }), 200
        
        # Construire l'email HTML
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #e0e0e0; }}
                .info {{ background: white; padding: 15px; margin: 15px 0; border-left: 4px solid #667eea; }}
                .footer {{ text-align: center; padding: 20px; color: #888; font-size: 0.9em; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>📧 Nouveau Message de Contact</h2>
                    <p>Calculs Chimiques</p>
                </div>
                <div class="content">
                    <div class="info">
                        <strong>👤 Nom:</strong> {name}
                    </div>
                    <div class="info">
                        <strong>📧 Email:</strong> <a href="mailto:{email}">{email}</a>
                    </div>
                    <div class="info">
                        <strong>📌 Sujet:</strong> {subject}
                    </div>
                    <div class="info">
                        <strong>💬 Message:</strong><br><br>
                        {message_text.replace(chr(10), '<br>')}
                    </div>
                    <div class="info">
                        <strong>🕐 Date:</strong> {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
                    </div>
                </div>
                <div class="footer">
                    <p>Ce message a été envoyé depuis le formulaire de contact du site Calculs Chimiques</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Créer le message avec Flask-Mail
        msg = Message(
            subject=f"[Contact Site] {subject}",
            sender=current_app.config['MAIL_DEFAULT_SENDER'],
            recipients=[current_app.config['MAIL_USERNAME']],  # Email de réception (Gmail configuré)
            reply_to=email  # L'email de l'expéditeur pour répondre facilement
        )
        
        # Corps texte simple
        msg.body = f"""
Nouveau message de contact depuis Calculs Chimiques

==========================================
Nom: {name}
Email: {email}
Sujet: {subject}
Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
==========================================

Message:
{message_text}

==========================================
        """
        
        # Corps HTML stylisé
        msg.html = html_body
        
        # Envoyer l'email
        mail.send(msg)
        
        print(f"\n✅ Email de contact envoyé avec succès à {current_app.config['MAIL_USERNAME']}\n")
        
        return jsonify({
            'success': True,
            'message': 'Message envoyé avec succès'
        }), 200
        
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi du message: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Erreur lors de l\'envoi du message. Veuillez réessayer ou nous contacter directement par email.'
        }), 500


@contact_bp.route('/about')
def about_page():
    """
    Serve the about page
    """
    try:
        from flask import send_from_directory
        import os
        # Chemin vers le frontend
        FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
        return send_from_directory(os.path.join(FRONTEND_DIR, "public"), 'about.html')
    except Exception as e:
        print(f"❌ Erreur chargement page about: {e}")
        from flask import jsonify
        return jsonify({'error': str(e)}), 404
