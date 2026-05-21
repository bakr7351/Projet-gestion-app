"""
Routes pour les calculs d'absorption et de désorption
"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from datetime import datetime
import io
import logging
import numpy as np
import plotly.graph_objects as go
from backend.services.absorption_calculator import (
    simuler_absorption, 
    simuler_desorption,
    generer_rapport_absorption,
    generer_rapport_desorption,
    AbsorptionCalculator
)
from backend.middlewares.access_guard import require_access_choice, check_user_access

calculations_bp = Blueprint('calculations', __name__)
logger = logging.getLogger(__name__)


@calculations_bp.route('/absorption', methods=['POST'])
@require_access_choice
def calculer_absorption():
    """Endpoint pour simuler l'absorption - Accès contrôlé"""
    try:
        # Vérifier le type d'accès
        access_type = check_user_access()
        
        data = request.get_json()
        
        # Validation des données d'entrée
        required_fields = ['G_prime', 'L_prime', 'm', 'y0', 'x0', 'y_objectif']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Champ manquant: {field}'
                }), 400
        
        # Récupérer le type de contact (par défaut: contre-courant)
        contact_type = data.get('contact_type', 'counter-current')
        if contact_type not in ['counter-current', 'cross-current']:
            contact_type = 'counter-current'
        
        # Validation des valeurs
        try:
            G_prime = float(data['G_prime'])
            L_prime = float(data['L_prime'])
            m = float(data['m'])
            y0 = float(data['y0'])
            x0 = float(data['x0'])
            y_objectif = float(data['y_objectif'])
            
            if G_prime <= 0 or L_prime <= 0 or m <= 0:
                return jsonify({
                    'success': False,
                    'message': 'Les débits et la constante m doivent être positifs'
                }), 400
                
            if not (0 <= y0 <= 1) or not (0 <= x0 <= 1) or not (0 <= y_objectif <= 1):
                return jsonify({
                    'success': False,
                    'message': 'Les fractions molaires doivent être entre 0 et 1'
                }), 400
                
            if y_objectif >= y0:
                return jsonify({
                    'success': False,
                    'message': 'La fraction objectif doit être inférieure à la fraction d\'entrée'
                }), 400
                
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Valeurs numériques invalides'
            }), 400
        
        # Simulation avec graphiques McCabe-Thiele
        calculator = AbsorptionCalculator()
        results = calculator.calculate_absorption(
            G_prime=G_prime,
            L_prime=L_prime,
            m=m,
            y0=y0,
            y_obj=y_objectif,
            N=None,  # Calcul automatique du nombre d'étages pour atteindre l'objectif
            contact_type=contact_type  # Nouveau paramètre
        )

        # Auto-save to history for authenticated users (non-blocking)
        try:
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity as _get_identity
            verify_jwt_in_request(optional=True)
            _user_id = _get_identity()
            if _user_id is not None:
                from backend.services.history_service import history_service
                calc_results = results.get('calculation_results', {})
                history_service.save_entry(
                    user_id=int(_user_id),
                    calc_type='absorption',
                    input_params={
                        'G_prime': G_prime,
                        'L_prime': L_prime,
                        'm': m,
                        'y0': y0,
                        'x0': x0,
                        'y_objectif': y_objectif,
                    },
                    result_summary={
                        'nb_etages': calc_results.get('nb_etages') or calc_results.get('nombre_etages'),
                        'taux': calc_results.get('taux_absorption') or calc_results.get('taux'),
                        'quantite': calc_results.get('quantite_absorbee') or calc_results.get('quantite'),
                        'facteur_A': calc_results.get('facteur_absorption') or calc_results.get('facteur_A'),
                    },
                )
        except Exception as _hist_err:
            import logging as _logging
            _logging.getLogger(__name__).warning(
                "Failed to save absorption history: %s", _hist_err
            )

        # Ajouter des informations sur le type d'accès dans la réponse
        response_data = {
            'success': True,
            'data': {
                'calculation_results': results['calculation_results'],
                'mccabe_thiele_graph': results.get('mccabe_thiele_graph'),
                'matplotlib_mccabe_graph': results.get('matplotlib_mccabe_graph'),
                'advanced_plotly_mccabe_graph': results.get('advanced_plotly_mccabe_graph'),
                'surface_3d_graph': results.get('surface_3d_graph'),
                'concentration_evolution_graph': results.get('concentration_evolution_graph'),
                '3d_profile_graph': results.get('3d_profile_graph'),
                'performance': results['performance']
            },
            'access_type': access_type
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors du calcul: {str(e)}'
        }), 500


@calculations_bp.route('/desorption', methods=['POST'])
@require_access_choice
def calculer_desorption():
    """Endpoint pour simuler la désorption - Accès contrôlé"""
    try:
        # Vérifier le type d'accès
        access_type = check_user_access()
        
        data = request.get_json()
        
        # Validation des données d'entrée
        required_fields = ['G', 'L', 'm', 'x0', 'y0', 'x_obj']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Champ manquant: {field}'
                }), 400
        
        # Récupérer le type de contact (par défaut: contre-courant)
        contact_type = data.get('contact_type', 'counter-current')
        if contact_type not in ['counter-current', 'cross-current']:
            contact_type = 'counter-current'
        
        # Validation des valeurs
        try:
            G = float(data['G'])
            L = float(data['L'])
            m = float(data['m'])
            x0 = float(data['x0'])
            y0 = float(data['y0'])
            x_obj = float(data['x_obj'])
            
            if G <= 0 or L <= 0 or m <= 0:
                return jsonify({
                    'success': False,
                    'message': 'Les débits et la constante m doivent être positifs'
                }), 400
                
            if not (0 <= x0 <= 1) or not (0 <= y0 <= 1) or not (0 <= x_obj <= 1):
                return jsonify({
                    'success': False,
                    'message': 'Les fractions molaires doivent être entre 0 et 1'
                }), 400
                
            if x_obj >= x0:
                return jsonify({
                    'success': False,
                    'message': 'La fraction objectif doit être inférieure à la fraction d\'entrée'
                }), 400
                
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Valeurs numériques invalides'
            }), 400
        
        # Simulation avec graphiques McCabe-Thiele
        calculator = AbsorptionCalculator()
        results = calculator.calculate_desorption(
            G=G,
            L=L,
            m=m,
            x0=x0,
            x_obj=x_obj,
            N=None,  # Calcul automatique du nombre d'étages pour atteindre l'objectif
            contact_type=contact_type  # Nouveau paramètre
        )

        # Auto-save to history for authenticated users (non-blocking)
        try:
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity as _get_identity
            verify_jwt_in_request(optional=True)
            _user_id = _get_identity()
            if _user_id is not None:
                from backend.services.history_service import history_service
                calc_results = results.get('calculation_results', {})
                history_service.save_entry(
                    user_id=int(_user_id),
                    calc_type='desorption',
                    input_params={
                        'G': G,
                        'L': L,
                        'm': m,
                        'x0': x0,
                        'y0': y0,
                        'x_obj': x_obj,
                    },
                    result_summary={
                        'nb_etages': calc_results.get('nb_etages') or calc_results.get('nombre_etages'),
                        'taux': calc_results.get('taux_desorption') or calc_results.get('taux'),
                        'quantite': calc_results.get('quantite_desorbee') or calc_results.get('quantite'),
                        'facteur_S': calc_results.get('facteur_desorption') or calc_results.get('facteur_S'),
                    },
                )
        except Exception as _hist_err:
            import logging as _logging
            _logging.getLogger(__name__).warning(
                "Failed to save desorption history: %s", _hist_err
            )

        # Ajouter des informations sur le type d'accès dans la réponse
        response_data = {
            'success': True,
            'data': {
                'calculation_results': results['calculation_results'],
                'mccabe_thiele_graph': results.get('mccabe_thiele_graph'),
                'matplotlib_mccabe_graph': results.get('matplotlib_mccabe_graph'),
                'advanced_plotly_mccabe_graph': results.get('advanced_plotly_mccabe_graph'),
                'surface_3d_graph': results.get('surface_3d_graph'),
                'concentration_evolution_graph': results.get('concentration_evolution_graph'),
                '3d_profile_graph': results.get('3d_profile_graph'),
                'performance': results['performance']
            },
            'access_type': access_type
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors du calcul: {str(e)}'
        }), 500


@calculations_bp.route('/export/excel/absorption', methods=['POST'])
def exporter_excel_absorption():
    """Exporter les résultats d'absorption en format Excel (.xlsx)"""
    try:
        from backend.services.excel_export_service import generate_absorption_excel
        data = request.get_json() or {}
        
        logger.info(f"Excel export request received - data keys: {list(data.keys())}")

        if 'results' not in data:
            logger.error("Missing 'results' in export request")
            return jsonify({'success': False, 'message': 'Résultats manquants'}), 400

        graphs_b64 = data.get('graphs', {})  # optional {mccabe, concentration, profile_3d}
        logger.info(f"Graphs received for export: {list(graphs_b64.keys())}")
        
        if 'mccabe' in graphs_b64:
            mccabe_size = len(graphs_b64['mccabe'])
            logger.info(f"McCabe-Thiele diagram captured from web interface: {mccabe_size} characters")
        else:
            logger.info("No McCabe-Thiele diagram captured from web interface")
        
        xlsx_bytes = generate_absorption_excel(data['results'], graphs_b64 or None)
        logger.info(f"Excel file generated successfully - size: {len(xlsx_bytes)} bytes")

        buf = io.BytesIO(xlsx_bytes)
        buf.seek(0)
        filename = f"absorption_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        logger.info(f"Sending Excel file: {filename}")
        
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        logger.error(f"Excel export error: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'Erreur export Excel: {str(e)}'}), 500


@calculations_bp.route('/export/excel/desorption', methods=['POST'])
def exporter_excel_desorption():
    """Exporter les résultats de désorption en format Excel (.xlsx)"""
    try:
        from backend.services.excel_export_service import generate_desorption_excel
        data = request.get_json() or {}
        
        logger.info(f"Desorption Excel export request received - data keys: {list(data.keys())}")

        if 'results' not in data:
            logger.error("Missing 'results' in desorption export request")
            return jsonify({'success': False, 'message': 'Résultats manquants'}), 400

        graphs_b64 = data.get('graphs', {})
        logger.info(f"Graphs received for desorption export: {list(graphs_b64.keys())}")
        
        if 'mccabe' in graphs_b64:
            mccabe_size = len(graphs_b64['mccabe'])
            logger.info(f"Desorption McCabe-Thiele diagram captured from web interface: {mccabe_size} characters")
        else:
            logger.info("No McCabe-Thiele diagram captured from web interface (desorption)")
        
        xlsx_bytes = generate_desorption_excel(data['results'], graphs_b64 or None)
        logger.info(f"Desorption Excel file generated successfully - size: {len(xlsx_bytes)} bytes")

        buf = io.BytesIO(xlsx_bytes)
        buf.seek(0)
        filename = f"desorption_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        logger.info(f"Sending desorption Excel file: {filename}")
        
        return send_file(
            buf,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        logger.error(f"Desorption Excel export error: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'Erreur export Excel: {str(e)}'}), 500


@calculations_bp.route('/export/absorption', methods=['POST'])
@jwt_required()
def exporter_absorption():
    """Exporter les résultats d'absorption en format texte"""
    try:
        data = request.get_json()
        
        if 'results' not in data:
            return jsonify({
                'success': False,
                'message': 'Résultats manquants'
            }), 400
        
        results = data['results']
        rapport_text, timestamp = generer_rapport_absorption(results)
        
        # Créer un fichier en mémoire
        rapport_bytes = io.BytesIO()
        rapport_bytes.write(rapport_text.encode('utf-8'))
        rapport_bytes.seek(0)
        
        return send_file(
            rapport_bytes,
            mimetype='text/plain',
            as_attachment=True,
            download_name=f'rapport_absorption_{timestamp[:10]}.txt'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de l\'export: {str(e)}'
        }), 500


@calculations_bp.route('/export/desorption', methods=['POST'])
@jwt_required()
def exporter_desorption():
    """Exporter les résultats de désorption en format texte"""
    try:
        data = request.get_json()
        
        if 'results' not in data:
            return jsonify({
                'success': False,
                'message': 'Résultats manquants'
            }), 400
        
        results = data['results']
        rapport_text, timestamp = generer_rapport_desorption(results)
        
        # Créer un fichier en mémoire
        rapport_bytes = io.BytesIO()
        rapport_bytes.write(rapport_text.encode('utf-8'))
        rapport_bytes.seek(0)
        
        return send_file(
            rapport_bytes,
            mimetype='text/plain',
            as_attachment=True,
            download_name=f'rapport_desorption_{timestamp[:10]}.txt'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors de l\'export: {str(e)}'
        }), 500


# ============================================================================
# ROUTES POUR COURANT CROISÉ
# ============================================================================

@calculations_bp.route('/absorption-cross-current', methods=['POST'])
@require_access_choice
def calculer_absorption_cross_current():
    """Endpoint pour simuler l'absorption à courant croisé"""
    try:
        access_type = check_user_access()
        data = request.get_json()
        
        # Validation des données d'entrée
        required_fields = ['G_prime', 'L_prime', 'm', 'y0', 'x0', 'y_objectif']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Champ manquant: {field}'
                }), 400
        
        # Validation des valeurs
        try:
            G_prime = float(data['G_prime'])
            L_prime = float(data['L_prime'])
            m = float(data['m'])
            y0 = float(data['y0'])
            x0 = float(data['x0'])
            y_objectif = float(data['y_objectif'])
            
            if G_prime <= 0 or L_prime <= 0 or m <= 0:
                return jsonify({
                    'success': False,
                    'message': 'Les débits et la constante m doivent être positifs'
                }), 400
                
            if not (0 <= y0 <= 1) or not (0 <= x0 <= 1) or not (0 <= y_objectif <= 1):
                return jsonify({
                    'success': False,
                    'message': 'Les fractions molaires doivent être entre 0 et 1'
                }), 400
                
            if y_objectif >= y0:
                return jsonify({
                    'success': False,
                    'message': 'La fraction objectif doit être inférieure à la fraction d\'entrée'
                }), 400
                
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Valeurs numériques invalides'
            }), 400
        
        # Simulation avec courant croisé
        from backend.services.cross_current_calculator import CrossCurrentCalculator
        calculator = CrossCurrentCalculator()
        results = calculator.calculate_absorption_cross_current(
            G_prime=G_prime,
            L_prime=L_prime,
            m=m,
            y0=y0,
            y_obj=y_objectif,
            N=None  # Calcul automatique du nombre d'étages
        )

        # Auto-save to history for authenticated users
        try:
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity as _get_identity
            verify_jwt_in_request(optional=True)
            _user_id = _get_identity()
            if _user_id is not None:
                from backend.services.history_service import history_service
                calc_results = results.get('calculation_results', {})
                history_service.save_entry(
                    user_id=int(_user_id),
                    calc_type='absorption',
                    input_params={
                        'G_prime': G_prime,
                        'L_prime': L_prime,
                        'm': m,
                        'y0': y0,
                        'x0': x0,
                        'y_objectif': y_objectif,
                        'flow_type': 'cross-current'
                    },
                    result_summary={
                        'nb_etages': calc_results.get('nb_etages'),
                        'taux': calc_results.get('taux'),
                        'quantite': calc_results.get('quantite'),
                        'facteur_A': calc_results.get('facteur_A'),
                    },
                )
        except Exception as _hist_err:
            import logging as _logging
            _logging.getLogger(__name__).warning(
                "Failed to save absorption history: %s", _hist_err
            )

        response_data = {
            'success': True,
            'data': {
                'calculation_results': results['calculation_results'],
                'matplotlib_mccabe_graph': results.get('matplotlib_mccabe_graph'),
                'concentration_evolution_graph': results.get('concentration_evolution_graph'),
                '3d_profile_graph': results.get('3d_profile_graph'),
                'performance': results['performance']
            },
            'access_type': access_type
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors du calcul: {str(e)}'
        }), 500


@calculations_bp.route('/desorption-cross-current', methods=['POST'])
@require_access_choice
def calculer_desorption_cross_current():
    """Endpoint pour simuler la désorption à courant croisé"""
    try:
        access_type = check_user_access()
        data = request.get_json()
        
        # Validation des données d'entrée
        required_fields = ['G', 'L', 'm', 'x0', 'y0', 'x_obj']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Champ manquant: {field}'
                }), 400
        
        # Validation des valeurs
        try:
            G = float(data['G'])
            L = float(data['L'])
            m = float(data['m'])
            x0 = float(data['x0'])
            y0 = float(data['y0'])
            x_obj = float(data['x_obj'])
            
            if G <= 0 or L <= 0 or m <= 0:
                return jsonify({
                    'success': False,
                    'message': 'Les débits et la constante m doivent être positifs'
                }), 400
                
            if not (0 <= x0 <= 1) or not (0 <= y0 <= 1) or not (0 <= x_obj <= 1):
                return jsonify({
                    'success': False,
                    'message': 'Les fractions molaires doivent être entre 0 et 1'
                }), 400
                
            if x_obj >= x0:
                return jsonify({
                    'success': False,
                    'message': 'La fraction objectif doit être inférieure à la fraction d\'entrée'
                }), 400
                
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Valeurs numériques invalides'
            }), 400
        
        # Simulation avec courant croisé
        from backend.services.cross_current_calculator import CrossCurrentCalculator
        calculator = CrossCurrentCalculator()
        results = calculator.calculate_desorption_cross_current(
            G=G,
            L=L,
            m=m,
            x0=x0,
            x_obj=x_obj,
            N=None  # Calcul automatique du nombre d'étages
        )

        # Auto-save to history for authenticated users
        try:
            from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity as _get_identity
            verify_jwt_in_request(optional=True)
            _user_id = _get_identity()
            if _user_id is not None:
                from backend.services.history_service import history_service
                calc_results = results.get('calculation_results', {})
                history_service.save_entry(
                    user_id=int(_user_id),
                    calc_type='desorption',
                    input_params={
                        'G': G,
                        'L': L,
                        'm': m,
                        'x0': x0,
                        'y0': y0,
                        'x_obj': x_obj,
                        'flow_type': 'cross-current'
                    },
                    result_summary={
                        'nb_etages': calc_results.get('nb_etages'),
                        'taux': calc_results.get('taux'),
                        'quantite': calc_results.get('quantite'),
                        'facteur_S': calc_results.get('facteur_S'),
                    },
                )
        except Exception as _hist_err:
            import logging as _logging
            _logging.getLogger(__name__).warning(
                "Failed to save desorption history: %s", _hist_err
            )

        response_data = {
            'success': True,
            'data': {
                'calculation_results': results['calculation_results'],
                'matplotlib_mccabe_graph': results.get('matplotlib_mccabe_graph'),
                'concentration_evolution_graph': results.get('concentration_evolution_graph'),
                '3d_profile_graph': results.get('3d_profile_graph'),
                'performance': results['performance']
            },
            'access_type': access_type
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur lors du calcul: {str(e)}'
        }), 500


# ============================================================================
# CROSS-CURRENT SIMULATOR ENDPOINT
# ============================================================================

@calculations_bp.route('/cross-current/calculate', methods=['POST'])
def cross_current_calculate():
    """Endpoint pour le simulateur d'exercices à courant croisé"""
    try:
        data = request.get_json()
        exercice = data.get('exercice', '1')
        
        def y_to_Y(y):
            return y / (1 - y)
        
        def Y_to_y(Y):
            return Y / (1 + Y)
        
        def x_to_X(x):
            return x / (1 - x) if x < 1 else float('inf')
        
        def X_to_x(X):
            return X / (1 + X) if X != float('inf') else 1
        
        def calcul_absorption_automatique(G_prime, L_prime, m, y0, y_obj):
            """Calcul automatique absorption courants croisés jusqu'à objectif"""
            Y0 = y_to_Y(y0)
            Y_obj = y_to_Y(y_obj)
            A = L_prime / (m * G_prime)
            pente = -L_prime / G_prime
            
            Y_vals = [Y0]
            X_vals = [0.0]
            convergence = False
            etages = 0
            
            # Calcul étage par étage jusqu'à atteindre l'objectif
            for i in range(1, 51):  # Maximum 50 étages
                Y_prev = Y_vals[-1]
                Yi = Y_prev / (1 + A)
                Xi = Yi / m
                yi = Y_to_y(Yi)
                
                Y_vals.append(Yi)
                X_vals.append(Xi)
                etages = i
                
                # Vérifier si objectif atteint
                if yi <= y_obj:
                    convergence = True
                    break
            
            taux = (Y0 - Y_vals[-1]) / Y0
            quantite_absorbee = G_prime * (Y0 - Y_vals[-1])
            
            return {
                'type': 'absorption',
                'G_prime': G_prime,
                'L_prime': L_prime,
                'm': m,
                'y0': y0,
                'y_obj': y_obj,
                'Y0': Y0,
                'A': A,
                'pente': pente,
                'N_etages': etages,
                'Y_vals': Y_vals,
                'X_vals': X_vals,
                'taux': taux,
                'quantite_absorbee': quantite_absorbee,
                'convergence': convergence,
                'objectif_atteint': convergence
            }
        
        def calcul_desorption_automatique(L_prime, G_prime, m, x0, x_obj):
            """Calcul automatique désorption courants croisés jusqu'à objectif"""
            X0 = x_to_X(x0)
            X_obj = x_to_X(x_obj)
            pente = G_prime / L_prime
            
            X_vals = [X0]
            Y_vals = [0.0]
            convergence = False
            etages = 0
            X_courant = X0
            
            # Calcul étage par étage jusqu'à atteindre l'objectif
            for i in range(1, 51):  # Maximum 50 étages
                # À courant croisé: chaque étage reçoit du gaz frais (Y=0)
                # Intersection analytique: m*X = pente*(X_courant - X)
                # X_sortant = (pente * X_courant) / (m + pente)
                X_sortant = (pente * X_courant) / (m + pente)
                Y_sortant = m * X_sortant
                
                # Vérifier la progression
                if X_sortant < 0 or X_sortant >= X_courant:
                    break
                
                x_sortie = X_to_x(X_sortant)
                
                X_vals.append(X_sortant)
                Y_vals.append(Y_sortant)
                etages = i
                X_courant = X_sortant
                
                # Vérifier si objectif atteint
                if x_sortie <= x_obj:
                    convergence = True
                    break
            
            taux = (X0 - X_vals[-1]) / X0 if X0 > 0 else 0
            quantite_desorbee = L_prime * (X0 - X_vals[-1])
            
            return {
                'type': 'desorption',
                'L_prime': L_prime,
                'G_prime': G_prime,
                'm': m,
                'x0': x0,
                'x_obj': x_obj,
                'X0': X0,
                'pente': pente,
                'N_etages': etages,
                'X_vals': X_vals,
                'Y_vals': Y_vals,
                'taux': taux,
                'quantite_desorbee': quantite_desorbee,
                'convergence': convergence,
                'objectif_atteint': convergence
            }
        
        def calcul_exercice1():
            G_prime = 150.0
            L_prime = 200.0
            m = 0.5
            y0 = 0.06
            N_etages = 3
            Y0 = y_to_Y(y0)
            A = L_prime / (m * G_prime)
            pente = -L_prime / G_prime
            Y_vals = [Y0]
            X_vals = [0.0]
            for i in range(1, N_etages + 1):
                Y_prev = Y_vals[-1]
                Yi = Y_prev / (1 + A)
                Xi = Yi / m
                Y_vals.append(Yi)
                X_vals.append(Xi)
            taux = (Y0 - Y_vals[-1]) / Y0
            benz_abs = G_prime * (Y0 - Y_vals[-1])
            n_min = int(np.ceil(np.log(10) / np.log(1 + A)))
            return {
                'type': 'absorption',
                'G_prime': G_prime,
                'L_prime': L_prime,
                'm': m,
                'y0': y0,
                'Y0': Y0,
                'A': A,
                'pente': pente,
                'N_etages': N_etages,
                'Y_vals': Y_vals,
                'X_vals': X_vals,
                'taux': taux,
                'benz_abs': benz_abs,
                'n_min': n_min,
                'suffisant': taux >= 0.9
            }
        
        def calcul_exercice2():
            G_prime = 500.0
            L_prime = 800.0
            m = 25.0
            y0 = 0.04
            y_obj = 0.004
            Y0 = y0
            A = L_prime / (m * G_prime)
            pente = -L_prime / G_prime
            n_necessaire = np.ceil(np.log(y0 / y_obj) / np.log(1 + A))
            N_etages = int(n_necessaire)
            Y_vals = [Y0]
            X_vals = [0.0]
            for i in range(1, N_etages + 1):
                Y_prev = Y_vals[-1]
                Yi = Y_prev / (1 + A)
                Xi = Yi / m
                Y_vals.append(Yi)
                X_vals.append(Xi)
            taux = (Y0 - Y_vals[-1]) / Y0
            L_tot = N_etages * L_prime
            debit_vol = (L_tot * 18.0) / 1000.0
            return {
                'type': 'absorption',
                'G_prime': G_prime,
                'L_prime': L_prime,
                'm': m,
                'y0': y0,
                'y_obj': y_obj,
                'Y0': Y0,
                'A': A,
                'pente': pente,
                'N_etages': N_etages,
                'Y_vals': Y_vals,
                'X_vals': X_vals,
                'taux': taux,
                'L_tot': L_tot,
                'debit_vol': debit_vol,
                'n_necessaire': n_necessaire
            }
        
        def calcul_exercice3():
            L_prime = 100.0
            G_prime = 150.0
            m = 1.2
            x0 = 0.05
            N_etages = 3
            X0 = x0 / (1 - x0)
            S = (m * G_prime) / L_prime
            pente = L_prime / G_prime
            X_vals = [X0]
            Y_vals = [0.0]
            for i in range(1, N_etages + 1):
                X_prev = X_vals[-1]
                Xi = X_prev / (1 + S)
                Yi = m * Xi
                X_vals.append(Xi)
                Y_vals.append(Yi)
            taux = (X0 - X_vals[-1]) / X0
            NH3_desorbe = L_prime * (X0 - X_vals[-1])
            return {
                'type': 'desorption',
                'L_prime': L_prime,
                'G_prime': G_prime,
                'm': m,
                'x0': x0,
                'X0': X0,
                'S': S,
                'pente': pente,
                'N_etages': N_etages,
                'X_vals': X_vals,
                'Y_vals': Y_vals,
                'taux': taux,
                'NH3_desorbe': NH3_desorbe
            }
        
        def generer_graphique_absorption(Y_vals, X_vals, m, pente, titre):
            fig = go.Figure()
            X_max = max(X_vals) * 1.2 if X_vals else 0.01
            X_eq = np.linspace(0, X_max, 100)
            Y_eq = m * X_eq
            fig.add_trace(go.Scatter(x=X_eq, y=Y_eq, mode='lines', name=f'Équilibre: Y = {m}·X', line=dict(color='blue', width=2)))
            for i in range(len(Y_vals) - 1):
                Y_start = Y_vals[i]
                X_end = X_vals[i+1]
                Y_end = Y_vals[i+1]
                X_line = np.linspace(0, X_end, 50)
                Y_line = Y_start + pente * X_line
                fig.add_trace(go.Scatter(x=X_line, y=Y_line, mode='lines', name='Droite opératoire' if i == 0 else None, line=dict(color='red', width=2, dash='dash'), showlegend=(i == 0)))
                fig.add_trace(go.Scatter(x=[X_end], y=[Y_end], mode='markers', name=f'Étage {i+1}', marker=dict(color='red', size=10), showlegend=True))
            for i in range(1, len(Y_vals)):
                X_point = X_vals[i]
                Y_point = Y_vals[i]
                X_line_gray = np.linspace(0, X_point, 20)
                Y_line_gray = [Y_point] * len(X_line_gray)
                fig.add_trace(go.Scatter(x=X_line_gray, y=Y_line_gray, mode='lines', line=dict(color='gray', width=1, dash='dot'), showlegend=False, hoverinfo='skip'))
            fig.update_layout(title=titre, xaxis_title='X (rapport molaire liquide)', yaxis_title='Y (rapport molaire gaz)', hovermode='closest', template='plotly_white', height=600, width=900, font=dict(size=12))
            return fig.to_json()
        
        def generer_graphique_evolution_absorption(Y_vals, X_vals, titre):
            fig = go.Figure()
            etages = list(range(len(Y_vals)))
            fig.add_trace(go.Scatter(x=etages, y=Y_vals, mode='lines+markers', name='Gaz (Y)', line=dict(color='green', width=3), marker=dict(size=8)))
            fig.add_trace(go.Scatter(x=etages, y=X_vals, mode='lines+markers', name='Liquide (X)', line=dict(color='blue', width=3), marker=dict(size=8)))
            fig.update_layout(title=titre, xaxis_title='Numéro d\'étage (0 = Entrée liquide)', yaxis_title='Rapport molaire', hovermode='closest', template='plotly_white', height=500, width=700, font=dict(size=12), legend=dict(x=0.7, y=0.95))
            return fig.to_json()
        
        def generer_schema_colonne_absorption(resultats, titre):
            fig = go.Figure()
            col_x = [2, 4, 4, 2, 2]
            col_y = [1, 1, 5, 5, 1]
            fig.add_trace(go.Scatter(x=col_x, y=col_y, fill='toself', fillcolor='rgba(100, 150, 200, 0.3)', line=dict(color='blue', width=3), name='Colonne', hoverinfo='skip'))
            n_etages = resultats['N_etages']
            fig.add_annotation(x=3, y=3, text=f"<b>N = {n_etages}<br>Étages</b>", showarrow=False, font=dict(size=16, color='#FF9500'), bgcolor='#FFD700', bordercolor='#FF9500', borderwidth=2, borderpad=10)
            fig.add_annotation(x=0.5, y=4.5, text=f"<b>Gaz Entrant</b><br>G' = {resultats['G_prime']:.1f} mol/h<br>Y<sub>in</sub> = {resultats['Y_vals'][0]:.6f}", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='green', ax=50, ay=0, font=dict(size=10), bgcolor='white', bordercolor='green', borderwidth=2, borderpad=8)
            fig.add_annotation(x=5.5, y=4.5, text=f"<b>Gaz Sortant</b><br>G' = {resultats['G_prime']:.1f} mol/h<br>Y<sub>out</sub> = {resultats['Y_vals'][-1]:.6f}", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='green', ax=-50, ay=0, font=dict(size=10), bgcolor='white', bordercolor='green', borderwidth=2, borderpad=8)
            fig.add_annotation(x=3, y=6.2, text=f"<b>Liquide Entrant</b><br>L' = {resultats['L_prime']:.1f} mol/h<br>X<sub>in</sub> = 0.0000", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='blue', ax=0, ay=-30, font=dict(size=10), bgcolor='white', bordercolor='blue', borderwidth=2, borderpad=8)
            fig.add_annotation(x=3, y=-0.2, text=f"<b>Liquide Sortant</b><br>L' = {resultats['L_prime']:.1f} mol/h<br>X<sub>out</sub> = {resultats['X_vals'][-1]:.6f}", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='blue', ax=0, ay=30, font=dict(size=10), bgcolor='white', bordercolor='blue', borderwidth=2, borderpad=8)
            fig.update_layout(title=titre, xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 7]), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 7]), hovermode='closest', template='plotly_white', height=600, width=700, font=dict(size=11), showlegend=False, margin=dict(l=50, r=50, t=80, b=50))
            return fig.to_json()
        
        def generer_schema_colonne_desorption(resultats, titre):
            fig = go.Figure()
            col_x = [2, 4, 4, 2, 2]
            col_y = [1, 1, 5, 5, 1]
            fig.add_trace(go.Scatter(x=col_x, y=col_y, fill='toself', fillcolor='rgba(100, 150, 200, 0.3)', line=dict(color='blue', width=3), name='Colonne', hoverinfo='skip'))
            n_etages = resultats['N_etages']
            fig.add_annotation(x=3, y=3, text=f"<b>N = {n_etages}<br>Étages</b>", showarrow=False, font=dict(size=16, color='#FF9500'), bgcolor='#FFD700', bordercolor='#FF9500', borderwidth=2, borderpad=10)
            fig.add_annotation(x=0.5, y=4.5, text=f"<b>Gaz Entrant</b><br>G' = {resultats['G_prime']:.1f} mol/h<br>Y<sub>in</sub> = 0.0000 (pur)", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='green', ax=50, ay=0, font=dict(size=10), bgcolor='white', bordercolor='green', borderwidth=2, borderpad=8)
            fig.add_annotation(x=5.5, y=4.5, text=f"<b>Gaz Sortant</b><br>G' = {resultats['G_prime']:.1f} mol/h<br>Y<sub>out</sub> = {resultats['Y_vals'][-1]:.6f}", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='green', ax=-50, ay=0, font=dict(size=10), bgcolor='white', bordercolor='green', borderwidth=2, borderpad=8)
            fig.add_annotation(x=3, y=6.2, text=f"<b>Liquide Entrant</b><br>L' = {resultats['L_prime']:.1f} mol/h<br>X<sub>in</sub> = {resultats['X_vals'][0]:.6f}", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='blue', ax=0, ay=-30, font=dict(size=10), bgcolor='white', bordercolor='blue', borderwidth=2, borderpad=8)
            fig.add_annotation(x=3, y=-0.2, text=f"<b>Liquide Sortant</b><br>L' = {resultats['L_prime']:.1f} mol/h<br>X<sub>out</sub> = {resultats['X_vals'][-1]:.6f}", showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='blue', ax=0, ay=30, font=dict(size=10), bgcolor='white', bordercolor='blue', borderwidth=2, borderpad=8)
            fig.update_layout(title=titre, xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 7]), yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 7]), hovermode='closest', template='plotly_white', height=600, width=700, font=dict(size=11), showlegend=False, margin=dict(l=50, r=50, t=80, b=50))
            return fig.to_json()
        
        # Calcul selon l'exercice ou mode personnalisé
        if exercice == 'custom_absorption':
            # Mode personnalisé pour absorption
            required_fields = ['G_prime', 'L_prime', 'm', 'y0', 'y_obj']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'message': f'Champ manquant pour absorption personnalisée: {field}'
                    }), 400
            
            try:
                G_prime = float(data['G_prime'])
                L_prime = float(data['L_prime'])
                m = float(data['m'])
                y0 = float(data['y0'])
                y_obj = float(data['y_obj'])
                
                if G_prime <= 0 or L_prime <= 0 or m <= 0:
                    return jsonify({
                        'success': False,
                        'message': 'Les débits et la constante m doivent être positifs'
                    }), 400
                    
                if not (0 <= y0 <= 1) or not (0 <= y_obj <= 1):
                    return jsonify({
                        'success': False,
                        'message': 'Les fractions molaires doivent être entre 0 et 1'
                    }), 400
                    
                if y_obj >= y0:
                    return jsonify({
                        'success': False,
                        'message': 'La fraction objectif doit être inférieure à la fraction d\'entrée'
                    }), 400
                    
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Valeurs numériques invalides'
                }), 400
            
            resultats = calcul_absorption_automatique(G_prime, L_prime, m, y0, y_obj)
            plot_url = generer_graphique_absorption(resultats['Y_vals'], resultats['X_vals'], resultats['m'], resultats['pente'], "Absorption Personnalisée - Calcul Automatique")
            plot_evolution_url = generer_graphique_evolution_absorption(resultats['Y_vals'], resultats['X_vals'], "Absorption - Évolution des concentrations")
            plot_schema_url = generer_schema_colonne_absorption(resultats, "Absorption - Schéma de la colonne")
            
        elif exercice == 'custom_desorption':
            # Mode personnalisé pour désorption
            required_fields = ['L_prime', 'G_prime', 'm', 'x0', 'x_obj']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'message': f'Champ manquant pour désorption personnalisée: {field}'
                    }), 400
            
            try:
                L_prime = float(data['L_prime'])
                G_prime = float(data['G_prime'])
                m = float(data['m'])
                x0 = float(data['x0'])
                x_obj = float(data['x_obj'])
                
                if L_prime <= 0 or G_prime <= 0 or m <= 0:
                    return jsonify({
                        'success': False,
                        'message': 'Les débits et la constante m doivent être positifs'
                    }), 400
                    
                if not (0 <= x0 <= 1) or not (0 <= x_obj <= 1):
                    return jsonify({
                        'success': False,
                        'message': 'Les fractions molaires doivent être entre 0 et 1'
                    }), 400
                    
                if x_obj >= x0:
                    return jsonify({
                        'success': False,
                        'message': 'La fraction objectif doit être inférieure à la fraction d\'entrée'
                    }), 400
                    
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': 'Valeurs numériques invalides'
                }), 400
            
            resultats = calcul_desorption_automatique(L_prime, G_prime, m, x0, x_obj)
            plot_url = generer_graphique_absorption(resultats['Y_vals'], resultats['X_vals'], resultats['m'], resultats['pente'], "Désorption Personnalisée - Calcul Automatique")
            plot_evolution_url = generer_graphique_evolution_absorption(resultats['Y_vals'], resultats['X_vals'], "Désorption - Évolution des concentrations")
            plot_schema_url = generer_schema_colonne_desorption(resultats, "Désorption - Schéma de la colonne")
            
        elif exercice == '1':
            resultats = calcul_exercice1()
            plot_url = generer_graphique_absorption(resultats['Y_vals'], resultats['X_vals'], resultats['m'], resultats['pente'], "Exercice 1 - Absorption")
            plot_evolution_url = generer_graphique_evolution_absorption(resultats['Y_vals'], resultats['X_vals'], "Exercice 1 - Évolution des concentrations")
            plot_schema_url = generer_schema_colonne_absorption(resultats, "Exercice 1 - Schéma de la colonne")
        elif exercice == '2':
            resultats = calcul_exercice2()
            plot_url = generer_graphique_absorption(resultats['Y_vals'], resultats['X_vals'], resultats['m'], resultats['pente'], "Exercice 2 - Absorption du SO₂")
            plot_evolution_url = generer_graphique_evolution_absorption(resultats['Y_vals'], resultats['X_vals'], "Exercice 2 - Évolution des concentrations")
            plot_schema_url = generer_schema_colonne_absorption(resultats, "Exercice 2 - Schéma de la colonne")
        else:  # exercice == '3'
            resultats = calcul_exercice3()
            plot_url = generer_graphique_absorption(resultats['Y_vals'], resultats['X_vals'], resultats['m'], resultats['pente'], "Exercice 3 - Désorption du NH₃")
            plot_evolution_url = generer_graphique_evolution_absorption(resultats['Y_vals'], resultats['X_vals'], "Exercice 3 - Évolution des concentrations")
            plot_schema_url = generer_schema_colonne_desorption(resultats, "Exercice 3 - Schéma de la colonne")
        
        return jsonify({
            'success': True,
            'resultats': resultats,
            'plot_url': plot_url,
            'plot_evolution_url': plot_evolution_url,
            'plot_schema_url': plot_schema_url
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }), 500
