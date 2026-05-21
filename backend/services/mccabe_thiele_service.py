"""
Service de génération de graphiques McCabe-Thiele
Génère des graphiques interactifs avec Plotly pour l'absorption et la désorption
"""

import numpy as np
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json


class McCabeThieleService:
    """Service pour générer des graphiques McCabe-Thiele interactifs"""
    
    def __init__(self):
        self.colors = {
            'equilibrium': '#00ff00',  # Vert lime
            'operating': '#ff00ff',    # Magenta
            'steps': '#00ffff',        # Cyan
            'background': '#1e1e1e',   # Noir foncé
            'grid': '#404040',         # Gris foncé
            'text': '#ffffff'          # Blanc
        }
    
    def generate_absorption_graph(self, L_prime, G_prime, m, y_in, x_in, stages_data):
        """
        Génère un graphique McCabe-Thiele pour l'absorption
        
        Args:
            L_prime: Débit molaire du solvant (mol/h)
            G_prime: Débit molaire du gaz (mol/h) 
            m: Constante d'équilibre
            y_in: Fraction molaire d'entrée du gaz
            x_in: Fraction molaire d'entrée du liquide
            stages_data: Données des étages calculés
        """
        
        # Conversion en rapports molaires
        Y_in = y_in / (1 - y_in) if y_in < 1 else 0
        X_in = x_in / (1 - x_in) if x_in < 1 else 0
        
        # Plage pour les courbes
        X_max = max(0.2, Y_in / m * 1.2)
        X_eq = np.linspace(0, X_max, 300)
        Y_eq = m * X_eq
        
        # Création de la figure
        fig = go.Figure()
        
        # Courbe d'équilibre
        fig.add_trace(go.Scatter(
            x=X_eq,
            y=Y_eq,
            mode='lines',
            name='Courbe d\'équilibre (Y = mX)',
            line=dict(color=self.colors['equilibrium'], width=3),
            hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
        ))
        
        # Droite opératoire
        X_line = np.linspace(0, X_max, 300)
        Y_line = (L_prime/G_prime) * (X_line - X_in) + Y_in
        
        fig.add_trace(go.Scatter(
            x=X_line,
            y=Y_line,
            mode='lines',
            name=f'Droite opératoire (pente = {L_prime/G_prime:.3f})',
            line=dict(color=self.colors['operating'], width=3),
            hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
        ))
        
        # Étapes McCabe-Thiele
        if stages_data:
            self._add_mccabe_steps_absorption(fig, stages_data, m, L_prime, G_prime, X_in, Y_in)
        
        # Points importants
        fig.add_trace(go.Scatter(
            x=[X_in],
            y=[Y_in],
            mode='markers',
            name=f'Point d\'entrée (X₀={X_in:.4f}, Y₀={Y_in:.4f})',
            marker=dict(color='red', size=10, symbol='circle'),
            hovertemplate='Point d\'entrée<br>X₀: %{x:.4f}<br>Y₀: %{y:.4f}<extra></extra>'
        ))
        
        if stages_data:
            final_stage = stages_data[-1]
            X_final = final_stage['X_sortie']
            Y_final = final_stage['Y_sortie']
            
            fig.add_trace(go.Scatter(
                x=[X_final],
                y=[Y_final],
                mode='markers',
                name=f'Point final (X={X_final:.4f}, Y={Y_final:.4f})',
                marker=dict(color='orange', size=10, symbol='star'),
                hovertemplate='Point final<br>X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
            ))
        
        # Configuration du layout
        fig.update_layout(
            template='plotly_dark',
            title={
                'text': 'Diagramme McCabe-Thiele - Absorption a contre-courant',
                'x': 0.5,
                'font': {'size': 18, 'color': self.colors['text']}
            },
            xaxis_title='X (rapport molaire phase liquide)',
            yaxis_title='Y (rapport molaire phase gaz)',
            xaxis=dict(
                gridcolor=self.colors['grid'],
                showgrid=True,
                zeroline=True,
                zerolinecolor=self.colors['grid']
            ),
            yaxis=dict(
                gridcolor=self.colors['grid'],
                showgrid=True,
                zeroline=True,
                zerolinecolor=self.colors['grid']
            ),
            plot_bgcolor=self.colors['background'],
            paper_bgcolor=self.colors['background'],
            font=dict(color=self.colors['text']),
            height=650,
            hovermode='closest',
            legend=dict(
                bgcolor='rgba(0,0,0,0.5)',
                bordercolor=self.colors['grid'],
                borderwidth=1
            )
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def generate_desorption_graph(self, L, G, m, x_in, y_in, stages_data):
        """
        Génère un graphique McCabe-Thiele pour la désorption.
        
        Logique correcte (d'après code de référence) :
        - Courbe d'équilibre : Y = m*X
        - Droite opératoire  : Y = Y_in + (L/G)*(X - X_out)
        - Escalier : part de (X_in, Y_out) en haut, descend vers (X_out, Y_in)
          * Horizontal gauche → courbe d'équilibre : X_eq = Y_c / m
          * Vertical bas → droite opératoire : Y_op = Y_in + (L/G)*(X_eq - X_out)
        """

        # Conversion fractions → rapports molaires
        X_in = x_in / (1 - x_in) if 0 < x_in < 1 else x_in
        Y_in = y_in / (1 - y_in) if 0 < y_in < 1 else 0.0

        # Récupérer X_out et Y_out depuis stages_data si disponible
        if stages_data:
            X_out = stages_data[-1]['X_sortie']
            Y_out = Y_in + (L / G) * (X_in - X_out)
        else:
            X_out = 0.0
            Y_out = Y_in

        X_max = max(0.2, X_in * 1.3)

        fig = go.Figure()

        # ── Courbe d'équilibre ──────────────────────────────────────────────
        X_eq_line = np.linspace(0, X_max, 300)
        Y_eq_line = m * X_eq_line
        fig.add_trace(go.Scatter(
            x=X_eq_line, y=Y_eq_line,
            mode='lines',
            name="Courbe d'équilibre (Y = mX)",
            line=dict(color=self.colors['equilibrium'], width=3),
            hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
        ))

        # ── Droite opératoire ───────────────────────────────────────────────
        # Y = Y_in + (L/G)*(X - X_out)
        X_op_line = np.linspace(0, X_max, 300)
        Y_op_line = Y_in + (L / G) * (X_op_line - X_out)
        fig.add_trace(go.Scatter(
            x=X_op_line, y=Y_op_line,
            mode='lines',
            name=f'Droite opératoire (pente = {L/G:.3f})',
            line=dict(color=self.colors['operating'], width=3),
            hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
        ))

        # ── Escalier McCabe-Thiele ──────────────────────────────────────────
        if stages_data:
            self._add_mccabe_steps_desorption_corrected(
                fig, stages_data, m, L, G, X_in, Y_in, X_out, Y_out
            )

        # ── Points remarquables ─────────────────────────────────────────────
        fig.add_trace(go.Scatter(
            x=[X_in], y=[Y_out],
            mode='markers',
            name=f'Entrée liquide (X_in={X_in:.4f}, Y_out={Y_out:.4f})',
            marker=dict(color='red', size=10, symbol='circle'),
            hovertemplate='Entrée liquide<br>X_in: %{x:.4f}<br>Y_out: %{y:.4f}<extra></extra>'
        ))
        fig.add_trace(go.Scatter(
            x=[X_out], y=[Y_in],
            mode='markers',
            name=f'Sortie liquide (X_out={X_out:.4f}, Y_in={Y_in:.4f})',
            marker=dict(color='orange', size=10, symbol='star'),
            hovertemplate='Sortie liquide<br>X_out: %{x:.4f}<br>Y_in: %{y:.4f}<extra></extra>'
        ))

        # ── Layout ──────────────────────────────────────────────────────────
        fig.update_layout(
            template='plotly_dark',
            title={
                'text': f'Diagramme McCabe-Thiele - Desorption a contre-courant ({len(stages_data) if stages_data else 0} etages)',
                'x': 0.5,
                'font': {'size': 18, 'color': self.colors['text']}
            },
            xaxis_title='X (rapport molaire phase liquide)',
            yaxis_title='Y (rapport molaire phase gaz)',
            xaxis=dict(gridcolor=self.colors['grid'], showgrid=True,
                       zeroline=True, zerolinecolor=self.colors['grid'], rangemode='tozero'),
            yaxis=dict(gridcolor=self.colors['grid'], showgrid=True,
                       zeroline=True, zerolinecolor=self.colors['grid'], rangemode='tozero'),
            plot_bgcolor=self.colors['background'],
            paper_bgcolor=self.colors['background'],
            font=dict(color=self.colors['text']),
            height=650,
            hovermode='closest',
            legend=dict(bgcolor='rgba(0,0,0,0.5)', bordercolor=self.colors['grid'], borderwidth=1)
        )

        return json.dumps(fig, cls=PlotlyJSONEncoder)

    def _add_mccabe_steps_desorption_corrected(self, fig, stages_data, m, L, G, X_in, Y_in, X_out, Y_out):
        """
        Trace l'escalier McCabe-Thiele correct pour la désorption.
        
        L'escalier part de (X_in, Y_out) en haut et descend :
          - Horizontal gauche → X_eq = Y_c / m  (courbe d'équilibre)
          - Vertical bas      → Y_op = Y_in + (L/G)*(X_eq - X_out)  (droite opératoire)
        """
        x_steps = [X_in]
        y_steps = [Y_out]

        Y_c = Y_out
        for i, stage in enumerate(stages_data):
            X_eq = stage['X_sortie']   # = Y_c / m
            Y_op = stage['Y_sortie']   # = Y_in + (L/G)*(X_eq - X_out)

            # Horizontal : (x_prev, Y_c) → (X_eq, Y_c)
            x_steps.append(X_eq)
            y_steps.append(Y_c)

            # Vertical : (X_eq, Y_c) → (X_eq, Y_op)
            x_steps.append(X_eq)
            y_steps.append(Y_op)

            # Annotation numéro d'étage
            fig.add_annotation(
                x=X_eq,
                y=(Y_c + Y_op) / 2,
                text=str(i + 1),
                showarrow=False,
                font=dict(color='white', size=11),
                bgcolor='rgba(0,0,0,0.7)',
                bordercolor='white',
                borderwidth=1
            )

            Y_c = Y_op

        fig.add_trace(go.Scatter(
            x=x_steps, y=y_steps,
            mode='lines',
            name=f"Étages McCabe-Thiele ({len(stages_data)})",
            line=dict(color=self.colors['steps'], width=2),
            hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
        ))
    
    def _add_mccabe_steps_absorption(self, fig, stages_data, m, L_prime, G_prime, X_in, Y_in):
        """Ajoute les étapes McCabe-Thiele pour l'absorption"""
        
        x_current = X_in
        y_current = Y_in
        
        for i, stage in enumerate(stages_data):
            # Ligne horizontale vers la courbe d'équilibre
            x_eq = y_current / m
            
            fig.add_trace(go.Scatter(
                x=[x_current, x_eq],
                y=[y_current, y_current],
                mode='lines',
                showlegend=False,
                line=dict(color=self.colors['steps'], width=2, dash='solid'),
                hovertemplate=f'Étage {i+1} - Horizontal<br>X: %{{x:.4f}}<br>Y: %{{y:.4f}}<extra></extra>'
            ))
            
            # Ligne verticale vers la droite opératoire
            y_new = (L_prime/G_prime) * (x_eq - X_in) + Y_in
            
            fig.add_trace(go.Scatter(
                x=[x_eq, x_eq],
                y=[y_current, y_new],
                mode='lines',
                showlegend=False,
                line=dict(color=self.colors['steps'], width=2, dash='solid'),
                hovertemplate=f'Étage {i+1} - Vertical<br>X: %{{x:.4f}}<br>Y: %{{y:.4f}}<extra></extra>'
            ))
            
            # Numérotation des étages
            fig.add_annotation(
                x=x_eq,
                y=(y_current + y_new) / 2,
                text=str(i + 1),
                showarrow=False,
                font=dict(color='white', size=12),
                bgcolor='rgba(0,0,0,0.7)',
                bordercolor='white',
                borderwidth=1
            )
            
            x_current = x_eq
            y_current = y_new
    
    def generate_3d_surface_plot(self, calculation_type, results):
        """
        Génère un graphique 3D de surface pour visualiser les variations
        
        Args:
            calculation_type: 'absorption' ou 'desorption'
            results: Résultats du calcul
        """
        
        if calculation_type == 'absorption':
            return self._generate_3d_absorption_surface(results)
        else:
            return self._generate_3d_desorption_surface(results)
    
    def _generate_3d_absorption_surface(self, results):
        """Génère une surface 3D pour l'absorption"""
        
        # Créer une grille de paramètres
        m_range = np.linspace(0.1, 2.0, 20)
        L_G_ratio = np.linspace(0.5, 3.0, 20)
        
        M, LG = np.meshgrid(m_range, L_G_ratio)
        
        # Calculer le nombre d'étages théoriques pour chaque combinaison
        stages_surface = np.zeros_like(M)
        
        base_y0 = results.get('y0', 0.08)
        base_y_obj = results.get('y_objectif', 0.008)
        
        for i in range(len(m_range)):
            for j in range(len(L_G_ratio)):
                # Simulation simplifiée pour la surface
                Y0 = base_y0 / (1 - base_y0)
                Y_obj = base_y_obj / (1 - base_y_obj)
                
                m_val = M[j, i]
                lg_ratio = LG[j, i]
                
                # Estimation du nombre d'étages
                if m_val > 0 and lg_ratio > 0:
                    A = 1 / (m_val * lg_ratio)
                    if A > 1:
                        stages_surface[j, i] = np.log(Y_obj/Y0) / np.log(1/A)
                    else:
                        stages_surface[j, i] = 50  # Maximum
                else:
                    stages_surface[j, i] = 50
                
                # Limiter les valeurs
                stages_surface[j, i] = min(max(stages_surface[j, i], 1), 50)
        
        # Créer la figure 3D
        fig = go.Figure(data=[go.Surface(
            z=stages_surface,
            x=M,
            y=LG,
            colorscale='Viridis',
            hovertemplate='m: %{x:.2f}<br>L/G: %{y:.2f}<br>Étages: %{z:.1f}<extra></extra>'
        )])
        
        fig.update_layout(
            template='plotly_dark',
            title='Surface 3D - Nombre d\'etages vs parametres (Absorption a contre-courant)',
            scene=dict(
                xaxis_title='Constante d\'equilibre (m)',
                yaxis_title='Rapport L/G',
                zaxis_title='Nombre d\'etages theoriques',
                bgcolor=self.colors['background']
            ),
            font=dict(color=self.colors['text']),
            height=600
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)
    
    def _generate_3d_desorption_surface(self, results):
        """Génère une surface 3D pour la désorption"""
        
        # Créer une grille de paramètres
        m_range = np.linspace(0.1, 2.0, 20)
        G_L_ratio = np.linspace(0.5, 3.0, 20)
        
        M, GL = np.meshgrid(m_range, G_L_ratio)
        
        # Calculer le nombre d'étages théoriques pour chaque combinaison
        stages_surface = np.zeros_like(M)
        
        base_x0 = results.get('x0', 0.06)
        base_x_obj = results.get('x_obj', 0.006)
        
        for i in range(len(m_range)):
            for j in range(len(G_L_ratio)):
                # Simulation simplifiée pour la surface
                X0 = base_x0 / (1 - base_x0)
                X_obj = base_x_obj / (1 - base_x_obj)
                
                m_val = M[j, i]
                gl_ratio = GL[j, i]
                
                # Estimation du nombre d'étages
                if m_val > 0 and gl_ratio > 0:
                    S = m_val * gl_ratio
                    if S > 1:
                        stages_surface[j, i] = np.log(X_obj/X0) / np.log(1/S)
                    else:
                        stages_surface[j, i] = 50  # Maximum
                else:
                    stages_surface[j, i] = 50
                
                # Limiter les valeurs
                stages_surface[j, i] = min(max(abs(stages_surface[j, i]), 1), 50)
        
        # Créer la figure 3D
        fig = go.Figure(data=[go.Surface(
            z=stages_surface,
            x=M,
            y=GL,
            colorscale='Plasma',
            hovertemplate='m: %{x:.2f}<br>G/L: %{y:.2f}<br>Étages: %{z:.1f}<extra></extra>'
        )])
        
        fig.update_layout(
            template='plotly_dark',
            title='Surface 3D - Nombre d\'etages vs parametres (Desorption a contre-courant)',
            scene=dict(
                xaxis_title='Constante d\'equilibre (m)',
                yaxis_title='Rapport G/L',
                zaxis_title='Nombre d\'etages theoriques',
                bgcolor=self.colors['background']
            ),
            font=dict(color=self.colors['text']),
            height=600
        )
        
        return json.dumps(fig, cls=PlotlyJSONEncoder)


# Instance globale du service
mccabe_service = McCabeThieleService()