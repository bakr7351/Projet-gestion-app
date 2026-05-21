"""
Service de calcul pour les procédés d'absorption et de désorption
"""
from datetime import datetime
import io
import time
import psutil
import os

# Import conditionnel pour éviter les erreurs de dépendance
try:
    from backend.services.mccabe_thiele_service import mccabe_service
    MCCABE_AVAILABLE = True
except ImportError as e:
    MCCABE_AVAILABLE = False
    mccabe_service = None

try:
    from backend.services.plotly_mccabe_advanced import advanced_plotly_mccabe_service
    ADVANCED_PLOTLY_AVAILABLE = True
except ImportError:
    ADVANCED_PLOTLY_AVAILABLE = False
    advanced_plotly_mccabe_service = None

try:
    from backend.services.concentration_3d_service import concentration_3d_service
    CONCENTRATION_3D_AVAILABLE = True
except ImportError:
    CONCENTRATION_3D_AVAILABLE = False
    concentration_3d_service = None


def fraction_to_rapport(z):
    """Convertit une fraction molaire en rapport molaire"""
    return z / (1 - z) if 0 < z < 1 else 0


def rapport_to_fraction(Z):
    """Convertit un rapport molaire en fraction molaire"""
    return Z / (1 + Z) if Z >= 0 else 0


def simuler_absorption_courant_croise(G_prime, L_prime, m, y0, y_obj=None, N_etages=None):
    """
    Simulation absorption a courant croise (cross-current)
    Chaque etage recoit du solvant frais
    
    Args:
        G_prime: Debit gaz inerte (mol/h)
        L_prime: Debit solvant par etage (mol/h)
        m: Constante equilibre
        y0: Fraction molaire entree gaz
        y_obj: Fraction molaire objectif (optionnel)
        N_etages: Nombre etages max (optionnel, par défaut 50)
    
    Returns:
        dict avec resultats
    """
    Y0 = fraction_to_rapport(y0)
    Y_obj = fraction_to_rapport(y_obj) if y_obj else None
    A = L_prime / (m * G_prime)
    pente = -L_prime / G_prime
    
    Y_vals = [Y0]
    X_vals = [0.0]
    resultats = []
    
    convergence = False
    etages = 0
    max_etages = N_etages if N_etages else 50
    
    for i in range(1, max_etages + 1):
        Y_prev = Y_vals[-1]
        Yi = Y_prev / (1 + A)
        Xi = Yi / m
        yi = rapport_to_fraction(Yi)
        
        Y_vals.append(Yi)
        X_vals.append(Xi)
        
        resultats.append({
            'etage': i,
            'Y_entree': round(Y_prev, 6),
            'X_sortie': round(Xi, 6),
            'Y_sortie': round(Yi, 6),
            'y_sortie': round(yi, 6)
        })
        
        etages = i
        
        # Vérifier si objectif atteint
        if y_obj and yi <= y_obj:
            convergence = True
            break
    
    taux = (Y0 - Y_vals[-1]) / Y0 if Y0 > 0 else 0
    quantite = G_prime * (Y0 - Y_vals[-1])
    
    # Prepare data for concentration graphs
    stages_list = list(range(etages + 1))
    X_prof = X_vals.copy()
    Y_prof = Y_vals.copy()
    
    # Prepare step data for McCabe-Thiele
    x_steps = []
    y_steps = []
    for i in range(len(Y_vals)):
        if i < len(X_vals):
            x_steps.append(X_vals[i])
            y_steps.append(Y_vals[i])
    
    return {
        'resultats': resultats,
        'Y_vals': Y_vals,
        'X_vals': X_vals,
        'stages_list': stages_list,
        'X_prof': X_prof,
        'Y_prof': Y_prof,
        'x_steps': x_steps,
        'y_steps': y_steps,
        'm': m,
        'Y0': round(Y0, 6),
        'X0': 0.0,
        'Y_out': round(Y_vals[-1], 6),
        'X_out': round(X_vals[-1], 6),
        'Y_in': round(Y0, 6),
        'X_in': 0.0,
        'G_prime': G_prime,
        'L_prime': L_prime,
        'y0': y0,
        'y_objectif': round(rapport_to_fraction(Y_vals[-1]), 6),
        'facteur_A': round(A, 4),
        'taux': round(taux * 100, 2),
        'quantite': round(quantite, 2),
        'nb_etages': etages,
        'convergence': convergence,
        'objectif_atteint': convergence if y_obj else True,
        'contact_type': 'cross-current'
    }


def simuler_desorption_courant_croise(L_prime, G_prime, m, x0, x_obj=None, N_etages=None):
    """
    Simulation desorption a courant croise (cross-current)
    Chaque etage recoit du gaz frais
    
    Args:
        L_prime: Debit liquide (mol/h)
        G_prime: Debit gaz par etage (mol/h)
        m: Constante equilibre
        x0: Fraction molaire entree liquide
        x_obj: Fraction molaire objectif (optionnel)
        N_etages: Nombre etages max (optionnel, par défaut 50)
    
    Returns:
        dict avec resultats
    """
    X0 = fraction_to_rapport(x0)
    X_obj = fraction_to_rapport(x_obj) if x_obj else None
    pente = G_prime / L_prime
    
    X_vals = [X0]
    Y_vals = [0.0]
    resultats = []
    
    convergence = False
    etages = 0
    max_etages = N_etages if N_etages else 50
    X_courant = X0
    
    for i in range(1, max_etages + 1):
        # À courant croisé: chaque étage reçoit du gaz frais (Y=0)
        # Intersection analytique: m*X = pente*(X_courant - X)
        # X_sortant = (pente * X_courant) / (m + pente)
        X_sortant = (pente * X_courant) / (m + pente)
        Y_sortant = m * X_sortant
        
        # Vérifier la progression
        if X_sortant < 0 or X_sortant >= X_courant:
            break
        
        x_sortie = rapport_to_fraction(X_sortant)
        
        X_vals.append(X_sortant)
        Y_vals.append(Y_sortant)
        
        resultats.append({
            'etage': i,
            'X_entree': round(X_courant, 6),
            'Y_entree': 0.0,
            'X_sortie': round(X_sortant, 6),
            'Y_sortie': round(Y_sortant, 6),
            'x_sortie': round(x_sortie, 6)
        })
        
        etages = i
        X_courant = X_sortant
        
        # Vérifier si objectif atteint
        if x_obj and x_sortie <= x_obj:
            convergence = True
            break
    
    taux = (X0 - X_vals[-1]) / X0 if X0 > 0 else 0
    quantite = L_prime * (X0 - X_vals[-1])
    facteur_S = (m * G_prime) / L_prime
    
    # Prepare data for concentration graphs
    stages_list = list(range(etages + 1))
    X_prof = X_vals.copy()
    Y_prof = Y_vals.copy()
    
    # Prepare step data for McCabe-Thiele
    x_steps = []
    y_steps = []
    for i in range(len(X_vals)):
        if i < len(Y_vals):
            x_steps.append(X_vals[i])
            y_steps.append(Y_vals[i])
    
    return {
        'resultats': resultats,
        'X_vals': X_vals,
        'Y_vals': Y_vals,
        'stages_list': stages_list,
        'X_prof': X_prof,
        'Y_prof': Y_prof,
        'x_steps': x_steps,
        'y_steps': y_steps,
        'm': m,
        'X0': round(X0, 6),
        'Y0': 0.0,
        'X_out': round(X_vals[-1], 6),
        'Y_out': round(Y_vals[-1], 6),
        'X_in': round(X0, 6),
        'Y_in': 0.0,
        'G': G_prime,
        'L': L_prime,
        'x0': x0,
        'x_obj': round(rapport_to_fraction(X_vals[-1]), 6),
        'facteur_S': round(facteur_S, 4),
        'taux': round(taux * 100, 2),
        'quantite': round(quantite, 2),
        'nb_etages': etages,
        'convergence': convergence,
        'objectif_atteint': convergence if x_obj else True,
        'contact_type': 'cross-current'
    }


class AbsorptionCalculator:
    """
    Wrapper class for absorption and desorption calculations
    Provides a unified interface for the API
    """
    
    def __init__(self):
        self.start_time = None
        self.process = psutil.Process()
    
    def _start_performance_tracking(self):
        """Start performance tracking"""
        self.start_time = time.time()
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.initial_cpu = self.process.cpu_percent()
    
    def _get_performance_metrics(self):
        """Get performance metrics"""
        if not self.start_time:
            return {}
        
        execution_time = time.time() - self.start_time
        current_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_usage = current_memory - self.initial_memory
        cpu_usage = self.process.cpu_percent()
        
        return {
            'execution_time_ms': round(execution_time * 1000, 2),
            'memory_usage_mb': round(memory_usage, 2),
            'cpu_usage_percent': round(cpu_usage, 2),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def calculate_absorption(self, G_prime, L_prime, m, y0, y_obj, N=10, contact_type='counter-current'):
        """
        Calculate absorption process with McCabe-Thiele diagram
        
        Args:
            G_prime: Gas molar flow rate (mol/h)
            L_prime: Solvent molar flow rate (mol/h)
            m: Equilibrium constant
            y0: Inlet gas mole fraction
            y_obj: Target outlet mole fraction
            N: Number of stages (default: 10)
            contact_type: 'counter-current' or 'cross-current' (default: 'counter-current')
        """
        self._start_performance_tracking()
        
        try:
            # Choose calculation method based on contact type
            if contact_type == 'cross-current':
                # Use cross-current calculation with objective
                results = simuler_absorption_courant_croise(G_prime, L_prime, m, y0, y_obj, N)
            else:
                # Use counter-current calculation (default)
                data = {
                    'G_prime': G_prime,
                    'L_prime': L_prime,
                    'm': m,
                    'y0': y0,
                    'x0': 0,  # Default value
                    'y_objectif': y_obj
                }
                results = simuler_absorption(data)
            
            # Generate McCabe-Thiele diagram if available
            mccabe_graph = None
            matplotlib_graph = None
            advanced_plotly_graph = None
            surface_3d = None
            concentration_graph = None
            graph_3d = None
            
            # Choose the appropriate graph generation based on contact_type
            if contact_type == 'cross-current':
                # Use cross-current methods
                if ADVANCED_PLOTLY_AVAILABLE and advanced_plotly_mccabe_service:
                    try:
                        advanced_result = advanced_plotly_mccabe_service.generate_absorption_cross_current(
                            G_prime, L_prime, m, y0, 0, N
                        )
                        advanced_plotly_graph = advanced_result['graph_json']
                    except Exception as e:
                        print(f"Warning: Cross-current graph generation failed: {e}")
                
                # Generate concentration evolution and 3D graphs for cross-current
                if CONCENTRATION_3D_AVAILABLE and concentration_3d_service:
                    try:
                        # Calculate y_out from results
                        y_out = results.get('y_objectif', y_obj)
                        conc_3d_result = concentration_3d_service.generate_absorption_graphs(
                            G_prime, L_prime, m, y0, 0, y_out,
                            calc_results=results
                        )
                        if conc_3d_result.get('success'):
                            matplotlib_graph = conc_3d_result.get('mccabe_graph')
                            concentration_graph = conc_3d_result.get('concentration_graph')
                            graph_3d = conc_3d_result.get('3d_graph')
                    except Exception as e:
                        print(f"Warning: Concentration/3D graph generation failed: {e}")
            else:
                # Use counter-current methods (default)
                if MCCABE_AVAILABLE and mccabe_service:
                    try:
                        mccabe_graph = mccabe_service.generate_absorption_graph(
                            L_prime, G_prime, m, y0, 0, results['resultats']
                        )
                        surface_3d = mccabe_service.generate_3d_surface_plot('absorption', results)
                    except Exception as e:
                        print(f"Warning: McCabe-Thiele graph generation failed: {e}")
                
                if ADVANCED_PLOTLY_AVAILABLE and advanced_plotly_mccabe_service:
                    try:
                        advanced_result = advanced_plotly_mccabe_service.generate_absorption_unknown_stages(
                            G_prime, L_prime, m, y0, 0, y_obj
                        )
                        advanced_plotly_graph = advanced_result['graph_json']
                    except Exception as e:
                        print(f"Warning: Advanced Plotly McCabe-Thiele graph generation failed: {e}")
                
                # Generate concentration evolution and 3D graphs (includes matplotlib McCabe-Thiele)
                if CONCENTRATION_3D_AVAILABLE and concentration_3d_service:
                    try:
                        conc_3d_result = concentration_3d_service.generate_absorption_graphs(
                            G_prime, L_prime, m, y0, 0, y_obj,
                            calc_results=results  # pass pre-calculated stages
                        )
                        if conc_3d_result.get('success'):
                            matplotlib_graph = conc_3d_result.get('mccabe_graph')
                            concentration_graph = conc_3d_result.get('concentration_graph')
                            graph_3d = conc_3d_result.get('3d_graph')
                    except Exception as e:
                        print(f"Warning: Concentration/3D graph generation failed: {e}")
            
            # Add performance metrics
            performance = self._get_performance_metrics()
            
            response = {
                'calculation_results': results,
                'performance': performance
            }
            
            if mccabe_graph:
                response['mccabe_thiele_graph'] = mccabe_graph
            if matplotlib_graph:
                response['matplotlib_mccabe_graph'] = matplotlib_graph
            if advanced_plotly_graph:
                response['advanced_plotly_mccabe_graph'] = advanced_plotly_graph
            if surface_3d:
                response['surface_3d_graph'] = surface_3d
            if concentration_graph:
                response['concentration_evolution_graph'] = concentration_graph
            if graph_3d:
                response['3d_profile_graph'] = graph_3d
            
            return response
            
        except Exception as e:
            raise Exception(f"Absorption calculation failed: {str(e)}")
    
    def calculate_desorption(self, G, L, m, x0, x_obj, N=10, contact_type='counter-current'):
        """
        Calculate desorption process with McCabe-Thiele diagram
        
        Args:
            G: Gas molar flow rate (mol/h)
            L: Liquid molar flow rate (mol/h)
            m: Equilibrium constant
            x0: Inlet liquid mole fraction
            x_obj: Target outlet mole fraction
            N: Number of stages (default: 10)
            contact_type: 'counter-current' or 'cross-current' (default: 'counter-current')
        """
        self._start_performance_tracking()
        
        try:
            # Choose calculation method based on contact type
            if contact_type == 'cross-current':
                # Use cross-current calculation with objective
                results = simuler_desorption_courant_croise(L, G, m, x0, x_obj, N)
            else:
                # Use counter-current calculation (default)
                params = (G, L, m, x0, 0, x_obj)  # y0 = 0 as default
                results = simuler_desorption(params)
            
            # Generate McCabe-Thiele diagram if available
            mccabe_graph = None
            matplotlib_graph = None
            advanced_plotly_graph = None
            surface_3d = None
            concentration_graph = None
            graph_3d = None
            
            # Choose the appropriate graph generation based on contact_type
            if contact_type == 'cross-current':
                # Use cross-current methods
                if ADVANCED_PLOTLY_AVAILABLE and advanced_plotly_mccabe_service:
                    try:
                        advanced_result = advanced_plotly_mccabe_service.generate_desorption_cross_current(
                            G, L, m, 0, x0, N
                        )
                        advanced_plotly_graph = advanced_result['graph_json']
                    except Exception as e:
                        print(f"Warning: Cross-current desorption graph generation failed: {e}")
                
                # Generate concentration evolution and 3D graphs for cross-current
                if CONCENTRATION_3D_AVAILABLE and concentration_3d_service:
                    try:
                        # Calculate x_out from results
                        x_out = results.get('x_obj', x_obj)
                        conc_3d_result = concentration_3d_service.generate_desorption_graphs(
                            G, L, m, 0, x0, x_out,
                            calc_results=results
                        )
                        if conc_3d_result.get('success'):
                            matplotlib_graph = conc_3d_result.get('mccabe_graph')
                            concentration_graph = conc_3d_result.get('concentration_graph')
                            graph_3d = conc_3d_result.get('3d_graph')
                    except Exception as e:
                        print(f"Warning: Concentration/3D graph generation failed: {e}")
            else:
                # Use counter-current methods (default)
                if MCCABE_AVAILABLE and mccabe_service:
                    try:
                        mccabe_graph = mccabe_service.generate_desorption_graph(
                            L, G, m, x0, 0, results['resultats']
                        )
                        surface_3d = mccabe_service.generate_3d_surface_plot('desorption', results)
                    except Exception as e:
                        print(f"Warning: McCabe-Thiele graph generation failed: {e}")
                
                # Generate concentration evolution and 3D graphs (includes matplotlib McCabe-Thiele)
                if CONCENTRATION_3D_AVAILABLE and concentration_3d_service:
                    try:
                        conc_3d_result = concentration_3d_service.generate_desorption_graphs(
                            G, L, m, 0, x0, x_obj,
                            calc_results=results  # pass pre-calculated stages
                        )
                        if conc_3d_result.get('success'):
                            matplotlib_graph = conc_3d_result.get('mccabe_graph')
                            concentration_graph = conc_3d_result.get('concentration_graph')
                            graph_3d = conc_3d_result.get('3d_graph')
                    except Exception as e:
                        print(f"Warning: Concentration/3D graph generation failed: {e}")
            
            # Add performance metrics
            performance = self._get_performance_metrics()
            
            response = {
                'calculation_results': results,
                'performance': performance
            }
            
            if mccabe_graph:
                response['mccabe_thiele_graph'] = mccabe_graph
            if matplotlib_graph:
                response['matplotlib_mccabe_graph'] = matplotlib_graph
            if advanced_plotly_graph:
                response['advanced_plotly_mccabe_graph'] = advanced_plotly_graph
            if surface_3d:
                response['surface_3d_graph'] = surface_3d
            if concentration_graph:
                response['concentration_evolution_graph'] = concentration_graph
            if graph_3d:
                response['3d_profile_graph'] = graph_3d
            
            return response
            
        except Exception as e:
            raise Exception(f"Desorption calculation failed: {str(e)}")


# ==================== ABSORPTION ====================

def simuler_absorption(data):
    """
    Simulation du procede absorption - meme logique que le code de reference McCabe-Thiele.
    
    Algorithme :
    - Rapports molaires : Y = y/(1-y), X = x/(1-x)
    - Bilan : X_out = X_in + (G/L)*(Y_in - Y_out)
    - Escalier : part de (X_in, Y_out) et monte vers (X_out, Y_in)
      * Horizontal droite -> courbe equilibre : X_eq = Y_c / m
      * Vertical haut -> droite operatoire : Y_op = Y_out + (L/G)*(X_eq - X_in)
    """
    start_time = time.time()

    G_prime = float(data['G_prime'])
    L_prime = float(data['L_prime'])
    m       = float(data['m'])
    y0      = float(data['y0'])
    x0      = float(data['x0'])
    y_objectif = float(data['y_objectif'])

    # Conversion fractions -> rapports molaires
    Y_in  = y0 / (1 - y0) if y0 < 1 else 0
    X_in  = x0 / (1 - x0) if 0 < x0 < 1 else 0
    Y_out = y_objectif / (1 - y_objectif) if y_objectif < 1 else 0
    X_out = X_in + (G_prime / L_prime) * (Y_in - Y_out)

    facteur_A = L_prime / (m * G_prime)

    # ── Construction de escalier McCabe-Thiele ──────────────────────────
    x_steps   = [X_in]
    y_steps   = [Y_out]
    stages_list = [0]
    X_prof    = [X_in]
    Y_prof    = [Y_out]

    Y_c       = Y_out
    stage_count = 0
    resultats = []

    while Y_c < Y_in and stage_count < 50:
        stage_count += 1

        # Horizontal droite -> courbe equilibre
        X_eq = Y_c / m
        x_steps.extend([X_eq, X_eq])
        y_steps.append(Y_c)

        # Vertical haut -> droite opératoire
        Y_op = Y_out + (L_prime / G_prime) * (X_eq - X_in)

        if Y_op >= Y_in:
            y_steps.append(Y_in)
            stages_list.append(stage_count)
            X_prof.append(X_eq)
            Y_prof.append(Y_in)
            resultats.append({
                'etage':    stage_count,
                'Y_entree': round(Y_c, 6),
                'X_sortie': round(X_eq, 6),
                'Y_sortie': round(Y_in, 6),
                'y_sortie': round(y_objectif, 6),
            })
            break

        y_steps.append(Y_op)
        Y_c = Y_op

        stages_list.append(stage_count)
        X_prof.append(X_eq)
        Y_prof.append(Y_c)
        resultats.append({
            'etage':    stage_count,
            'Y_entree': round(Y_c if stage_count == 1 else Y_prof[-2], 6),
            'X_sortie': round(X_eq, 6),
            'Y_sortie': round(Y_op, 6),
            'y_sortie': round(rapport_to_fraction(Y_op), 6),
        })

    # Résultats finaux - taux basé sur Y_in (entrée) et Y_out (objectif atteint)
    y_final  = resultats[-1]['y_sortie'] if resultats else y_objectif
    taux     = (Y_in - Y_out) / Y_in * 100 if Y_in > 0 else 0
    quantite = G_prime * (Y_in - Y_out)

    end_time    = time.time()
    execution_time = end_time - start_time
    _proc = psutil.Process(os.getpid())

    return {
        'resultats':    resultats,
        'stages_list':  stages_list,
        'X_prof':       X_prof,
        'Y_prof':       Y_prof,
        'x_steps':      x_steps,
        'y_steps':      y_steps,
        'm':            m,
        'Y0':           round(Y_in, 6),
        'X0':           round(X_in, 6),
        'Y_out':        round(Y_out, 6),
        'X_out':        round(X_out, 6),
        'G_prime':      G_prime,
        'L_prime':      L_prime,
        'y0':           y0,
        'y_objectif':   y_objectif,
        'facteur_A':    round(facteur_A, 4),
        'taux':         round(taux, 2),
        'quantite':     round(quantite, 2),
        'nb_etages':    stage_count,
        'performance': {
            'execution_time_ms':    round(execution_time * 1000, 2),
            'cpu_usage_percent':    round(psutil.cpu_percent(interval=0.1), 1),
            'memory_usage_mb':      round(_proc.memory_info().rss / 1024 / 1024, 1),
            'memory_usage_percent': round(_proc.memory_percent(), 1),
            'iterations':           stage_count,
            'convergence': 'Objectif atteint' if y_final <= y_objectif else 'Limite etages atteinte',
        },
    }


# ==================== DESORPTION ====================

def simuler_desorption(params):
    """
    Simulation du procede de desorption a contre-courant.
    
    Logique McCabe-Thiele correcte (selon code de reference) :
    - On travaille en rapports molaires (X, Y)
    - Bilan matiere : Y_out = Y_in + (L/G) * (X_in - X_out)
    - Escalier part de (X_in, Y_out) en haut et descend vers (X_out, Y_in)
    - Etape horizontale gauche : X_eq = Y_c / m  (vers courbe equilibre)
    - Etape verticale bas : Y_op = Y_in + (L/G) * (X_eq - X_out)  (vers droite operatoire)
    """
    start_time = time.time()

    G, L, m, x0, y0, x_obj = params

    # Conversion fractions -> rapports molaires
    X_in  = fraction_to_rapport(x0)
    Y_in  = fraction_to_rapport(y0)   # généralement 0
    X_out = fraction_to_rapport(x_obj)

    # Bilan matière global : Y_out (gaz sortant enrichi)
    Y_out = Y_in + (L / G) * (X_in - X_out)

    facteur_S = m * G / L

    # ── Construction de escalier McCabe-Thiele ──────────────────────────
    x_steps   = [X_in]
    y_steps   = [Y_out]
    stages_list = [0]
    X_prof    = [X_in]
    Y_prof    = [Y_out]

    Y_c         = Y_out
    stage_count = 0
    resultats   = []

    while Y_c > Y_in and stage_count < 50:
        stage_count += 1

        # Étape horizontale gauche -> courbe equilibre
        X_eq = Y_c / m

        # Étape verticale bas -> droite opératoire
        Y_op = Y_in + (L / G) * (X_eq - X_out)

        # Horizontal : (x_prev, Y_c) -> (X_eq, Y_c)
        x_steps.append(X_eq)
        y_steps.append(Y_c)

        # Vertical : (X_eq, Y_c) -> (X_eq, Y_op)
        x_steps.append(X_eq)
        y_steps.append(Y_op)

        resultats.append({
            'etage':    stage_count,
            'X_entree': round(X_in if stage_count == 1 else X_prof[-1], 6),
            'Y_entree': round(Y_c, 6),
            'X_sortie': round(X_eq, 6),
            'Y_sortie': round(Y_op, 6),
            'x_sortie': round(rapport_to_fraction(X_eq), 6),
        })

        stages_list.append(stage_count)
        X_prof.append(X_eq)
        Y_prof.append(Y_op)

        # Condition d'arrêt : on a atteint ou dépassé X_out
        if X_eq <= X_out:
            break

        Y_c = Y_op

    # Résultats finaux
    X_final   = resultats[-1]['X_sortie'] if resultats else X_out
    x_final   = resultats[-1]['x_sortie'] if resultats else rapport_to_fraction(X_out)
    taux      = (X_in - X_final) / X_in * 100 if X_in > 0 else 0
    quantite  = L * (X_in - X_final)

    end_time    = time.time()
    execution_time = end_time - start_time
    _proc = psutil.Process(os.getpid())

    return {
        'resultats':    resultats,
        'stages_list':  stages_list,
        'X_prof':       X_prof,
        'Y_prof':       Y_prof,
        'x_steps':      x_steps,
        'y_steps':      y_steps,
        'm':            m,
        'X_in':         round(X_in, 6),
        'Y_in':         round(Y_in, 6),
        'X_out':        round(X_out, 6),
        'Y_out':        round(Y_out, 6),
        # legacy keys
        'X0':           round(X_in, 6),
        'Y0':           round(Y_in, 6),
        'X_final':      round(X_final, 6),
        'G':            G,
        'L':            L,
        'x0':           x0,
        'x_obj':        x_obj,
        'facteur_S':    round(facteur_S, 4),
        'taux':         round(taux, 2),
        'quantite':     round(quantite, 2),
        'x_final':      x_final,
        'nb_etages':    stage_count,
        'performance': {
            'execution_time_ms':    round(execution_time * 1000, 2),
            'cpu_usage_percent':    round(psutil.cpu_percent(interval=0.1), 1),
            'memory_usage_mb':      round(_proc.memory_info().rss / 1024 / 1024, 1),
            'memory_usage_percent': round(_proc.memory_percent(), 1),
            'iterations':           stage_count,
            'convergence': 'Objectif atteint' if X_final <= X_out else 'Limite etages atteinte',
        },
    }


# ==================== EXPORT FUNCTIONS ====================

def generer_rapport_absorption(results):
    """Generate un rapport analyse pour absorption"""
    rapport = io.StringIO()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    rapport.write("="*80 + "\n")
    rapport.write("RAPPORT D'ANALYSE - ABSORPTION A CONTRE-COURANT\n".center(80) + "\n")
    rapport.write("="*80 + "\n\n")
    rapport.write(f"Date: {now}\n\n")
    
    rapport.write("1. PARAMETRES ENTREE\n")
    rapport.write("-"*40 + "\n")
    rapport.write(f"   Débit gaz G′      : {results['G_prime']:>10.2f} mol/h\n")
    rapport.write(f"   Débit solvant L′   : {results['L_prime']:>10.2f} mol/h\n")
    rapport.write(f"   Constante m        : {results['m']:>10.4f}\n")
    rapport.write(f"   Facteur A          : {results['facteur_A']:>10.4f}\n")
    rapport.write(f"   y₀ entrée          : {results['y0']:>10.6f}\n")
    rapport.write(f"   y objectif         : {results['y_objectif']:>10.6f}\n\n")
    
    rapport.write("2. RÉSULTATS DE LA SIMULATION\n")
    rapport.write("-"*60 + "\n")
    rapport.write(f"{'Étage':<8} {'X sortie':<16} {'Y sortie':<16} {'y sortie':<16}\n")
    rapport.write("-"*60 + "\n")
    
    for res in results['resultats']:
        rapport.write(f"{res['etage']:<8} {res['X_sortie']:<16.6f} "
                     f"{res['Y_sortie']:<16.6f} {res['y_sortie']:<16.6f}\n")
    
    rapport.write("\n3. PERFORMANCES\n")
    rapport.write("-"*40 + "\n")
    rapport.write(f"   Étages nécessaires : {results['nb_etages']:>3d}\n")
    rapport.write(f"   Taux absorption  : {results['taux']:>7.2f}%\n")
    rapport.write(f"   Quantité absorbée  : {results['quantite']:>8.2f} mol/h\n")
    rapport.write("\n" + "="*80 + "\n")
    
    return rapport.getvalue(), now


def generer_rapport_desorption(results):
    """Generate un rapport analyse pour desorption"""
    rapport = io.StringIO()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    rapport.write("="*80 + "\n")
    rapport.write("RAPPORT D'ANALYSE - DESORPTION A CONTRE-COURANT\n".center(80) + "\n")
    rapport.write("="*80 + "\n\n")
    rapport.write(f"Date: {now}\n\n")
    
    rapport.write("1. PARAMETRES ENTREE\n")
    rapport.write("-"*40 + "\n")
    rapport.write(f"   Débit gaz G       : {results['G']:>10.2f} mol/h\n")
    rapport.write(f"   Débit liquide L   : {results['L']:>10.2f} mol/h\n")
    rapport.write(f"   Constante m       : {results['m']:>10.4f}\n")
    rapport.write(f"   Facteur S         : {results['facteur_S']:>10.4f}\n")
    rapport.write(f"   x₀ entrée         : {results['x0']:>10.6f}\n")
    rapport.write(f"   x objectif        : {results['x_obj']:>10.6f}\n\n")
    
    rapport.write("2. RÉSULTATS DE LA SIMULATION\n")
    rapport.write("-"*80 + "\n")
    rapport.write(f"{'Étage':<8} {'X entrée':<16} {'Y entrée':<16} {'X sortie':<16} {'Y sortie':<16} {'x sortie':<16}\n")
    rapport.write("-"*80 + "\n")
    
    for res in results['resultats']:
        rapport.write(f"{res['etage']:<8} {res['X_entree']:<16.6f} {res['Y_entree']:<16.6f} "
                     f"{res['X_sortie']:<16.6f} {res['Y_sortie']:<16.6f} {res['x_sortie']:<16.6f}\n")
    
    rapport.write("\n3. PERFORMANCES\n")
    rapport.write("-"*40 + "\n")
    rapport.write(f"   Étages nécessaires : {results['nb_etages']:>3d}\n")
    rapport.write(f"   Taux de désorption : {results['taux']:>7.2f}%\n")
    rapport.write(f"   Quantité désorbée  : {results['quantite']:>8.2f} mol/h\n")
    rapport.write("\n" + "="*80 + "\n")
    
    return rapport.getvalue(), now
