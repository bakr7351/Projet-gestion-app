"""
Routes pour le simulateur McCabe-Thiele standalone
"""
from flask import Blueprint, request, jsonify
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import base64

mccabe_simulator_bp = Blueprint('mccabe_simulator', __name__)


def generate_mccabe_plot(operation, G, L, m_cst, y_in, x_in, target_out):
    """
    Génère un graphique McCabe-Thiele
    Code adapté avec les couleurs du site
    """
    # Conversion en rapports molaires
    Y_in = y_in / (1 - y_in)
    X_in = x_in / (1 - x_in) if x_in != 1 else 0
    
    plt.figure(figsize=(9, 8))
    plt.style.use('dark_background')
    
    error_msg = None
    stage_count = 0
    
    if operation == "absorption":
        y_out = target_out
        Y_out = y_out / (1 - y_out)
        X_out = X_in + (G / L) * (Y_in - Y_out)
        
        # Vérification du pincement
        if Y_out <= m_cst * X_in or Y_in <= m_cst * X_out:
            error_msg = "Erreur (Pincement) : La droite opératoire croise la courbe d'équilibre."
        
        X_eq_max = max(X_out, Y_in / m_cst) * 1.2
        
        # Courbe d'équilibre
        X_line = np.linspace(0, X_eq_max, 100)
        Y_eq_line = m_cst * X_line
        plt.plot(X_line, Y_eq_line, color='lime', linewidth=2.5, label="Courbe d'équilibre (Y = mX)")
        
        # Droite opératoire
        plt.plot([X_in, X_out], [Y_out, Y_in], color='#17a2b8', linewidth=2.5, 
                label="Droite opératoire (Absorption)")
        
        if not error_msg:
            # Construction des gradins
            x_steps, y_steps = [X_in], [Y_out]
            Y_c = Y_out
            
            while Y_c < Y_in and stage_count < 50:
                stage_count += 1
                # Horizontal vers équilibre
                X_eq = Y_c / m_cst
                x_steps.extend([X_eq, X_eq])
                y_steps.append(Y_c)
                
                # Vertical vers droite opératoire
                Y_op = Y_out + (L / G) * (X_eq - X_in)
                if Y_op >= Y_in:
                    y_steps.append(Y_in)
                    break
                
                y_steps.append(Y_op)
                Y_c = Y_op
            
            plt.plot(x_steps, y_steps, color='magenta', linewidth=1.8, 
                    label=f"Étages = {stage_count}")
            plt.scatter([X_in, X_out], [Y_out, Y_in], color='#17a2b8', zorder=5, s=80, 
                       edgecolors='white', linewidths=2)
        
    elif operation == "desorption":
        x_out = target_out
        X_out = x_out / (1 - x_out) if x_out != 1 else 0
        Y_out = Y_in + (L / G) * (X_in - X_out)
        
        # Vérification du pincement
        if Y_out >= m_cst * X_in or Y_in >= m_cst * X_out:
            error_msg = "Erreur (Pincement) : La droite doit être sous la courbe d'équilibre pour désorber."
        
        X_eq_max = X_in * 1.2
        
        # Courbe d'équilibre
        X_line = np.linspace(0, X_eq_max, 100)
        Y_eq_line = m_cst * X_line
        plt.plot(X_line, Y_eq_line, color='lime', linewidth=2.5, label="Courbe d'équilibre (Y = mX)")
        
        # Droite opératoire
        plt.plot([X_out, X_in], [Y_in, Y_out], color='#ffc107', linewidth=2.5,
                label="Droite opératoire (Désorption)")
        
        if not error_msg:
            # Construction des gradins
            x_steps, y_steps = [X_in], [Y_out]
            X_current, Y_current = X_in, Y_out
            
            while X_current > X_out and stage_count < 50:
                stage_count += 1
                # Horizontal vers équilibre
                X_eq = Y_current / m_cst
                x_steps.append(X_eq)
                y_steps.append(Y_current)
                
                # Vertical vers droite opératoire
                Y_op = Y_in + (L / G) * (X_eq - X_out)
                if X_eq <= X_out:
                    x_steps.append(X_out)
                    y_steps.append(Y_current)
                    break
                
                x_steps.append(X_eq)
                y_steps.append(Y_op)
                X_current = X_eq
                Y_current = Y_op
            
            plt.plot(x_steps, y_steps, color='magenta', linewidth=1.8,
                    label=f"Étages = {stage_count}")
            plt.scatter([X_out, X_in], [Y_in, Y_out], color='#ffc107', zorder=5, s=80,
                       edgecolors='white', linewidths=2)
    
    if error_msg:
        plt.text(0.5, 0.5, error_msg, color='white', fontsize=13, fontweight='bold',
                ha='center', va='center', transform=plt.gca().transAxes,
                bbox=dict(facecolor='#ef4444', alpha=0.9, boxstyle="round,pad=0.8"))
    
    plt.title(f"Méthode de McCabe et Thiele - {operation.capitalize()}", 
             fontsize=16, fontweight='bold', pad=20)
    plt.xlabel("Rapport molaire phase liquide (X)", fontsize=13, fontweight='bold')
    plt.ylabel("Rapport molaire phase gaz (Y)", fontsize=13, fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.4, color='gray')
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.legend(loc='upper left' if operation == 'absorption' else 'lower right',
              fontsize=11, framealpha=0.9)
    plt.tight_layout()
    
    # Sauvegarde en base64
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=120, bbox_inches='tight', facecolor='#1e1e1e')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    
    return plot_url, stage_count, error_msg


@mccabe_simulator_bp.route('/generate', methods=['POST'])
def generate_graph():
    """Endpoint pour générer un graphique McCabe-Thiele"""
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = ['G', 'L', 'm', 'y_in', 'x_in', 'target_out', 'operation']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Champ manquant: {field}'
                }), 400
        
        # Conversion des valeurs
        try:
            G = float(data['G'])
            L = float(data['L'])
            m = float(data['m'])
            y_in = float(data['y_in'])
            x_in = float(data['x_in'])
            target_out = float(data['target_out'])
            operation = data['operation']
            
            if operation not in ['absorption', 'desorption']:
                return jsonify({
                    'success': False,
                    'message': 'Opération invalide (absorption ou desorption)'
                }), 400
            
            if G <= 0 or L <= 0 or m <= 0:
                return jsonify({
                    'success': False,
                    'message': 'Les débits et la constante m doivent être positifs'
                }), 400
            
            if not (0 <= y_in <= 1) or not (0 <= x_in <= 1) or not (0 <= target_out <= 1):
                return jsonify({
                    'success': False,
                    'message': 'Les fractions molaires doivent être entre 0 et 1'
                }), 400
            
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Valeurs numériques invalides'
            }), 400
        
        # Génération du graphique
        plot_url, stage_count, error_msg = generate_mccabe_plot(
            operation, G, L, m, y_in, x_in, target_out
        )
        
        return jsonify({
            'success': True,
            'plot_url': plot_url,
            'stage_count': stage_count,
            'error': error_msg
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de la génération: {str(e)}'
        }), 500
