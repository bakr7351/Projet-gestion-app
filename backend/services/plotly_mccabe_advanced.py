"""
Service avancé de génération de graphiques McCabe-Thiele avec Plotly
Basé sur le code fourni par l'utilisateur avec logique d'étages multiples
"""

import numpy as np
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json


class AdvancedPlotlyMcCabeService:
    """Service avancé pour générer des graphiques McCabe-Thiele avec Plotly"""
    
    def __init__(self):
        self.dark_theme = {
            'template': 'plotly_dark',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': '#020617',
            'font': {'color': '#e2e8f0'},
            'margin': {'l': 40, 'r': 40, 't': 60, 'b': 40},
            'legend': {
                'bgcolor': 'rgba(0,0,0,0)',
                'bordercolor': '#1e293b'
            }
        }
    
    def generate_absorption_cross_current(self, G, L, m, y0, x0, stages):
        """
        Génère un graphique McCabe-Thiele pour l'absorption à contre-courant
        Logique exacte du code fourni
        
        Args:
            G: Débit molaire du gaz (mol/h)
            L: Débit molaire du solvant (mol/h)
            m: Constante d'équilibre
            y0: Fraction molaire d'entrée du gaz
            x0: Fraction molaire d'entrée du liquide
            stages: Nombre d'étages
        """
        
        # Conversion en rapports molaires
        Y0 = y0 / (1 - y0)
        A = L / (m * G)
        
        Ystart = Y0
        
        # Courbe d'équilibre
        Xeq = np.linspace(0, 0.2, 100)
        Yeq = m * Xeq
        
        fig = go.Figure()
        
        # Courbe d'équilibre
        fig.add_trace(go.Scatter(
            x=Xeq, 
            y=Yeq,
            mode='lines',
            name='Courbe d\'équilibre (Y = mX)',
            line=dict(color='lime', width=3)
        ))
        
        # Calcul des étages
        results = []
        for i in range(stages):
            # Intersection avec la courbe d'équilibre
            Xint = Ystart / (m + L / G)
            Yint = m * Xint
            
            # Droite opératoire pour cet étage
            Xop = np.linspace(0, Xint, 100)
            Yop = -(L / G) * Xop + Ystart
            
            fig.add_trace(go.Scatter(
                x=Xop, 
                y=Yop,
                mode='lines',
                name=f'Droite opératoire étage {i+1}',
                line=dict(color='magenta', width=2)
            ))
            
            # Point d'intersection
            fig.add_trace(go.Scatter(
                x=[Xint], 
                y=[Yint],
                mode='markers',
                name=f'Point étage {i+1}',
                marker=dict(color='cyan', size=10)
            ))
            
            # Stocker les résultats
            results.append({
                'stage': i + 1,
                'X_int': Xint,
                'Y_int': Yint,
                'Y_start': Ystart
            })
            
            Ystart = Yint
        
        # Calcul du taux d'absorption
        taux = (Y0 - Yint) / Y0 * 100 if Y0 > 0 else 0
        
        # Configuration du layout
        fig.update_layout(
            title="Diagramme McCabe-Thiele - Absorption à contre-courant",
            xaxis_title="X (rapport molaire phase liquide)",
            yaxis_title="Y (rapport molaire phase gaz)",
            **self.dark_theme
        )
        
        return {
            'graph_json': json.dumps(fig, cls=PlotlyJSONEncoder),
            'results': results,
            'Y0': Y0,
            'A': A,
            'taux': taux,
            'final_Y': Yint
        }
    
    def generate_absorption_unknown_stages(self, G, L, m, y0, x0, y_objectif):
        """
        Génère un graphique McCabe-Thiele pour l'absorption avec nombre d'étages inconnu
        Calcule automatiquement le nombre d'étages nécessaires
        
        Args:
            G: Débit molaire du gaz (mol/h)
            L: Débit molaire du solvant (mol/h)
            m: Constante d'équilibre
            y0: Fraction molaire d'entrée du gaz
            x0: Fraction molaire d'entrée du liquide
            y_objectif: Fraction molaire objectif en sortie
        """
        
        # Conversion en rapports molaires
        Y0 = y0 / (1 - y0)
        X0 = x0 / (1 - x0) if x0 > 0 else 0
        Y_objectif = y_objectif / (1 - y_objectif)
        
        A = L / (m * G)
        Ystart = Y0
        
        # Courbe d'équilibre
        Xeq = np.linspace(0, 0.2, 100)
        Yeq = m * Xeq
        
        fig = go.Figure()
        
        # Courbe d'équilibre
        fig.add_trace(go.Scatter(
            x=Xeq, 
            y=Yeq, 
            mode='lines', 
            name='Courbe d\'équilibre (Y = mX)',
            line=dict(color='lime', width=3)
        ))
        
        # Calcul itératif jusqu'à atteindre l'objectif
        i = 0
        results = []
        
        while Ystart > Y_objectif and i < 50:  # Limite de sécurité
            # Intersection avec la courbe d'équilibre
            Xint = Ystart / (m + L / G)
            Yint = m * Xint
            
            # Droite opératoire
            Xop = np.linspace(0, Xint, 100)
            Yop = (L / G) * Xop + Ystart
            
            fig.add_trace(go.Scatter(
                x=Xop, 
                y=Yop, 
                mode='lines', 
                name=f'Droite opératoire étage {i+1}',
                line=dict(color='magenta', width=2)
            ))
            
            # Point d'intersection
            fig.add_trace(go.Scatter(
                x=[Xint], 
                y=[Yint], 
                mode='markers', 
                name=f'Point étage {i+1}',
                marker=dict(color='cyan', size=10)
            ))
            
            # Stocker les résultats
            results.append({
                'stage': i + 1,
                'X_int': Xint,
                'Y_int': Yint,
                'Y_start': Ystart
            })
            
            Ystart = Yint
            i += 1
        
        # Calcul du taux d'absorption
        taux = (Y0 - Yint) / Y0 * 100 if Y0 > 0 else 0
        
        # Configuration du layout
        fig.update_layout(
            title=f"Absorption - {i} étages nécessaires (Taux: {taux:.1f}%)",
            xaxis_title="X (rapport molaire phase liquide)",
            yaxis_title="Y (rapport molaire phase gaz)",
            **self.dark_theme
        )
        
        return {
            'graph_json': json.dumps(fig, cls=PlotlyJSONEncoder),
            'results': results,
            'Y0': Y0,
            'A': A,
            'taux': taux,
            'stages': i,
            'final_Y': Yint
        }
    
    def generate_desorption_cross_current(self, G, L, m, y0, x0, stages):
        """
        Génère un graphique McCabe-Thiele pour la désorption à contre-courant
        
        Args:
            G: Débit molaire du gaz (mol/h)
            L: Débit molaire du liquide (mol/h)
            m: Constante d'équilibre
            y0: Fraction molaire d'entrée du gaz
            x0: Fraction molaire d'entrée du liquide
            stages: Nombre d'étages
        """
        
        # Conversion en rapports molaires
        Y0 = y0 / (1 - y0) if y0 > 0 else 0
        X0 = x0 / (1 - x0)
        
        A = L / (m * G)
        S = m * G / L
        
        # Calcul des valeurs x pour chaque étage
        x_values = []
        x_temp = x0
        for i in range(stages):
            xi = x_temp / (1 + S)
            x_values.append(xi)
            x_temp = xi
        
        Ystart = Y0
        
        # Courbe d'équilibre
        Xeq = np.linspace(0, 0.2, 100)
        Yeq = m * Xeq
        
        fig = go.Figure()
        
        # Courbe d'équilibre
        fig.add_trace(go.Scatter(
            x=Xeq, 
            y=Yeq,
            mode='lines',
            name='Courbe d\'équilibre (Y = mX)',
            line=dict(color='lime', width=3)
        ))
        
        # Calcul des étages de désorption
        results = []
        for i in range(stages):
            # Intersection avec la courbe d'équilibre
            Xint = Ystart / (m + L / G)
            Yint = m * Xint
            
            # Droite opératoire pour désorption (logique corrigée)
            Yop = np.linspace(0, Yint, 100)
            Xop = (Ystart - Yop) * (G / L)
            
            fig.add_trace(go.Scatter(
                x=Xop, 
                y=Yop,
                mode='lines',
                name=f'Droite opératoire étage {i+1}',
                line=dict(color='magenta', width=2)
            ))
            
            # Point d'intersection
            fig.add_trace(go.Scatter(
                x=[Xint], 
                y=[Yint],
                mode='markers',
                name=f'Point étage {i+1}',
                marker=dict(color='cyan', size=10)
            ))
            
            # Stocker les résultats
            results.append({
                'stage': i + 1,
                'X_int': Xint,
                'Y_int': Yint,
                'Y_start': Ystart,
                'x_value': x_values[i] if i < len(x_values) else None
            })
            
            Ystart = Yint
        
        # Calcul du taux de désorption
        taux = (Y0 - Yint) / Y0 * 100 if Y0 > 0 else 0
        
        # Configuration du layout
        fig.update_layout(
            title="Diagramme McCabe-Thiele - Désorption à contre-courant",
            xaxis_title="X (rapport molaire phase liquide)",
            yaxis_title="Y (rapport molaire phase gaz)",
            **self.dark_theme
        )
        
        return {
            'graph_json': json.dumps(fig, cls=PlotlyJSONEncoder),
            'results': results,
            'Y0': Y0,
            'A': A,
            'taux': taux,
            'S': S,
            'x_values': x_values,
            'final_Y': Yint
        }


# Instance globale du service
advanced_plotly_mccabe_service = AdvancedPlotlyMcCabeService()