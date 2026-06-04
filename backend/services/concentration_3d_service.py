"""
Service pour générer les graphiques de concentration et schéma de colonne
VERSION PLOTLY - Graphiques interactifs modernes
"""
import plotly.graph_objects as go
import numpy as np


class Concentration3DService:
    """Service pour générer les graphiques d'évolution de concentration et schéma de colonne avec Plotly"""
    
    def generate_absorption_graphs(self, G, L, m_cst, y_in, x_in, y_out, calc_results=None):
        """
        Génère les graphiques de concentration et schéma de colonne pour l'absorption.
        Si calc_results est fourni, utilise les étages déjà calculés (évite la divergence).
        """
        try:
            # Conversion en rapports molaires
            Y_in = y_in / (1 - y_in) if y_in < 1 else 0
            X_in = x_in / (1 - x_in) if x_in != 1 and x_in > 0 else 0
            Y_out = y_out / (1 - y_out) if y_out < 1 else 0
            X_out = X_in + (G / L) * (Y_in - Y_out)

            X_eq_max = max(X_out, Y_in / m_cst) * 1.2

            # ── Utiliser les étages pré-calculés si disponibles ──────────────
            if calc_results and 'resultats' in calc_results:
                resultats = calc_results['resultats']
                stage_count = len(resultats)

                # Utiliser x_steps/y_steps pré-calculés si disponibles
                if 'x_steps' in calc_results and 'y_steps' in calc_results:
                    x_steps   = calc_results['x_steps']
                    y_steps   = calc_results['y_steps']
                    stages_list = calc_results.get('stages_list', list(range(stage_count + 1)))
                    X_prof    = calc_results.get('X_prof', [X_in])
                    Y_prof    = calc_results.get('Y_prof', [Y_out])
                else:
                    # Reconstruire depuis resultats
                    x_steps = [X_in]
                    y_steps = [Y_out]
                    stages_list = [0]
                    X_prof = [X_in]
                    Y_prof = [Y_out]
                    Y_c = Y_out
                    for i, r in enumerate(resultats):
                        X_eq = r['X_sortie']
                        Y_op = r['Y_sortie']
                        x_steps.extend([X_eq, X_eq])
                        y_steps.append(Y_c)
                        y_steps.append(Y_op)
                        stages_list.append(i + 1)
                        X_prof.append(X_eq)
                        Y_prof.append(Y_op)
                        Y_c = Y_op

            else:
                # Fallback : recalcul local (même algorithme que simuler_absorption)
                if Y_out <= m_cst * X_in or Y_in <= m_cst * X_out:
                    return {'success': False, 'error': "Erreur (Pincement)"}

                x_steps, y_steps = [X_in], [Y_out]
                Y_c = Y_out
                stage_count = 0
                stages_list = [0]
                X_prof, Y_prof = [X_in], [Y_out]

                while Y_c < Y_in and stage_count < 50:
                    stage_count += 1
                    X_eq = Y_c / m_cst
                    x_steps.extend([X_eq, X_eq])
                    y_steps.append(Y_c)
                    Y_op = Y_out + (L / G) * (X_eq - X_in)
                    if Y_op >= Y_in:
                        y_steps.append(Y_in)
                        stages_list.append(stage_count)
                        X_prof.append(X_eq)
                        Y_prof.append(Y_in)
                        break
                    y_steps.append(Y_op)
                    Y_c = Y_op
                    stages_list.append(stage_count)
                    X_prof.append(X_eq)
                    Y_prof.append(Y_c)
            
            # --- 1. GRAPHIQUE MCCABE-THIELE AVEC PLOTLY (INTERACTIF) ---
            X_line = np.linspace(0, X_eq_max, 100)
            Y_eq_line = m_cst * X_line
            
            fig_plotly = go.Figure()
            
            # Courbe d'équilibre (noir/gris foncé)
            fig_plotly.add_trace(go.Scatter(
                x=X_line,
                y=Y_eq_line,
                mode='lines',
                name="Courbe d'équilibre (Y = mX)",
                line=dict(color='#ef4444', width=2.5),
                hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
            ))
            
            # Droite opératoire (cyan #00FFFF)
            fig_plotly.add_trace(go.Scatter(
                x=[X_in, X_out],
                y=[Y_out, Y_in],
                mode='lines+markers',
                name="Droite opératoire (Absorption)",
                line=dict(color='#00FFFF', width=3),
                marker=dict(size=10, color='#00FFFF'),
                hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
            ))
            
            # Étages (magenta #FF00FF)
            fig_plotly.add_trace(go.Scatter(
                x=x_steps,
                y=y_steps,
                mode='lines',
                name=f"Nombre d'étages = {stage_count}",
                line=dict(color='#FF00FF', width=2),
                hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
            ))
            
            # Layout avec thème clair
            fig_plotly.update_layout(
                title=dict(
                    text="Construction de McCabe et Thiele - Absorption a contre-courant",
                    font=dict(size=16, color='#1e293b')
                ),
                xaxis=dict(
                    title="Rapport molaire phase liquide (X)",
                    gridcolor='rgba(255,255,255,0.1)',
                    zerolinecolor='rgba(150,150,150,0.5)',
                    color='#1e293b',
                    rangemode='tozero'
                ),
                yaxis=dict(
                    title="Rapport molaire phase gaz (Y)",
                    gridcolor='rgba(255,255,255,0.1)',
                    zerolinecolor='rgba(150,150,150,0.5)',
                    color='#1e293b',
                    rangemode='tozero'
                ),
                plot_bgcolor='#1e293b',
                paper_bgcolor='#0f172a',
                font=dict(color='#e2e8f0'),
                hovermode='closest',
                legend=dict(
                    x=0.02,
                    y=0.98,
                    bgcolor='rgba(30,41,59,0.9)',
                    bordercolor='#475569',
                    borderwidth=1
                ),
                height=400,
                margin=dict(l=50, r=10, t=30, b=0)
            )
            
            plot_mccabe = fig_plotly.to_json()
            
            # --- 2. GRAPHIQUE EVOLUTION DES CONCENTRATIONS AVEC PLOTLY (STYLE BLANC) ---
            fig_concentration = go.Figure()
            
            # Liquide (X) - Vert
            fig_concentration.add_trace(go.Scatter(
                x=stages_list,
                y=X_prof,
                mode='lines+markers',
                name='Liquide (X)',
                line=dict(color='#10b981', width=3),
                marker=dict(size=8, color='#10b981', symbol='circle')
            ))
            
            # Gaz (Y) - Bleu
            fig_concentration.add_trace(go.Scatter(
                x=stages_list,
                y=Y_prof,
                mode='lines+markers',
                name='Gaz (Y)',
                line=dict(color='#3b82f6', width=3),
                marker=dict(size=8, color='#3b82f6', symbol='square')
            ))
            
            fig_concentration.update_layout(
                title=dict(
                    text="Profil de concentration",
                    font=dict(size=16, color='#1e293b')
                ),
                xaxis=dict(
                    title="Numéro d'étage (0 = Entrée liquide)",
                    titlefont=dict(size=14, color='#e2e8f0'),
                    tickfont=dict(size=12, color='#cbd5e1'),
                    gridcolor='rgba(255,255,255,0.1)',
                    showgrid=True,
                    zeroline=False
                ),
                yaxis=dict(
                    title="Rapport molaire",
                    titlefont=dict(size=14, color='#e2e8f0'),
                    tickfont=dict(size=12, color='#cbd5e1'),
                    gridcolor='rgba(255,255,255,0.1)',
                    showgrid=True,
                    zeroline=False
                ),
                plot_bgcolor='#1e293b',
                paper_bgcolor='#0f172a',
                font=dict(color='#e2e8f0'),
                hovermode='x unified',
                legend=dict(
                    x=0.02,
                    y=0.98,
                    bgcolor='rgba(30,41,59,0.9)',
                    bordercolor='#475569',
                    borderwidth=2,
                    font=dict(size=12, color='#e2e8f0')
                ),
                height=540,
                margin=dict(l=0, r=0, t=15, b=25)
            )
            
            plot_evol = fig_concentration.to_json()
            
            # --- 3. SCHÉMA DE LA COLONNE AVEC PLOTLY (STYLE BLANC) ---
            fig_schema = go.Figure()
            
            # Corps de la colonne (rectangle)
            fig_schema.add_shape(
                type="rect",
                x0=0.35, y0=0.15, x1=0.65, y1=0.85,
                line=dict(color='#3b82f6', width=6),
                fillcolor='rgba(224,242,254,0.3)'
            )
            
            # Lignes d'étages
            num_drawn = min(stage_count, 8) if stage_count > 0 else 3
            for i in range(1, num_drawn):
                y_pos = 0.15 + i * (0.7 / num_drawn)
                fig_schema.add_shape(
                    type="line",
                    x0=0.35, y0=y_pos, x1=0.65, y1=y_pos,
                    line=dict(color='#0284c7', width=3, dash='dash')
                )
            
            # Boîte nombre d'étages
            fig_schema.add_annotation(
                x=0.5, y=0.5,
                text=f"N = {stage_count}<br>Étages",
                showarrow=False,
                font=dict(size=20, color='#1f2937', family='Arial Black'),
                bgcolor='#fbbf24',
                bordercolor='#d97706',
                borderwidth=4,
                borderpad=8
            )
            
            # Flèches et annotations
            # Liquide Entrant (haut)
            fig_schema.add_annotation(
                x=0.5, y=0.93,
                text=f"Liquide Entrant<br>L = {L:.1f} mol/h<br>X<sub>in</sub> = {X_in:.4f}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='#10b981',
                ax=0, ay=-40,
                font=dict(size=14, color='#065f46'),
                bgcolor='#d1fae5',
                bordercolor='#10b981',
                borderwidth=3,
                borderpad=8
            )
            
            # Liquide Sortant (bas)
            fig_schema.add_annotation(
                x=0.5, y=0.07,
                text=f"Liquide Sortant<br>L = {L:.1f} mol/h<br>X<sub>out</sub> = {X_out:.4f}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='#10b981',
                ax=0, ay=40,
                font=dict(size=14, color='#065f46'),
                bgcolor='#d1fae5',
                bordercolor='#10b981',
                borderwidth=3,
                borderpad=8
            )
            
            # Gaz Entrant (gauche bas)
            fig_schema.add_annotation(
                x=0.15, y=0.3,
                text=f"Gaz Entrant<br>G = {G:.1f} mol/h<br>Y<sub>in</sub> = {Y_in:.4f}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='#3b82f6',
                ax=50, ay=0,
                font=dict(size=14, color='#1e3a8a'),
                bgcolor='#dbeafe',
                bordercolor='#3b82f6',
                borderwidth=3,
                borderpad=8
            )
            
            # Gaz Sortant (droite haut)
            fig_schema.add_annotation(
                x=0.85, y=0.7,
                text=f"Gaz Sortant<br>G = {G:.1f} mol/h<br>Y<sub>out</sub> = {Y_out:.4f}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='#3b82f6',
                ax=-50, ay=0,
                font=dict(size=14, color='#1e3a8a'),
                bgcolor='#dbeafe',
                bordercolor='#3b82f6',
                borderwidth=3,
                borderpad=8
            )
            
            fig_schema.update_layout(
                xaxis=dict(range=[0, 1], showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(range=[0, 1], showgrid=False, showticklabels=False, zeroline=False),
                plot_bgcolor='#1e293b',
                paper_bgcolor='#0f172a',
                height=540,
                showlegend=False,
                margin=dict(l=0, r=0, t=0, b=0)
            )
            
            plot_3d = fig_schema.to_json()
            
            return {
                'success': True,
                'mccabe_graph': plot_mccabe,
                'concentration_graph': plot_evol,
                '3d_graph': plot_3d,
                'stage_count': stage_count
            }
            
        except Exception as e:
            print(f"Error in generate_absorption_graphs: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_desorption_graphs(self, G, L, m_cst, y_in, x_in, x_out, calc_results=None):
        """
        Génère les graphiques de concentration et schéma de colonne pour la désorption.
        Si calc_results est fourni, utilise les étages déjà calculés.
        """
        try:
            # Conversion en rapports molaires
            Y_in = y_in / (1 - y_in) if y_in < 1 and y_in > 0 else 0
            X_in = x_in / (1 - x_in) if x_in != 1 and x_in > 0 else 0
            X_out = x_out / (1 - x_out) if x_out != 1 and x_out > 0 else 0
            Y_out = Y_in + (L / G) * (X_in - X_out)

            X_eq_max = X_in * 1.3

            # ── Utiliser les étages pré-calculés si disponibles ──────────────
            if calc_results and 'resultats' in calc_results:
                resultats = calc_results['resultats']
                stage_count = len(resultats)

                # Utiliser x_steps/y_steps pré-calculés si disponibles
                if 'x_steps' in calc_results and 'y_steps' in calc_results:
                    x_steps     = calc_results['x_steps']
                    y_steps     = calc_results['y_steps']
                    stages_list = calc_results.get('stages_list', list(range(stage_count + 1)))
                    X_prof      = calc_results.get('X_prof', [X_in])
                    Y_prof      = calc_results.get('Y_prof', [Y_out])
                else:
                    x_steps = [X_in]
                    y_steps = [Y_out]
                    stages_list = [0]
                    X_prof = [X_in]
                    Y_prof = [Y_out]
                    Y_c = Y_out
                    for i, r in enumerate(resultats):
                        X_eq = r['X_sortie']
                        Y_op = r['Y_sortie']
                        x_steps.append(X_eq)
                        y_steps.append(Y_c)
                        x_steps.append(X_eq)
                        y_steps.append(Y_op)
                        stages_list.append(i + 1)
                        X_prof.append(X_eq)
                        Y_prof.append(Y_op)
                        Y_c = Y_op

            else:
                # Fallback : recalcul local (même algorithme que simuler_desorption)
                if Y_out >= m_cst * X_in or Y_in >= m_cst * X_out:
                    return {'success': False, 'error': "Erreur (Pincement)"}

                x_steps, y_steps = [X_in], [Y_out]
                Y_c = Y_out
                stage_count = 0
                stages_list = [0]
                X_prof, Y_prof = [X_in], [Y_out]

                while Y_c > Y_in and stage_count < 50:
                    stage_count += 1
                    X_eq = Y_c / m_cst
                    Y_op = Y_in + (L / G) * (X_eq - X_out)
                    x_steps.append(X_eq)
                    y_steps.append(Y_c)
                    x_steps.append(X_eq)
                    y_steps.append(Y_op)
                    stages_list.append(stage_count)
                    X_prof.append(X_eq)
                    Y_prof.append(Y_op)
                    if X_eq <= X_out:
                        break
                    Y_c = Y_op
            
            # --- 1. GRAPHIQUE MCCABE-THIELE AVEC PLOTLY (INTERACTIF) ---
            X_line = np.linspace(0, X_eq_max, 100)
            Y_eq_line = m_cst * X_line
            
            fig_plotly = go.Figure()
            
            # Courbe d'équilibre (noir/gris foncé)
            fig_plotly.add_trace(go.Scatter(
                x=X_line,
                y=Y_eq_line,
                mode='lines',
                name="Courbe d'équilibre (Y = mX)",
                line=dict(color='#ef4444', width=2.5),
                hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
            ))
            
            # Droite opératoire (gold #FFD700)
            fig_plotly.add_trace(go.Scatter(
                x=[X_out, X_in],
                y=[Y_in, Y_out],
                mode='lines+markers',
                name="Droite opératoire (Désorption)",
                line=dict(color='#FFD700', width=3),
                marker=dict(size=10, color='#FFD700'),
                hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
            ))
            
            # Étages (magenta #FF00FF)
            fig_plotly.add_trace(go.Scatter(
                x=x_steps,
                y=y_steps,
                mode='lines',
                name=f"Nombre d'étages = {stage_count}",
                line=dict(color='#FF00FF', width=2),
                hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
            ))
            
            # Layout avec thème clair
            fig_plotly.update_layout(
                title=dict(
                    text="Construction de McCabe et Thiele - Desorption a contre-courant",
                    font=dict(size=16, color='#1e293b')
                ),
                xaxis=dict(
                    title="Rapport molaire phase liquide (X)",
                    gridcolor='rgba(255,255,255,0.1)',
                    zerolinecolor='rgba(150,150,150,0.5)',
                    color='#1e293b',
                    rangemode='tozero'
                ),
                yaxis=dict(
                    title="Rapport molaire phase gaz (Y)",
                    gridcolor='rgba(255,255,255,0.1)',
                    zerolinecolor='rgba(150,150,150,0.5)',
                    color='#1e293b',
                    rangemode='tozero'
                ),
                plot_bgcolor='#1e293b',
                paper_bgcolor='#0f172a',
                font=dict(color='#e2e8f0'),
                hovermode='closest',
                legend=dict(
                    x=0.98,
                    y=0.02,
                    xanchor='right',
                    yanchor='bottom',
                    bgcolor='rgba(30,41,59,0.9)',
                    bordercolor='#475569',
                    borderwidth=1
                ),
                height=400,
                margin=dict(l=50, r=10, t=30, b=0)
            )
            
            plot_mccabe = fig_plotly.to_json()
            
            # --- 2. GRAPHIQUE EVOLUTION DES CONCENTRATIONS AVEC PLOTLY (STYLE BLANC) ---
            fig_concentration = go.Figure()
            
            # Liquide (X) - Vert
            fig_concentration.add_trace(go.Scatter(
                x=stages_list,
                y=X_prof,
                mode='lines+markers',
                name='Liquide (X)',
                line=dict(color='#10b981', width=3),
                marker=dict(size=8, color='#10b981', symbol='circle')
            ))
            
            # Gaz (Y) - Bleu
            fig_concentration.add_trace(go.Scatter(
                x=stages_list,
                y=Y_prof,
                mode='lines+markers',
                name='Gaz (Y)',
                line=dict(color='#3b82f6', width=3),
                marker=dict(size=8, color='#3b82f6', symbol='square')
            ))
            
            fig_concentration.update_layout(
                title=dict(
                    text="Profil de concentration",
                    font=dict(size=16, color='#1e293b')
                ),
                xaxis=dict(
                    title="Numéro d'étage (0 = Entrée liquide)",
                    titlefont=dict(size=14, color='#e2e8f0'),
                    tickfont=dict(size=12, color='#cbd5e1'),
                    gridcolor='rgba(255,255,255,0.1)',
                    showgrid=True,
                    zeroline=False
                ),
                yaxis=dict(
                    title="Rapport molaire",
                    titlefont=dict(size=14, color='#e2e8f0'),
                    tickfont=dict(size=12, color='#cbd5e1'),
                    gridcolor='rgba(255,255,255,0.1)',
                    showgrid=True,
                    zeroline=False
                ),
                plot_bgcolor='#1e293b',
                paper_bgcolor='#0f172a',
                font=dict(color='#e2e8f0'),
                hovermode='x unified',
                legend=dict(
                    x=0.02,
                    y=0.98,
                    bgcolor='rgba(30,41,59,0.9)',
                    bordercolor='#475569',
                    borderwidth=2,
                    font=dict(size=12, color='#e2e8f0')
                ),
                height=540,
                margin=dict(l=0, r=0, t=15, b=25)
            )
            
            plot_evol = fig_concentration.to_json()
            
            # --- 3. SCHÉMA DE LA COLONNE AVEC PLOTLY (STYLE BLANC) ---
            fig_schema = go.Figure()
            
            # Corps de la colonne (rectangle)
            fig_schema.add_shape(
                type="rect",
                x0=0.35, y0=0.15, x1=0.65, y1=0.85,
                line=dict(color='#3b82f6', width=6),
                fillcolor='rgba(224,242,254,0.3)'
            )
            
            # Lignes d'étages
            num_drawn = min(stage_count, 8) if stage_count > 0 else 3
            for i in range(1, num_drawn):
                y_pos = 0.15 + i * (0.7 / num_drawn)
                fig_schema.add_shape(
                    type="line",
                    x0=0.35, y0=y_pos, x1=0.65, y1=y_pos,
                    line=dict(color='#0284c7', width=3, dash='dash')
                )
            
            # Boîte nombre d'étages
            fig_schema.add_annotation(
                x=0.5, y=0.5,
                text=f"N = {stage_count}<br>Étages",
                showarrow=False,
                font=dict(size=20, color='#1f2937', family='Arial Black'),
                bgcolor='#fbbf24',
                bordercolor='#d97706',
                borderwidth=4,
                borderpad=8
            )
            
            # Flèches et annotations
            # Liquide Entrant (haut)
            fig_schema.add_annotation(
                x=0.5, y=0.93,
                text=f"Liquide Entrant<br>L = {L:.1f} mol/h<br>X<sub>in</sub> = {X_in:.4f}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='#10b981',
                ax=0, ay=-40,
                font=dict(size=14, color='#065f46'),
                bgcolor='#d1fae5',
                bordercolor='#10b981',
                borderwidth=3,
                borderpad=8
            )
            
            # Liquide Sortant (bas)
            fig_schema.add_annotation(
                x=0.5, y=0.07,
                text=f"Liquide Sortant<br>L = {L:.1f} mol/h<br>X<sub>out</sub> = {X_out:.4f}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='#10b981',
                ax=0, ay=40,
                font=dict(size=14, color='#065f46'),
                bgcolor='#d1fae5',
                bordercolor='#10b981',
                borderwidth=3,
                borderpad=8
            )
            
            # Gaz Entrant (gauche bas)
            fig_schema.add_annotation(
                x=0.15, y=0.3,
                text=f"Gaz Entrant<br>G = {G:.1f} mol/h<br>Y<sub>in</sub> = {Y_in:.4f}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='#3b82f6',
                ax=50, ay=0,
                font=dict(size=14, color='#1e3a8a'),
                bgcolor='#dbeafe',
                bordercolor='#3b82f6',
                borderwidth=3,
                borderpad=8
            )
            
            # Gaz Sortant (droite haut)
            fig_schema.add_annotation(
                x=0.85, y=0.7,
                text=f"Gaz Sortant<br>G = {G:.1f} mol/h<br>Y<sub>out</sub> = {Y_out:.4f}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='#3b82f6',
                ax=-50, ay=0,
                font=dict(size=14, color='#1e3a8a'),
                bgcolor='#dbeafe',
                bordercolor='#3b82f6',
                borderwidth=3,
                borderpad=8
            )
            
            fig_schema.update_layout(
                xaxis=dict(range=[0, 1], showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(range=[0, 1], showgrid=False, showticklabels=False, zeroline=False),
                plot_bgcolor='#1e293b',
                paper_bgcolor='#0f172a',
                height=540,
                showlegend=False,
                margin=dict(l=0, r=0, t=0, b=0)
            )
            
            plot_3d = fig_schema.to_json()
            
            return {
                'success': True,
                'mccabe_graph': plot_mccabe,
                'concentration_graph': plot_evol,
                '3d_graph': plot_3d,
                'stage_count': stage_count
            }
            
        except Exception as e:
            print(f"Error in generate_desorption_graphs: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }


# Instance globale du service
concentration_3d_service = Concentration3DService()
