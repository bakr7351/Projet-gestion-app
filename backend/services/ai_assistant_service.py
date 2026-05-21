"""
Service Assistant AI pour les calculs chimiques
Fournit des réponses intelligentes UNIQUEMENT sur les sujets liés au site
"""
import logging
from typing import List, Dict, Any
import json

logger = logging.getLogger(__name__)

class AIAssistantService:
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Charge la base de connaissances sur les calculs chimiques"""
        return {
            "absorption": {
                "definition": "L'absorption est un procédé de séparation où un composant gazeux est transféré vers une phase liquide.",
                "applications": [
                    "Purification de gaz",
                    "Récupération de solvants",
                    "Traitement des effluents gazeux",
                    "Production chimique"
                ],
                "parametres_cles": [
                    "Débit gaz G' (mol/h)",
                    "Débit solvant L' (mol/h)", 
                    "Constante d'équilibre m",
                    "Fraction molaire d'entrée y₀",
                    "Fraction objectif y_obj"
                ],
                "equations": {
                    "facteur_absorption": "A = L'/(m × G')",
                    "rapport_molaire": "Y = y/(1-y)",
                    "etages_theoriques": "N = ln(Y₀/Y_N) / ln(1+A)"
                }
            },
            "desorption": {
                "definition": "La désorption est un procédé où un composant dissous dans un liquide est transféré vers une phase gazeuse.",
                "applications": [
                    "Régénération de solvants",
                    "Stripping de composés volatils",
                    "Purification de liquides",
                    "Récupération de produits"
                ],
                "parametres_cles": [
                    "Débit gaz G (mol/h)",
                    "Débit liquide L (mol/h)",
                    "Constante d'équilibre m", 
                    "Fraction molaire d'entrée x₀",
                    "Fraction objectif x_obj"
                ],
                "equations": {
                    "facteur_desorption": "S = (m × G)/L",
                    "rapport_molaire": "X = x/(1-x)",
                    "etages_theoriques": "N = ln(X₀/X_N) / ln(1+S)"
                }
            }
        }

    def get_response(self, message: str, conversation_history: List[Dict] = None) -> str:
        """
        Génère une réponse basée sur le message de l'utilisateur
        Répond UNIQUEMENT aux questions liées au site (absorption, désorption, calculs chimiques)
        """
        try:
            message_lower = message.lower()
            
            # Vérifier si la question est liée au site
            site_keywords = [
                # Procédés chimiques
                'absorption', 'absorber', 'absorbe', 'absorbeur',
                'désorption', 'desorption', 'stripping', 'désorbé', 'desorbe',
                'mccabe', 'thiele', 'diagramme', 'graphique',
                'étage', 'etage', 'plateau', 'théorique', 'theorique',
                'colonne', 'garnissage', 'contacteur',
                
                # Paramètres et calculs
                'débit', 'debit', 'molaire', 'fraction',
                'constante', 'equilibre', 'équilibre',
                'facteur', 'efficacité', 'efficacite', 'rendement',
                'taux', 'concentration', 'rapport',
                
                # Opérations
                'calcul', 'calculer', 'formule', 'équation', 'equation',
                'optimis', 'améliorer', 'performance',
                'simuler', 'simulation', 'résultat', 'resultat',
                
                # Export et fonctionnalités
                'export', 'exporter', 'excel', 'txt',
                'historique', 'sauvegarder', 'télécharger', 'telecharger',
                
                # Aide générale sur le site
                'site', 'plateforme', 'utiliser', 'fonctionner',
                'aide', 'help', 'comment', 'pourquoi',
                'bonjour', 'salut', 'hello', 'bonsoir'
            ]
            
            # Vérifier si au moins un mot-clé du site est présent
            is_site_related = any(keyword in message_lower for keyword in site_keywords)
            
            # Si la question n'est PAS liée au site, refuser poliment
            if not is_site_related:
                return self._get_out_of_scope_response()
            
            # Réponses spécifiques au site
            if any(word in message_lower for word in ['absorption', 'absorber', 'absorbe', 'absorbeur']):
                return self._get_absorption_response(message_lower)
            elif any(word in message_lower for word in ['désorption', 'desorption', 'stripping', 'désorbé', 'desorbe']):
                return self._get_desorption_response(message_lower)
            elif any(word in message_lower for word in ['mccabe', 'thiele', 'diagramme', 'graphique']):
                return self._get_mccabe_response(message_lower)
            elif any(word in message_lower for word in ['étage', 'etage', 'plateau', 'théorique', 'theorique']):
                return self._get_stages_response(message_lower)
            elif any(word in message_lower for word in ['optimis', 'améliorer', 'efficacité', 'efficacite', 'performance']):
                return self._get_optimization_response(message_lower)
            elif any(word in message_lower for word in ['export', 'exporter', 'excel', 'télécharger', 'telecharger']):
                return self._get_export_response(message_lower)
            elif any(word in message_lower for word in ['historique', 'sauvegarder', 'sauvegarde']):
                return self._get_history_response(message_lower)
            elif any(word in message_lower for word in ['bonjour', 'salut', 'hello', 'hi', 'bonsoir']):
                return self._get_greeting_response()
            elif any(word in message_lower for word in ['aide', 'help', 'aidez-moi', 'aidez moi', 'comment utiliser']):
                return self._get_help_response()
            else:
                # Question liée au site mais pas de correspondance spécifique
                return self._get_general_site_response()
                
        except Exception as e:
            logger.error(f"Erreur dans get_response: {e}")
            return "Je rencontre une difficulté technique. Pouvez-vous reformuler votre question ?"
    
    def _get_out_of_scope_response(self) -> str:
        """Réponse pour les questions hors du scope du site"""
        return """**🎯 Assistant spécialisé**

Je suis un assistant spécialisé dans les **calculs d'absorption et de désorption**.

**Je peux vous aider avec :**
✅ Calculs d'absorption et désorption
✅ Diagrammes McCabe-Thiele
✅ Optimisation des procédés
✅ Interprétation des résultats
✅ Utilisation du site

**Je ne peux pas répondre à :**
❌ Questions générales hors du domaine du site
❌ Sujets non liés aux calculs chimiques

**💡 Exemples de questions que je peux traiter :**
• "Comment calculer le nombre d'étages théoriques ?"
• "Qu'est-ce que le diagramme McCabe-Thiele ?"
• "Comment optimiser mon procédé d'absorption ?"
• "Comment exporter mes résultats en Excel ?"

Posez-moi une question sur l'absorption, la désorption ou l'utilisation du site ! 😊"""

    def _get_absorption_response(self, message: str) -> str:
        """Réponses spécifiques à l'absorption"""
        absorption_info = self.knowledge_base["absorption"]
        
        if "définition" in message or "qu'est-ce" in message or "c'est quoi" in message:
            return f"""**Absorption - Définition**

{absorption_info['definition']}

**Applications principales :**
{chr(10).join(f'• {app}' for app in absorption_info['applications'])}

**Paramètres clés à considérer :**
{chr(10).join(f'• {param}' for param in absorption_info['parametres_cles'])}

L'efficacité dépend principalement du facteur d'absorption A = L'/(m × G')."""
        
        elif "calcul" in message or "formule" in message:
            return f"""**Formules clés pour l'absorption**

**Facteur d'absorption :** `A = L'/(m × G')`
- L' : débit molaire solvant (mol/h)
- G' : débit molaire gaz porteur (mol/h)  
- m : constante d'équilibre de Henry

**Rapport molaire :** `Y = y/(1-y)`
- y : fraction molaire du soluté

**Nombre d'étages théoriques :** `N = ln(Y₀/Y_N) / ln(1+A)`
- Y₀ : rapport molaire d'entrée
- Y_N : rapport molaire de sortie

**Taux d'absorption :** `η = (Y₀ - Y_N)/Y₀ × 100%`"""
        
        else:
            return f"""**À propos de l'absorption**

{absorption_info['definition']}

**Questions fréquentes :**
• Comment calculer le nombre d'étages ?
• Quel débit de solvant utiliser ?
• Comment interpréter le diagramme McCabe-Thiele ?
• Comment optimiser l'efficacité ?

Posez-moi une question plus spécifique pour obtenir des détails !"""

    def _get_desorption_response(self, message: str) -> str:
        """Réponses spécifiques à la désorption"""
        desorption_info = self.knowledge_base["desorption"]
        
        if "définition" in message or "qu'est-ce" in message or "c'est quoi" in message:
            return f"""**Désorption - Définition**

{desorption_info['definition']}

**Applications principales :**
{chr(10).join(f'• {app}' for app in desorption_info['applications'])}

**Paramètres clés :**
{chr(10).join(f'• {param}' for param in desorption_info['parametres_cles'])}

L'efficacité dépend du facteur de désorption S = (m × G)/L."""
        
        elif "calcul" in message or "formule" in message:
            return f"""**Formules clés pour la désorption**

**Facteur de désorption :** `S = (m × G)/L`
- m : constante d'équilibre de Henry
- G : débit molaire gaz de stripping (mol/h)
- L : débit molaire liquide (mol/h)

**Rapport molaire :** `X = x/(1-x)`
- x : fraction molaire du soluté dans le liquide

**Nombre d'étages théoriques :** `N = ln(X₀/X_N) / ln(1+S)`
- X₀ : rapport molaire d'entrée
- X_N : rapport molaire de sortie

**Taux de désorption :** `η = (X₀ - X_N)/X₀ × 100%`"""
        
        else:
            return f"""**À propos de la désorption**

{desorption_info['definition']}

La désorption est l'inverse de l'absorption : on extrait un composé du liquide vers le gaz.

**Principe :** Un gaz de stripping (souvent de la vapeur d'eau ou de l'air) traverse le liquide pour entraîner le composé à récupérer.

**Facteur clé :** S = (m × G)/L - plus S est élevé, plus la désorption est efficace."""

    def _get_mccabe_response(self, message: str) -> str:
        """Réponses sur le diagramme McCabe-Thiele"""
        return """**Diagramme McCabe-Thiele**

Le diagramme McCabe-Thiele est une méthode graphique pour déterminer le nombre d'étages théoriques.

**Éléments du diagramme :**
• Courbe d'équilibre Y = m×X
• Droite opératoire
• Construction par étages
• Points d'intersection

**Interprétation :**
• Plus la courbe d'équilibre est éloignée de la droite opératoire, moins d'étages sont nécessaires
• La pente de la droite opératoire dépend des débits L' et G'
• Chaque marche représente un étage théorique

💡 **Astuce :** Plus l'écart entre la courbe d'équilibre et la droite opératoire est grand, moins d'étages sont nécessaires !"""

    def _get_stages_response(self, message: str) -> str:
        """Réponses sur les étages théoriques"""
        return """**Étages théoriques - Concepts clés**

**Définition :** Un étage théorique est une unité où l'équilibre thermodynamique est atteint entre les phases gaz et liquide.

**Calcul du nombre d'étages :**

**Pour l'absorption :**
```
N = ln(Y₀/Y_N) / ln(1+A)
```
où A = L'/(m × G')

**Pour la désorption :**
```
N = ln(X₀/X_N) / ln(1+S)  
```
où S = (m × G)/L

**Facteurs d'influence :**
• **Débit relatif :** L'/G' ou L/G
• **Sélectivité :** constante m
• **Objectif :** taux d'épuration souhaité"""

    def _get_optimization_response(self, message: str) -> str:
        """Réponses sur l'optimisation"""
        return """**Optimisation des procédés**

**Paramètres à optimiser :**
• Rapport L'/G' (débit solvant/gaz)
• Température d'opération
• Pression du système
• Type de garnissage

**Stratégies d'optimisation :**
• Augmenter le débit de solvant pour améliorer l'efficacité
• Optimiser la température pour favoriser l'équilibre
• Choisir le bon solvant (faible m pour absorption)
• Dimensionner correctement la colonne

**Règles pratiques :**
• Facteur d'absorption A > 1.4 pour une bonne efficacité
• Facteur de désorption S > 1.4 pour une bonne efficacité
• Compromis entre efficacité et coût opératoire"""
    
    def _get_export_response(self, message: str) -> str:
        """Réponses sur l'export des résultats"""
        return """**Export des résultats 📊**

Vous pouvez exporter vos résultats de calcul dans plusieurs formats :

**📄 Export TXT :**
• Rapport textuel complet
• Tous les paramètres et résultats
• Format lisible et imprimable
• Cliquez sur "Exporter TXT" après un calcul

**📊 Export Excel (.xlsx) :**
• Fichier Excel professionnel
• Feuilles multiples (Résumé, Paramètres, Étages)
• Formatage et styles
• Cliquez sur "Exporter Excel" après un calcul
• Chaque export a un nom unique avec timestamp

**💡 Astuce :** Les exports sont automatiques et se téléchargent immédiatement !

**📝 Contenu de l'export :**
• Paramètres d'entrée
• Résultats de simulation
• Détails de chaque étage
• Performances du procédé"""

    def _get_history_response(self, message: str) -> str:
        """Réponses sur l'historique"""
        return """**Historique des calculs 📚**

Le site sauvegarde automatiquement tous vos calculs !

**📋 Accès à l'historique :**
• Menu "Historique" dans la navigation
• Liste de tous vos calculs passés
• Filtrage par type (absorption/désorption)
• Recherche par date

**🔍 Informations disponibles :**
• Date et heure du calcul
• Type de procédé
• Paramètres utilisés
• Résultats obtenus
• Nombre d'étages calculés

**💾 Fonctionnalités :**
• Consulter les détails
• Réutiliser les paramètres
• Comparer les résultats
• Exporter à nouveau

**💡 Astuce :** Connectez-vous pour sauvegarder votre historique de manière permanente !"""

    def _get_general_site_response(self) -> str:
        """Réponse générale sur le site"""
        return """**À propos de ce site 🌐**

Bienvenue sur la plateforme de calculs d'absorption et de désorption !

**🎯 Fonctionnalités principales :**
• **Calculs d'absorption** : Déterminez le nombre d'étages théoriques
• **Calculs de désorption** : Optimisez vos procédés de stripping
• **Diagrammes McCabe-Thiele** : Visualisation graphique interactive
• **Export de résultats** : Excel et TXT
• **Historique** : Sauvegarde automatique de vos calculs

**📊 Visualisations :**
• Diagramme McCabe-Thiele
• Évolution des concentrations
• Profil 3D de la colonne

**🔧 Outils :**
• Simulateur interactif
• Assistant IA (moi !)
• Gestion de profil utilisateur
• Tableau de bord personnalisé

**💡 Questions fréquentes :**
• "Comment calculer le nombre d'étages ?"
• "Comment interpréter le diagramme McCabe-Thiele ?"
• "Comment exporter mes résultats ?"
• "Comment optimiser mon procédé ?"

Posez-moi une question spécifique ! 😊"""

    def _get_greeting_response(self) -> str:
        """Réponse de salutation"""
        return """**Bonjour ! 👋**

Je suis votre assistant spécialisé en **calculs d'absorption et de désorption** !

**🎯 Je peux vous aider avec :**
• Calculs d'absorption et désorption
• Diagrammes McCabe-Thiele
• Optimisation des procédés
• Interprétation des résultats
• Utilisation du site

**💡 Exemples de questions :**
• "Comment calculer le nombre d'étages théoriques ?"
• "Qu'est-ce que le diagramme McCabe-Thiele ?"
• "Comment optimiser mon procédé d'absorption ?"
• "Comment exporter mes résultats en Excel ?"
• "Quelle est la différence entre absorption et désorption ?"

**🚀 Posez-moi votre question !**
Je suis là pour vous aider avec vos calculs chimiques ! 🧪✨"""

    def _get_help_response(self) -> str:
        """Réponse d'aide générale"""
        return """**Aide - Comment utiliser le site ? 🆘**

**📝 Pour effectuer un calcul :**
1. Choisissez "Absorption" ou "Désorption" dans le menu
2. Remplissez les paramètres requis (débits, constantes, fractions)
3. Cliquez sur "Lancer la simulation"
4. Consultez les résultats et visualisations

**📊 Paramètres requis :**

**Absorption :**
• Débit gaz G' (mol/h)
• Débit solvant L' (mol/h)
• Constante d'équilibre m
• Fraction molaire entrée y₀
• Fraction objectif y_obj

**Désorption :**
• Débit gaz G (mol/h)
• Débit liquide L (mol/h)
• Constante d'équilibre m
• Fraction molaire entrée x₀
• Fraction objectif x_obj

**💾 Export des résultats :**
• Cliquez sur "Exporter TXT" pour un rapport textuel
• Cliquez sur "Exporter Excel" pour un fichier .xlsx

**📚 Historique :**
• Accédez à "Historique" pour voir vos calculs passés
• Réutilisez les paramètres d'un calcul précédent

**🤖 Assistant IA :**
• Posez-moi des questions sur les calculs
• Demandez des explications sur les résultats
• Obtenez de l'aide sur l'utilisation du site

**💡 Besoin d'aide spécifique ?**
Posez-moi une question précise ! 😊"""

# Instance globale du service
ai_assistant_service = AIAssistantService()
