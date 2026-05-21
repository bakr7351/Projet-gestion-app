from flask import current_app, url_for
from flask_mail import Message
from backend.extensions import mail


def _send(subject: str, recipient: str, body: str, html_body: str = None) -> None:
    # In development (no MAIL_USERNAME configured), just log to console
    if not current_app.config.get("MAIL_USERNAME"):
        current_app.logger.info(
            f"\n{'='*60}\n📧 EMAIL (dev mode — not sent)\nTo: {recipient}\nSubject: {subject}\n\n{body}\n{'='*60}"
        )
        return
    
    msg = Message(
        subject=subject, 
        recipients=[recipient], 
        body=body,
        html=html_body
    )
    mail.send(msg)


def send_verification(user, token: str) -> None:
    """Envoie un email de vérification avec un lien d'activation"""
    link = f"http://127.0.0.1:5000/user/verify-email.html?token={token}"
    
    # Version texte
    text_body = f"""Bonjour {user.prenom} {user.nom},

Merci de vous être inscrit sur notre plateforme de calculs chimiques !

Pour activer votre compte, veuillez cliquer sur le lien suivant :
{link}

⚠️ Ce lien expire dans 24 heures.

Si vous n'avez pas créé ce compte, vous pouvez ignorer cet email.

Cordialement,
L'équipe Calculs Chimiques"""

    # Version HTML
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #4f46e5, #4338ca); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="margin: 0; font-size: 24px;">🧪 Calculs Chimiques</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Activation de votre compte</p>
            </div>
            
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e2e8f0;">
                <h2 style="color: #4f46e5; margin-top: 0;">Bonjour {user.prenom} {user.nom},</h2>
                
                <p>Merci de vous être inscrit sur notre plateforme de calculs chimiques !</p>
                
                <p>Pour activer votre compte et commencer à utiliser nos outils de calcul, veuillez cliquer sur le bouton ci-dessous :</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{link}" style="background: linear-gradient(135deg, #4f46e5, #4338ca); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                        ✅ Activer mon compte
                    </a>
                </div>
                
                <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #92400e;"><strong>⚠️ Important :</strong> Ce lien expire dans 24 heures.</p>
                </div>
                
                <p style="font-size: 14px; color: #6b7280;">Si vous n'avez pas créé ce compte, vous pouvez ignorer cet email en toute sécurité.</p>
                
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                
                <p style="font-size: 14px; color: #6b7280; margin: 0;">
                    Cordialement,<br>
                    <strong>L'équipe Calculs Chimiques</strong>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    _send(
        subject="🧪 Activez votre compte - Calculs Chimiques",
        recipient=user.email,
        body=text_body,
        html_body=html_body
    )


def send_activation_confirmation(user) -> None:
    """Confirme l'activation du compte"""
    text_body = f"""Bonjour {user.prenom},

Excellente nouvelle ! Votre compte a été activé avec succès.

Vous pouvez maintenant vous connecter et accéder à tous nos outils de calculs chimiques :
- Calculs d'absorption et désorption
- Diagrammes McCabe-Thiele
- Simulateurs de courants croisés
- Historique de vos calculs

Connexion : http://127.0.0.1:5000/user/login.html

Cordialement,
L'équipe Calculs Chimiques"""

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="margin: 0; font-size: 24px;">🎉 Compte Activé !</h1>
            </div>
            
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e2e8f0;">
                <h2 style="color: #10b981; margin-top: 0;">Bonjour {user.prenom},</h2>
                
                <p><strong>Excellente nouvelle !</strong> Votre compte a été activé avec succès.</p>
                
                <p>Vous pouvez maintenant vous connecter et accéder à tous nos outils :</p>
                
                <ul style="color: #4b5563;">
                    <li>🧪 Calculs d'absorption et désorption</li>
                    <li>📊 Diagrammes McCabe-Thiele</li>
                    <li>⚡ Simulateurs de courants croisés</li>
                    <li>📈 Historique de vos calculs</li>
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://127.0.0.1:5000/user/login.html" style="background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                        🚀 Se connecter
                    </a>
                </div>
                
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                
                <p style="font-size: 14px; color: #6b7280; margin: 0;">
                    Cordialement,<br>
                    <strong>L'équipe Calculs Chimiques</strong>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    _send(
        subject="🎉 Votre compte est maintenant actif !",
        recipient=user.email,
        body=text_body,
        html_body=html_body
    )


def send_password_reset(user, token: str) -> None:
    """Envoie un lien de réinitialisation de mot de passe"""
    link = f"http://127.0.0.1:5000/user/reset-password.html?token={token}"
    
    text_body = f"""Bonjour {user.prenom},

Vous avez demandé la réinitialisation de votre mot de passe.

Cliquez sur le lien suivant pour créer un nouveau mot de passe :
{link}

⚠️ Ce lien expire dans 1 heure.

Si vous n'avez pas demandé cette réinitialisation, ignorez cet email. Votre mot de passe actuel reste inchangé.

Cordialement,
L'équipe Calculs Chimiques"""

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="margin: 0; font-size: 24px;">🔐 Réinitialisation</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Mot de passe</p>
            </div>
            
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e2e8f0;">
                <h2 style="color: #f59e0b; margin-top: 0;">Bonjour {user.prenom},</h2>
                
                <p>Vous avez demandé la réinitialisation de votre mot de passe.</p>
                
                <p>Cliquez sur le bouton ci-dessous pour créer un nouveau mot de passe :</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{link}" style="background: linear-gradient(135deg, #f59e0b, #d97706); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                        🔑 Réinitialiser mon mot de passe
                    </a>
                </div>
                
                <div style="background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #92400e;"><strong>⚠️ Important :</strong> Ce lien expire dans 1 heure.</p>
                </div>
                
                <div style="background: #f3f4f6; border: 1px solid #d1d5db; border-radius: 8px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #374151; font-size: 14px;"><strong>🛡️ Sécurité :</strong> Si vous n'avez pas demandé cette réinitialisation, ignorez cet email. Votre mot de passe actuel reste inchangé.</p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                
                <p style="font-size: 14px; color: #6b7280; margin: 0;">
                    Cordialement,<br>
                    <strong>L'équipe Calculs Chimiques</strong>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    _send(
        subject="🔐 Réinitialisation de votre mot de passe",
        recipient=user.email,
        body=text_body,
        html_body=html_body
    )


def send_password_changed(user) -> None:
    """Confirme le changement de mot de passe"""
    text_body = f"""Bonjour {user.prenom},

Votre mot de passe a été modifié avec succès.

Si vous n'êtes pas à l'origine de cette modification, contactez-nous immédiatement.

Cordialement,
L'équipe Calculs Chimiques"""

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="margin: 0; font-size: 24px;">✅ Mot de passe modifié</h1>
            </div>
            
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e2e8f0;">
                <h2 style="color: #10b981; margin-top: 0;">Bonjour {user.prenom},</h2>
                
                <p><strong>Votre mot de passe a été modifié avec succès.</strong></p>
                
                <div style="background: #fef2f2; border: 1px solid #ef4444; border-radius: 8px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #dc2626;"><strong>🚨 Sécurité :</strong> Si vous n'êtes pas à l'origine de cette modification, contactez-nous immédiatement.</p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                
                <p style="font-size: 14px; color: #6b7280; margin: 0;">
                    Cordialement,<br>
                    <strong>L'équipe Calculs Chimiques</strong>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    _send(
        subject="✅ Mot de passe modifié avec succès",
        recipient=user.email,
        body=text_body,
        html_body=html_body
    )


def send_status_change(user, new_status: str) -> None:
    """Notifie un changement de statut de compte"""
    status_messages = {
        "actif": "Votre compte a été activé",
        "desactive": "Votre compte a été désactivé",
        "banni": "Votre compte a été suspendu",
        "non_verifie": "Votre compte nécessite une vérification"
    }
    
    message = status_messages.get(new_status, f"L'état de votre compte a été mis à jour : {new_status}")
    
    _send(
        subject="📋 Modification de votre compte",
        recipient=user.email,
        body=f"Bonjour {user.prenom},\n\n{message}.\n\nCordialement,\nL'équipe Calculs Chimiques",
    )


def send_notification(user, content: str) -> None:
    """Envoie une notification générale"""
    _send(
        subject="📢 Notification - Calculs Chimiques",
        recipient=user.email,
        body=f"Bonjour {user.prenom},\n\n{content}\n\nCordialement,\nL'équipe Calculs Chimiques",
    )


def send_welcome(user) -> None:
    """Envoie un email de bienvenue avec guide d'utilisation"""
    text_body = f"""Bonjour {user.prenom},

Bienvenue sur la plateforme Calculs Chimiques !

Votre compte est maintenant actif et vous pouvez accéder à tous nos outils :

🧪 OUTILS DISPONIBLES :
• Calculs d'absorption et désorption
• Diagrammes McCabe-Thiele interactifs
• Simulateurs de courants croisés
• Historique et export de vos calculs

🚀 POUR COMMENCER :
1. Connectez-vous : http://127.0.0.1:5000/user/login.html
2. Explorez les différents calculateurs
3. Sauvegardez vos calculs favoris
4. Exportez vos résultats en Excel

📚 BESOIN D'AIDE ?
Consultez notre documentation intégrée ou contactez notre équipe.

Si vous n'avez pas créé ce compte, contactez-nous immédiatement.

Cordialement,
L'équipe Calculs Chimiques"""

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #4f46e5, #4338ca); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="margin: 0; font-size: 28px;">🎉 Bienvenue !</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 18px;">Calculs Chimiques</p>
            </div>
            
            <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e2e8f0;">
                <h2 style="color: #4f46e5; margin-top: 0;">Bonjour {user.prenom},</h2>
                
                <p><strong>Bienvenue sur la plateforme Calculs Chimiques !</strong></p>
                
                <p>Votre compte est maintenant actif et vous pouvez accéder à tous nos outils professionnels.</p>
                
                <div style="background: #eff6ff; border: 1px solid #3b82f6; border-radius: 8px; padding: 20px; margin: 25px 0;">
                    <h3 style="color: #1d4ed8; margin-top: 0;">🧪 Outils disponibles :</h3>
                    <ul style="color: #1e40af; margin: 10px 0;">
                        <li>Calculs d'absorption et désorption</li>
                        <li>Diagrammes McCabe-Thiele interactifs</li>
                        <li>Simulateurs de courants croisés</li>
                        <li>Historique et export de vos calculs</li>
                    </ul>
                </div>
                
                <div style="background: #f0fdf4; border: 1px solid #22c55e; border-radius: 8px; padding: 20px; margin: 25px 0;">
                    <h3 style="color: #15803d; margin-top: 0;">🚀 Pour commencer :</h3>
                    <ol style="color: #166534; margin: 10px 0;">
                        <li>Connectez-vous à votre compte</li>
                        <li>Explorez les différents calculateurs</li>
                        <li>Sauvegardez vos calculs favoris</li>
                        <li>Exportez vos résultats en Excel</li>
                    </ol>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://127.0.0.1:5000/user/login.html" style="background: linear-gradient(135deg, #4f46e5, #4338ca); color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block; font-size: 16px;">
                        🚀 Commencer maintenant
                    </a>
                </div>
                
                <div style="background: #fefce8; border: 1px solid #eab308; border-radius: 8px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #a16207;"><strong>📚 Besoin d'aide ?</strong> Consultez notre documentation intégrée ou contactez notre équipe.</p>
                </div>
                
                <div style="background: #fef2f2; border: 1px solid #ef4444; border-radius: 8px; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0; color: #dc2626; font-size: 14px;"><strong>🛡️ Sécurité :</strong> Si vous n'avez pas créé ce compte, contactez-nous immédiatement.</p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                
                <p style="font-size: 14px; color: #6b7280; margin: 0;">
                    Cordialement,<br>
                    <strong>L'équipe Calculs Chimiques</strong>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    _send(
        subject="🎉 Bienvenue sur Calculs Chimiques !",
        recipient=user.email,
        body=text_body,
        html_body=html_body
    )
