# -*- coding: utf-8 -*-
"""
Service de calcul pour l'absorption/désorption à courant croisé
"""

import numpy as np
import plotly.graph_objects as go
from datetime import datetime


class CrossCurrentCalculator:
    """Calculateur pour les procédés à courant croisé"""
    
    @staticmethod
    def y_to_Y(y):
        """Convertir fraction molaire y en Y"""
        if y >= 1:
            return float('inf')
        return y / (1 - y)
    
    @staticmethod
    def Y_to_y(Y):
        """Convertir Y en fraction molaire y"""
        return Y / (1 + Y)
    
    def calculate_absorption_cross_current(self, G_prime, L_prime, m, y0, y_obj, N=None):
        """
        Calcul d'absorption à courant croisé
        
        Args:
            G_prime: Débit gaz (mol/h)
            L_prime: Débit solvant (mol/h)
            m: Constante d'équilibre
            y0: Fraction molaire entrée gaz
            y_obj: Fraction molaire objectif
            N: Nombre d'étages (optionnel, calculé automatiquement si None)
        
        Returns:
            dict: Résultats du calcul
        """
        start_time = datetime.now()
        
        try:
            Y0 = self.y_to_Y(y0)
            Y_obj = self.y_to_Y(y_obj)
            A = L_prime / (m * G_prime)
            
            Y_vals = [Y0]
            X_vals = [0.0]
            y_vals = [y0]
            
            convergence = False
            etages = 0
            
            # Calcul étage par étage jusqu'à atteindre l'objectif
            for i in range(1, 51):  # Maximum 50 étages
                Y_prev = Y_vals[-1]
                # À courant croisé: chaque étage reçoit du solvant frais
                Yi = Y_prev / (1 + A)
                Xi = Yi / m
                yi = self.Y_to_y(Yi)
                
                Y_vals.append(Yi)
                X_vals.append(Xi)
                y_vals.append(yi)
                etages = i
                
                # Vérifier si objectif atteint
                if yi <= y_obj:
                    convergence = True
                    break
                
                # Si N est spécifié, s'arrêter après N étages
                if N is not None and i >= N:
                    break
            
            # Calculs de performance
            taux = (Y0 - Y_vals[-1]) / Y0 * 100 if Y0 > 0 else 0
            quantite_absorbee = G_prime * (y0 - y_vals[-1])
            facteur_A = A
            
            # Vérifier si objectif atteint
            objectif_atteint = y_vals[-1] <= y_obj
            
            # Résultats détaillés par étage
            resultats = []
            for i in range(len(Y_vals)):
                resultats.append({
                    'etage': i,
                    'Y_entree': Y_vals[i],
                    'X_sortie': X_vals[i],
                    'Y_sortie': Y_vals[i],
                    'y_sortie': y_vals[i]
                })
            
            # Graphique McCabe-Thiele
            mccabe_graph = self._create_mccabe_thiele_graph(
                X_vals, Y_vals, m, 'Courant Croisé', G_prime=G_prime, L_prime=L_prime
            )
            
            # Graphique d'évolution des concentrations
            concentration_graph = self._create_concentration_graph(
                list(range(len(Y_vals))), Y_vals, X_vals, 'Courant Croisé'
            )
            
            # Graphique 3D du profil (schéma de colonne)
            profile_3d_graph = self._create_3d_profile_graph(
                list(range(len(Y_vals))), Y_vals, X_vals, 'Courant Croisé',
                G_prime=G_prime, L_prime=L_prime, y0=y0, y_final=y_vals[-1], N=etages
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000
            
            return {
                'success': True,
                'calculation_results': {
                    'G_prime': G_prime,
                    'L_prime': L_prime,
                    'm': m,
                    'y0': y0,
                    'y_objectif': y_obj,
                    'nb_etages': etages,
                    'taux': round(taux, 2),
                    'quantite': round(quantite_absorbee, 2),
                    'facteur_A': round(facteur_A, 3),
                    'objectif_atteint': objectif_atteint,
                    'convergence': convergence,
                    'resultats': resultats
                },
                'matplotlib_mccabe_graph': mccabe_graph,
                'concentration_evolution_graph': concentration_graph,
                '3d_profile_graph': profile_3d_graph,
                'performance': {
                    'execution_time_ms': round(execution_time, 2),
                    'memory_usage_mb': 0
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erreur calcul absorption courant croisé: {str(e)}'
            }
    
    def calculate_desorption_cross_current(self, G, L, m, x0, x_obj, N=None):
        """
        Calcul de désorption à courant croisé
        
        Args:
            G: Débit gaz (mol/h)
            L: Débit liquide (mol/h)
            m: Constante d'équilibre
            x0: Fraction molaire entrée liquide
            x_obj: Fraction molaire objectif
            N: Nombre d'étages max (optionnel, par défaut 50)
        
        Returns:
            dict: Résultats du calcul
        """
        start_time = datetime.now()
        
        try:
            X0 = x0 / (1 - x0) if x0 < 1 else float('inf')
            pente = G / L
            
            X_vals = [X0]
            Y_vals = [0.0]
            x_vals = [x0]
            
            X_courant = X0
            etages = 0
            convergence = False
            max_etages = N if N else 50
            
            # Calcul étage par étage jusqu'à atteindre l'objectif
            for i in range(1, max_etages + 1):
                # À courant croisé: chaque étage reçoit du gaz frais (Y=0)
                # Intersection analytique: m*X = pente*(X_courant - X)
                # X_sortant = (pente * X_courant) / (m + pente)
                X_sortant = (pente * X_courant) / (m + pente)
                Y_sortant = m * X_sortant
                
                # Vérifier la progression
                if X_sortant < 0 or X_sortant >= X_courant:
                    break
                
                x_sortie = X_sortant / (1 + X_sortant)
                y_sortie = Y_sortant / (1 + Y_sortant) if Y_sortant != float('inf') else 1
                
                X_vals.append(X_sortant)
                Y_vals.append(Y_sortant)
                x_vals.append(x_sortie)
                
                etages = i
                X_courant = X_sortant
                
                # Vérifier si objectif atteint
                if x_sortie <= x_obj:
                    convergence = True
                    break
            
            # Calculs de performance
            taux = (X0 - X_vals[-1]) / X0 * 100 if X0 > 0 else 0
            quantite_desorbee = L * (x0 - x_vals[-1])
            facteur_pente = pente
            
            # Vérifier si objectif atteint
            objectif_atteint = x_vals[-1] <= x_obj
            
            # Résultats détaillés par étage
            resultats = []
            for i in range(len(X_vals)):
                resultats.append({
                    'etage': i,
                    'X_entree': X_vals[i],
                    'Y_entree': 0.0 if i > 0 else Y_vals[i],
                    'X_sortie': X_vals[i],
                    'Y_sortie': Y_vals[i],
                    'x_sortie': x_vals[i]
                })
            
            # Graphique McCabe-Thiele
            mccabe_graph = self._create_mccabe_thiele_graph_desorption(
                Y_vals, X_vals, m, 'Courant Croisé'
            )
            
            # Graphique d'évolution des concentrations
            concentration_graph = self._create_concentration_graph_desorption(
                list(range(len(X_vals))), X_vals, Y_vals, 'Courant Croisé'
            )
            
            # Graphique 3D du profil
            profile_3d_graph = self._create_3d_profile_graph_desorption(
                list(range(len(X_vals))), X_vals, Y_vals, 'Courant Croisé',
                G=G, L=L, x0=x0, N=etages
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000
            
            return {
                'success': True,
                'calculation_results': {
                    'G': G,
                    'L': L,
                    'm': m,
                    'x0': x0,
                    'x_objectif': x_obj,
                    'nb_etages': etages,
                    'taux': round(taux, 2),
                    'quantite': round(quantite_desorbee, 2),
                    'facteur_S': round(facteur_pente, 3),
                    'objectif_atteint': objectif_atteint,
                    'convergence': convergence,
                    'resultats': resultats
                },
                'matplotlib_mccabe_graph': mccabe_graph,
                'concentration_evolution_graph': concentration_graph,
                '3d_profile_graph': profile_3d_graph,
                'performance': {
                    'execution_time_ms': round(execution_time, 2),
                    'memory_usage_mb': 0
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erreur calcul désorption courant croisé: {str(e)}'
            }
    
    def _create_mccabe_thiele_graph(self, X_vals, Y_vals, m, title_suffix, G_prime=None, L_prime=None):
        """
        Créer graphique McCabe-Thiele pour absorption à courant croisé.
        
        Pour chaque étage i :
          - Le gaz entre avec Y_{i-1} et du solvant frais X=0
          - Le gaz sort avec Yi = Y_{i-1}/(1+A), le liquide sort avec Xi = Yi/m
          - La droite opératoire relie (0, Y_{i-1}) à (Xi, Yi)  [pente = -L'/G']
          - Le point d'équilibre est (Xi, Yi) sur la courbe Y = m·X
        """
        try:
            fig = go.Figure()

            # --- Courbe d'équilibre ---
            X_max = max(X_vals[1:]) * 1.3 if len(X_vals) > 1 else 0.05
            X_eq = np.linspace(0, X_max, 200)
            Y_eq = m * X_eq

            fig.add_trace(go.Scatter(
                x=X_eq, y=Y_eq,
                mode='lines',
                name=f'Équilibre: Y = {m}·X',
                line=dict(color='blue', width=2.5)
            ))

            # --- Droites opératoires et points d'équilibre ---
            n_stages = len(Y_vals) - 1  # Y_vals[0] = Y0 entrée
            for i in range(n_stages):
                Y_in  = Y_vals[i]      # gaz entrant dans l'étage i+1
                Y_out = Y_vals[i + 1]  # gaz sortant  (= Yi sur courbe équilibre)
                X_out = X_vals[i + 1]  # liquide sortant (Xi = Yi/m)

                # Droite opératoire : de (0, Y_in) à (X_out, Y_out)
                fig.add_trace(go.Scatter(
                    x=[0, X_out],
                    y=[Y_in, Y_out],
                    mode='lines',
                    name='Droite opératoire' if i == 0 else None,
                    showlegend=(i == 0),
                    line=dict(color='red', width=2, dash='dash')
                ))

                # Point d'équilibre (Xi, Yi)
                fig.add_trace(go.Scatter(
                    x=[X_out], y=[Y_out],
                    mode='markers',
                    name=f'Étage {i + 1}',
                    marker=dict(color='red', size=10, symbol='circle')
                ))

                # Lignes pointillées vers les axes (repères visuels)
                fig.add_shape(type='line',
                    x0=0, y0=Y_out, x1=X_out, y1=Y_out,
                    line=dict(color='rgba(148,163,184,0.35)', width=1, dash='dot'))
                fig.add_shape(type='line',
                    x0=X_out, y0=0, x1=X_out, y1=Y_out,
                    line=dict(color='rgba(148,163,184,0.35)', width=1, dash='dot'))

            fig.update_layout(
                title=dict(
                    text='Diagramme McCabe-Thiele — Absorption à courant croisé',
                    font=dict(size=15, color='#e2e8f0'),
                    x=0.5, xanchor='center'
                ),
                xaxis=dict(
                    title=dict(text='X (rapport molaire liquide)', font=dict(color='#94a3b8')),
                    rangemode='tozero',
                    gridcolor='rgba(255,255,255,0.08)',
                    zerolinecolor='rgba(255,255,255,0.2)',
                    tickfont=dict(color='#94a3b8'),
                    linecolor='rgba(255,255,255,0.15)',
                    showgrid=True,
                ),
                yaxis=dict(
                    title=dict(text='Y (rapport molaire gaz)', font=dict(color='#94a3b8')),
                    rangemode='tozero',
                    gridcolor='rgba(255,255,255,0.08)',
                    zerolinecolor='rgba(255,255,255,0.2)',
                    tickfont=dict(color='#94a3b8'),
                    linecolor='rgba(255,255,255,0.15)',
                    showgrid=True,
                ),
                legend=dict(
                    x=0.01, y=0.99,
                    xanchor='left', yanchor='top',
                    bgcolor='rgba(15,23,42,0.85)',
                    bordercolor='rgba(255,255,255,0.15)',
                    borderwidth=1,
                    font=dict(color='#e2e8f0', size=12),
                    itemsizing='constant',
                ),
                hovermode='closest',
                plot_bgcolor='#0f172a',
                paper_bgcolor='#1e293b',
                font=dict(color='#e2e8f0'),
                height=460,
                margin=dict(l=65, r=30, t=55, b=60),
                autosize=True,
            )

            return fig.to_json()
        except Exception as e:
            return None
    
    def _create_mccabe_thiele_graph_desorption(self, Y_vals, X_vals, m, title_suffix):
        """
        Graphique McCabe-Thiele pour désorption à courant croisé.

        Pour chaque étage i :
          - Le liquide entre avec X_{i-1} et du gaz frais Y=0
          - Le liquide sort avec Xi = X_{i-1}/(1+S), le gaz sort avec Yi = m·Xi
          - La droite opératoire relie (X_{i-1}, 0) à (Xi, Yi)  [pente négative]
          - Le point d'équilibre est (Xi, Yi) sur la courbe Y = m·X
        """
        try:
            fig = go.Figure()

            # --- Courbe d'équilibre Y = m·X ---
            X_max = max(X_vals) * 1.3 if X_vals else 0.1
            X_eq = np.linspace(0, X_max, 200)
            Y_eq = m * X_eq

            fig.add_trace(go.Scatter(
                x=X_eq, y=Y_eq,
                mode='lines',
                name=f'Équilibre: Y = {m}·X',
                line=dict(color='blue', width=2.5)
            ))

            # --- Droites opératoires et points d'équilibre ---
            n_stages = len(X_vals) - 1  # X_vals[0] = X0 entrée
            for i in range(n_stages):
                X_in_stage  = X_vals[i]      # liquide entrant dans l'étage i+1
                X_out_stage = X_vals[i + 1]  # liquide sortant
                Y_out_stage = Y_vals[i + 1]  # gaz sortant (= m·Xi sur courbe équilibre)

                # Droite opératoire : de (X_in, 0) à (X_out, Y_out)
                fig.add_trace(go.Scatter(
                    x=[X_in_stage, X_out_stage],
                    y=[0, Y_out_stage],
                    mode='lines',
                    name='Droite opératoire' if i == 0 else None,
                    showlegend=(i == 0),
                    line=dict(color='red', width=2, dash='dash')
                ))

                # Point d'équilibre (Xi, Yi)
                fig.add_trace(go.Scatter(
                    x=[X_out_stage], y=[Y_out_stage],
                    mode='markers',
                    name=f'Étage {i + 1}',
                    marker=dict(color='red', size=10, symbol='circle')
                ))

                # Lignes pointillées vers les axes
                fig.add_shape(type='line',
                    x0=0, y0=Y_out_stage, x1=X_out_stage, y1=Y_out_stage,
                    line=dict(color='rgba(148,163,184,0.35)', width=1, dash='dot'))
                fig.add_shape(type='line',
                    x0=X_out_stage, y0=0, x1=X_out_stage, y1=Y_out_stage,
                    line=dict(color='rgba(148,163,184,0.35)', width=1, dash='dot'))

            fig.update_layout(
                title=dict(
                    text='Diagramme McCabe-Thiele — Désorption à courant croisé',
                    font=dict(size=15, color='#e2e8f0'),
                    x=0.5, xanchor='center'
                ),
                xaxis=dict(
                    title=dict(text='X (rapport molaire liquide)', font=dict(color='#94a3b8')),
                    rangemode='tozero',
                    gridcolor='rgba(255,255,255,0.08)',
                    zerolinecolor='rgba(255,255,255,0.2)',
                    tickfont=dict(color='#94a3b8'),
                    linecolor='rgba(255,255,255,0.15)',
                    showgrid=True,
                ),
                yaxis=dict(
                    title=dict(text='Y (rapport molaire gaz)', font=dict(color='#94a3b8')),
                    rangemode='tozero',
                    gridcolor='rgba(255,255,255,0.08)',
                    zerolinecolor='rgba(255,255,255,0.2)',
                    tickfont=dict(color='#94a3b8'),
                    linecolor='rgba(255,255,255,0.15)',
                    showgrid=True,
                ),
                legend=dict(
                    x=0.01, y=0.99,
                    xanchor='left', yanchor='top',
                    bgcolor='rgba(15,23,42,0.85)',
                    bordercolor='rgba(255,255,255,0.15)',
                    borderwidth=1,
                    font=dict(color='#e2e8f0', size=12),
                    itemsizing='constant',
                ),
                hovermode='closest',
                plot_bgcolor='#0f172a',
                paper_bgcolor='#1e293b',
                font=dict(color='#e2e8f0'),
                height=460,
                margin=dict(l=65, r=30, t=55, b=60),
                autosize=True,
            )

            return fig.to_json()
        except Exception as e:
            return None
    
    def _create_concentration_graph(self, stages, Y_vals, X_vals_out, title_suffix):
        """
        Graphique d'évolution des concentrations pour absorption à courant croisé.
        
        - Y (gaz) : décroît de Y0 à Yn (gaz traverse les étages en série)
        - X_out (liquide sortant par étage) : Xi = Yi/m, aussi décroissant
          X_vals_out[0] = 0 (avant étage 1), X_vals_out[i] = Xi sortant étage i
        """
        try:
            fig = go.Figure()

            # Étages : 0 = entrée, 1..N = sortie de chaque étage
            n = len(stages)

            # Courbe Y (gaz) — décroissante
            fig.add_trace(go.Scatter(
                x=stages,
                y=Y_vals,
                mode='lines+markers',
                name='Gaz (Y)',
                line=dict(color='#22c55e', width=2.5),
                marker=dict(size=8, color='#22c55e', symbol='circle')
            ))

            # Courbe X sortant par étage — décroissante (ignorer X[0]=0 qui est l'entrée solvant)
            # On trace X_out[1..N] aux étages 1..N
            if X_vals_out and len(X_vals_out) > 1:
                fig.add_trace(go.Scatter(
                    x=stages[1:],
                    y=X_vals_out[1:],
                    mode='lines+markers',
                    name='Liquide sortant (X)',
                    line=dict(color='#3b82f6', width=2.5),
                    marker=dict(size=8, color='#3b82f6', symbol='square')
                ))

            fig.update_layout(
                title=dict(
                    text='Évolution des concentrations — Absorption à courant croisé',
                    font=dict(size=14, color='#e2e8f0'),
                    x=0.5, xanchor='center'
                ),
                xaxis=dict(
                    title=dict(text="Numéro d'étage (0 = Entrée gaz)", font=dict(color='#94a3b8', size=13)),
                    tickfont=dict(color='#cbd5e1', size=12),
                    gridcolor='rgba(255,255,255,0.08)',
                    zerolinecolor='rgba(255,255,255,0.15)',
                    showgrid=True,
                    zeroline=False,
                    dtick=1,
                ),
                yaxis=dict(
                    title=dict(text='Rapport molaire', font=dict(color='#94a3b8', size=13)),
                    tickfont=dict(color='#cbd5e1', size=12),
                    gridcolor='rgba(255,255,255,0.08)',
                    zerolinecolor='rgba(255,255,255,0.15)',
                    showgrid=True,
                    zeroline=False,
                    rangemode='tozero',
                ),
                legend=dict(
                    font=dict(size=12, color='#e2e8f0'),
                    x=0.02, y=0.98,
                    bgcolor='rgba(30,41,59,0.9)',
                    bordercolor='#475569',
                    borderwidth=2
                ),
                margin=dict(l=0, r=0, t=40, b=25),
                plot_bgcolor='#1e293b',
                paper_bgcolor='#0f172a',
                hovermode='x unified',
                height=480,
            )

            return fig.to_json()
        except Exception as e:
            return None
    
    def _create_concentration_graph_desorption(self, stages, X_vals, Y_vals_out, title_suffix):
        """
        Graphique d'évolution des concentrations pour désorption à courant croisé.

        - X (liquide) : décroît de X0 à Xn (liquide traverse les étages en série)
        - Y_out (gaz sortant par étage) : Yi = m·Xi, aussi décroissant
        """
        try:
            fig = go.Figure()

            # Courbe X (liquide) — décroissante
            fig.add_trace(go.Scatter(
                x=stages,
                y=X_vals,
                mode='lines+markers',
                name='Liquide (X)',
                line=dict(color='#3b82f6', width=2.5),
                marker=dict(size=8, color='#3b82f6', symbol='circle')
            ))

            # Courbe Y sortant par étage — décroissante (ignorer Y[0]=0 entrée gaz frais)
            if Y_vals_out and len(Y_vals_out) > 1:
                fig.add_trace(go.Scatter(
                    x=stages[1:],
                    y=Y_vals_out[1:],
                    mode='lines+markers',
                    name='Gaz sortant (Y)',
                    line=dict(color='#22c55e', width=2.5),
                    marker=dict(size=8, color='#22c55e', symbol='square')
                ))

            fig.update_layout(
                title=dict(
                    text='Évolution des concentrations — Désorption à courant croisé',
                    font=dict(size=14, color='#e2e8f0'),
                    x=0.5, xanchor='center'
                ),
                xaxis=dict(
                    title=dict(text="Numéro d'étage (0 = Entrée liquide)", font=dict(color='#94a3b8', size=13)),
                    tickfont=dict(color='#cbd5e1', size=12),
                    gridcolor='rgba(255,255,255,0.08)',
                    zerolinecolor='rgba(255,255,255,0.15)',
                    showgrid=True,
                    zeroline=False,
                    dtick=1,
                ),
                yaxis=dict(
                    title=dict(text='Rapport molaire', font=dict(color='#94a3b8', size=13)),
                    tickfont=dict(color='#cbd5e1', size=12),
                    gridcolor='rgba(255,255,255,0.08)',
                    zerolinecolor='rgba(255,255,255,0.15)',
                    showgrid=True,
                    zeroline=False,
                    rangemode='tozero',
                ),
                legend=dict(
                    font=dict(size=12, color='#e2e8f0'),
                    x=0.02, y=0.98,
                    bgcolor='rgba(30,41,59,0.9)',
                    bordercolor='#475569',
                    borderwidth=2
                ),
                margin=dict(l=0, r=0, t=40, b=25),
                plot_bgcolor='#1e293b',
                paper_bgcolor='#0f172a',
                hovermode='x unified',
                height=480,
            )

            return fig.to_json()
        except Exception as e:
            return None
    
    def _create_3d_profile_graph(self, stages, Y_vals, X_vals, title_suffix, G_prime=None, L_prime=None, y0=None, y_final=None, N=None):
        """
        Créer un schéma de colonne pour absorption à courant croisé.
        
        Schéma vertical montrant :
        - Liquide entrant en haut (L', X_in)
        - Gaz entrant à gauche (G', Y_in)
        - Colonne au centre avec N étages
        - Gaz sortant à droite (G', Y_out)
        - Liquide sortant en bas (L', X_out)
        """
        try:
            import plotly.graph_objects as go
            
            # Paramètres du schéma
            col_width = 3
            col_height = 6
            col_x = 5
            col_y_bottom = 2
            col_y_top = col_y_bottom + col_height
            
            # Nombre d'étages
            n_stages = N if N else len(Y_vals) - 1
            
            # Valeurs finales
            Y_in = Y_vals[0] if Y_vals else 0
            Y_out = Y_vals[-1] if Y_vals else 0
            X_out = X_vals[-1] if X_vals else 0
            
            fig = go.Figure()
            
            # --- Colonne principale (rectangle bleu) ---
            fig.add_shape(type='rect',
                x0=col_x, y0=col_y_bottom, x1=col_x + col_width, y1=col_y_top,
                fillcolor='rgba(59, 130, 246, 0.15)',
                line=dict(color='#3b82f6', width=3))
            
            # --- Texte N étages au centre ---
            fig.add_annotation(
                x=col_x + col_width/2, y=(col_y_bottom + col_y_top)/2,
                text=f'<b>N = {n_stages}</b><br>Étages',
                showarrow=False,
                font=dict(size=18, color='#fbbf24', family='Arial Black'),
                bgcolor='rgba(251, 191, 36, 0.2)',
                bordercolor='#fbbf24',
                borderwidth=2,
                borderpad=8
            )
            
            # --- Liquide entrant (haut) ---
            fig.add_shape(type='rect',
                x0=col_x + 0.3, y0=col_y_top + 0.5, x1=col_x + col_width - 0.3, y1=col_y_top + 1.5,
                fillcolor='rgba(59, 130, 246, 0.3)',
                line=dict(color='#3b82f6', width=2))
            fig.add_annotation(
                x=col_x + col_width/2, y=col_y_top + 1,
                text=f'<b>Liquide Entrant</b><br>L\' = {L_prime:.1f} mol/h<br>X<sub>in</sub> = 0.0000',
                showarrow=False,
                font=dict(size=11, color='#e2e8f0'),
                bgcolor='rgba(30, 41, 59, 0.9)',
                bordercolor='#3b82f6',
                borderwidth=2,
                borderpad=6
            )
            
            # Flèche liquide entrant (pointe vers le bas dans la colonne)
            fig.add_annotation(
                x=col_x + col_width/2, y=col_y_top,
                ax=col_x + col_width/2, ay=col_y_top + 0.8,
                xref='x', yref='y', axref='x', ayref='y',
                showarrow=True,
                arrowhead=2, arrowsize=1.5, arrowwidth=3,
                arrowcolor='#3b82f6'
            )
            
            # --- Gaz entrant (gauche) ---
            fig.add_shape(type='rect',
                x0=col_x - 2.5, y0=col_y_bottom + col_height/2 - 0.6,
                x1=col_x - 0.5, y1=col_y_bottom + col_height/2 + 0.6,
                fillcolor='rgba(34, 197, 94, 0.3)',
                line=dict(color='#22c55e', width=2))
            fig.add_annotation(
                x=col_x - 1.5, y=col_y_bottom + col_height/2,
                text=f'<b>Gaz Entrant</b><br>G\' = {G_prime:.1f} mol/h<br>Y<sub>in</sub> = {Y_in:.6f}',
                showarrow=False,
                font=dict(size=11, color='#e2e8f0'),
                bgcolor='rgba(30, 41, 59, 0.9)',
                bordercolor='#22c55e',
                borderwidth=2,
                borderpad=6
            )
            
            # Flèche gaz entrant (pointe vers la droite dans la colonne)
            fig.add_annotation(
                x=col_x, y=col_y_bottom + col_height/2,
                ax=col_x - 0.8, ay=col_y_bottom + col_height/2,
                xref='x', yref='y', axref='x', ayref='y',
                showarrow=True,
                arrowhead=2, arrowsize=1.5, arrowwidth=3,
                arrowcolor='#22c55e'
            )
            
            # --- Gaz sortant (droite) ---
            fig.add_shape(type='rect',
                x0=col_x + col_width + 0.5, y0=col_y_bottom + col_height/2 - 0.6,
                x1=col_x + col_width + 2.5, y1=col_y_bottom + col_height/2 + 0.6,
                fillcolor='rgba(34, 197, 94, 0.3)',
                line=dict(color='#22c55e', width=2))
            fig.add_annotation(
                x=col_x + col_width + 1.5, y=col_y_bottom + col_height/2,
                text=f'<b>Gaz Sortant</b><br>G\' = {G_prime:.1f} mol/h<br>Y<sub>out</sub> = {Y_out:.6f}',
                showarrow=False,
                font=dict(size=11, color='#e2e8f0'),
                bgcolor='rgba(30, 41, 59, 0.9)',
                bordercolor='#22c55e',
                borderwidth=2,
                borderpad=6
            )
            
            # Flèche gaz sortant (pointe vers la droite hors de la colonne)
            fig.add_annotation(
                x=col_x + col_width + 0.8, y=col_y_bottom + col_height/2,
                ax=col_x + col_width, ay=col_y_bottom + col_height/2,
                xref='x', yref='y', axref='x', ayref='y',
                showarrow=True,
                arrowhead=2, arrowsize=1.5, arrowwidth=3,
                arrowcolor='#22c55e'
            )
            
            # --- Liquide sortant (bas) ---
            fig.add_shape(type='rect',
                x0=col_x + 0.3, y0=col_y_bottom - 1.5, x1=col_x + col_width - 0.3, y1=col_y_bottom - 0.5,
                fillcolor='rgba(59, 130, 246, 0.3)',
                line=dict(color='#3b82f6', width=2))
            fig.add_annotation(
                x=col_x + col_width/2, y=col_y_bottom - 1,
                text=f'<b>Liquide Sortant</b><br>L\' = {L_prime:.1f} mol/h<br>X<sub>out</sub> = {X_out:.6f}',
                showarrow=False,
                font=dict(size=11, color='#e2e8f0'),
                bgcolor='rgba(30, 41, 59, 0.9)',
                bordercolor='#3b82f6',
                borderwidth=2,
                borderpad=6
            )
            
            # Flèche liquide sortant (pointe vers le bas hors de la colonne)
            fig.add_annotation(
                x=col_x + col_width/2, y=col_y_bottom - 0.8,
                ax=col_x + col_width/2, ay=col_y_bottom,
                xref='x', yref='y', axref='x', ayref='y',
                showarrow=True,
                arrowhead=2, arrowsize=1.5, arrowwidth=3,
                arrowcolor='#3b82f6'
            )
            
            # --- Configuration du layout ---
            fig.update_layout(
                xaxis=dict(
                    range=[0, 11],
                    showgrid=False,
                    showticklabels=False,
                    zeroline=False,
                    visible=False
                ),
                yaxis=dict(
                    range=[0, 10],
                    showgrid=False,
                    showticklabels=False,
                    zeroline=False,
                    visible=False,
                    scaleanchor='x',
                    scaleratio=1
                ),
                plot_bgcolor='#0f172a',
                paper_bgcolor='#1e293b',
                height=500,
                margin=dict(l=20, r=20, t=60, b=20),
                showlegend=False
            )
            
            return fig.to_json()
        except Exception as e:
            print(f"Error creating column schema: {e}")
            return None
    
    def _create_3d_profile_graph_desorption(self, stages, X_vals, Y_vals, title_suffix, G=None, L=None, x0=None, N=None):
        """
        Schéma de colonne pour désorption à courant croisé.

        - Liquide entrant à gauche (L, X_in)
        - Gaz frais entrant en bas (G, Y=0)
        - Colonne au centre avec N étages
        - Liquide sortant à droite (L, X_out)
        - Gaz sortant en haut (G, Y_out)
        """
        try:
            col_width = 3
            col_height = 6
            col_x = 5
            col_y_bottom = 2
            col_y_top = col_y_bottom + col_height

            n_stages = N if N else len(X_vals) - 1
            X_in  = X_vals[0] if X_vals else 0
            X_out = X_vals[-1] if X_vals else 0
            Y_out = Y_vals[-1] if Y_vals else 0

            fig = go.Figure()

            # Colonne principale
            fig.add_shape(type='rect',
                x0=col_x, y0=col_y_bottom, x1=col_x + col_width, y1=col_y_top,
                fillcolor='rgba(168, 85, 247, 0.15)',
                line=dict(color='#a855f7', width=3))

            # N étages au centre
            fig.add_annotation(
                x=col_x + col_width/2, y=(col_y_bottom + col_y_top)/2,
                text=f'<b>N = {n_stages}</b><br>Étages',
                showarrow=False,
                font=dict(size=18, color='#fbbf24', family='Arial Black'),
                bgcolor='rgba(251, 191, 36, 0.2)',
                bordercolor='#fbbf24',
                borderwidth=2,
                borderpad=8
            )

            # Liquide entrant (gauche)
            fig.add_shape(type='rect',
                x0=col_x - 2.5, y0=col_y_bottom + col_height/2 - 0.6,
                x1=col_x - 0.5, y1=col_y_bottom + col_height/2 + 0.6,
                fillcolor='rgba(59, 130, 246, 0.3)',
                line=dict(color='#3b82f6', width=2))
            fig.add_annotation(
                x=col_x - 1.5, y=col_y_bottom + col_height/2,
                text=f'<b>Liquide Entrant</b><br>L = {L:.1f} mol/h<br>X<sub>in</sub> = {X_in:.6f}',
                showarrow=False,
                font=dict(size=11, color='#e2e8f0'),
                bgcolor='rgba(30, 41, 59, 0.9)',
                bordercolor='#3b82f6',
                borderwidth=2,
                borderpad=6
            )
            fig.add_annotation(
                x=col_x, y=col_y_bottom + col_height/2,
                ax=col_x - 0.8, ay=col_y_bottom + col_height/2,
                xref='x', yref='y', axref='x', ayref='y',
                showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=3,
                arrowcolor='#3b82f6'
            )

            # Gaz frais entrant (bas)
            fig.add_shape(type='rect',
                x0=col_x + 0.3, y0=col_y_bottom - 1.5,
                x1=col_x + col_width - 0.3, y1=col_y_bottom - 0.5,
                fillcolor='rgba(34, 197, 94, 0.3)',
                line=dict(color='#22c55e', width=2))
            fig.add_annotation(
                x=col_x + col_width/2, y=col_y_bottom - 1,
                text=f'<b>Gaz Entrant (frais)</b><br>G = {G:.1f} mol/h<br>Y<sub>in</sub> = 0.0000',
                showarrow=False,
                font=dict(size=11, color='#e2e8f0'),
                bgcolor='rgba(30, 41, 59, 0.9)',
                bordercolor='#22c55e',
                borderwidth=2,
                borderpad=6
            )
            fig.add_annotation(
                x=col_x + col_width/2, y=col_y_bottom,
                ax=col_x + col_width/2, ay=col_y_bottom - 0.8,
                xref='x', yref='y', axref='x', ayref='y',
                showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=3,
                arrowcolor='#22c55e'
            )

            # Liquide sortant (droite)
            fig.add_shape(type='rect',
                x0=col_x + col_width + 0.5, y0=col_y_bottom + col_height/2 - 0.6,
                x1=col_x + col_width + 2.5, y1=col_y_bottom + col_height/2 + 0.6,
                fillcolor='rgba(59, 130, 246, 0.3)',
                line=dict(color='#3b82f6', width=2))
            fig.add_annotation(
                x=col_x + col_width + 1.5, y=col_y_bottom + col_height/2,
                text=f'<b>Liquide Sortant</b><br>L = {L:.1f} mol/h<br>X<sub>out</sub> = {X_out:.6f}',
                showarrow=False,
                font=dict(size=11, color='#e2e8f0'),
                bgcolor='rgba(30, 41, 59, 0.9)',
                bordercolor='#3b82f6',
                borderwidth=2,
                borderpad=6
            )
            fig.add_annotation(
                x=col_x + col_width + 0.8, y=col_y_bottom + col_height/2,
                ax=col_x + col_width, ay=col_y_bottom + col_height/2,
                xref='x', yref='y', axref='x', ayref='y',
                showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=3,
                arrowcolor='#3b82f6'
            )

            # Gaz sortant (haut)
            fig.add_shape(type='rect',
                x0=col_x + 0.3, y0=col_y_top + 0.5,
                x1=col_x + col_width - 0.3, y1=col_y_top + 1.5,
                fillcolor='rgba(34, 197, 94, 0.3)',
                line=dict(color='#22c55e', width=2))
            fig.add_annotation(
                x=col_x + col_width/2, y=col_y_top + 1,
                text=f'<b>Gaz Sortant</b><br>G = {G:.1f} mol/h<br>Y<sub>out</sub> = {Y_out:.6f}',
                showarrow=False,
                font=dict(size=11, color='#e2e8f0'),
                bgcolor='rgba(30, 41, 59, 0.9)',
                bordercolor='#22c55e',
                borderwidth=2,
                borderpad=6
            )
            fig.add_annotation(
                x=col_x + col_width/2, y=col_y_top + 0.8,
                ax=col_x + col_width/2, ay=col_y_top,
                xref='x', yref='y', axref='x', ayref='y',
                showarrow=True, arrowhead=2, arrowsize=1.5, arrowwidth=3,
                arrowcolor='#22c55e'
            )

            fig.update_layout(
                xaxis=dict(range=[0, 11], showgrid=False, showticklabels=False, zeroline=False, visible=False),
                yaxis=dict(range=[0, 10], showgrid=False, showticklabels=False, zeroline=False, visible=False,
                           scaleanchor='x', scaleratio=1),
                plot_bgcolor='#0f172a',
                paper_bgcolor='#1e293b',
                height=500,
                margin=dict(l=20, r=20, t=60, b=20),
                showlegend=False
            )

            return fig.to_json()
        except Exception as e:
            print(f"Error creating desorption column schema: {e}")
            return None
