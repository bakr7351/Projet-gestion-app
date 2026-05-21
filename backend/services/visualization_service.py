"""
Unified Visualization Service
Consolidates all graph generation functionality for McCabe-Thiele diagrams,
concentration profiles, and column schematics using Plotly.

This service replaces:
- mccabe_thiele_service.py
- plotly_mccabe_advanced.py  
- concentration_3d_service.py
"""

import numpy as np
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json


class VisualizationService:
    """Unified service for all visualization and graph generation needs"""
    
    def __init__(self):
        # Color schemes for different graph types
        self.colors = {
            'equilibrium': '#00ff00',  # Lime green
            'operating': '#ff00ff',    # Magenta
            'steps': '#00ffff',        # Cyan
            'background': '#1e1e1e',   # Dark black
            'grid': '#404040',         # Dark gray
            'text': '#ffffff'          # White
        }
        
        # Dark theme configuration for Plotly
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
    
    # ========================================================================
    # MCCABE-THIELE DIAGRAMS - Counter-current operations
    # ========================================================================
    
    def generate_absorption_graph(self, L_prime, G_prime, m, y_in, x_in, stages_data):
        """
        Generate McCabe-Thiele diagram for counter-current absorption
        
        Args:
            L_prime: Molar flow rate of solvent (mol/h)
            G_prime: Molar flow rate of gas (mol/h)
            m: Equilibrium constant
            y_in: Inlet gas mole fraction
            x_in: Inlet liquid mole fraction
            stages_data: Calculated stage data
            
        Returns:
            JSON string of Plotly figure
        """
        
        # Convert to molar ratios
        Y_in = y_in / (1 - y_in) if y_in < 1 else 0
        X_in = x_in / (1 - x_in) if x_in < 1 else 0
        
        # Range for curves
        X_max = max(0.2, Y_in / m * 1.2)
        X_eq = np.linspace(0, X_max, 300)
        Y_eq = m * X_eq
        
        # Create figure
        fig = go.Figure()
        
        # Equilibrium curve
        fig.add_trace(go.Scatter(
            x=X_eq,
            y=Y_eq,
            mode='lines',
            name='Courbe d\'équilibre (Y = mX)',
            line=dict(color=self.colors['equilibrium'], width=3),
            hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
        ))
        
        # Operating line
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
        
        # McCabe-Thiele steps
        if stages_data:
            self._add_mccabe_steps_absorption(fig, stages_data, m, L_prime, G_prime, X_in, Y_in)
        
        # Important points
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
        
        # Layout configuration
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
        Generate McCabe-Thiele diagram for counter-current desorption
        
        Args:
            L: Liquid molar flow rate (mol/h)
            G: Gas molar flow rate (mol/h)
            m: Equilibrium constant
            x_in: Inlet liquid mole fraction
            y_in: Inlet gas mole fraction
            stages_data: Calculated stage data
            
        Returns:
            JSON string of Plotly figure
        """
        
        # Convert fractions to molar ratios
        X_in = x_in / (1 - x_in) if 0 < x_in < 1 else x_in
        Y_in = y_in / (1 - y_in) if 0 < y_in < 1 else 0.0

        # Get X_out and Y_out from stages_data if available
        if stages_data:
            X_out = stages_data[-1]['X_sortie']
            Y_out = Y_in + (L / G) * (X_in - X_out)
        else:
            X_out = 0.0
            Y_out = Y_in

        X_max = max(0.2, X_in * 1.3)

        fig = go.Figure()

        # Equilibrium curve
        X_eq_line = np.linspace(0, X_max, 300)
        Y_eq_line = m * X_eq_line
        fig.add_trace(go.Scatter(
            x=X_eq_line, y=Y_eq_line,
            mode='lines',
            name="Courbe d'équilibre (Y = mX)",
            line=dict(color=self.colors['equilibrium'], width=3),
            hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
        ))

        # Operating line
        X_op_line = np.linspace(0, X_max, 300)
        Y_op_line = Y_in + (L / G) * (X_op_line - X_out)
        fig.add_trace(go.Scatter(
            x=X_op_line, y=Y_op_line,
            mode='lines',
            name=f'Droite opératoire (pente = {L/G:.3f})',
            line=dict(color=self.colors['operating'], width=3),
            hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
        ))

        # McCabe-Thiele steps
        if stages_data:
            self._add_mccabe_steps_desorption_corrected(
                fig, stages_data, m, L, G, X_in, Y_in, X_out, Y_out
            )

        # Important points
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

        # Layout
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
    
    # ========================================================================
    # CROSS-CURRENT OPERATIONS - Advanced Plotly diagrams
    # ========================================================================
    
    def generate_absorption_cross_current(self, G, L, m, y0, x0, stages):
        """
        Generate McCabe-Thiele diagram for cross-current absorption
        
        Args:
            G: Gas molar flow rate (mol/h)
            L: Solvent molar flow rate (mol/h)
            m: Equilibrium constant
            y0: Inlet gas mole fraction
            x0: Inlet liquid mole fraction
            stages: Number of stages
            
        Returns:
            Dictionary with graph JSON and results
        """
        
        # Convert to molar ratios
        Y0 = y0 / (1 - y0)
        A = L / (m * G)
        
        Ystart = Y0
        
        # Equilibrium curve
        Xeq = np.linspace(0, 0.2, 100)
        Yeq = m * Xeq
        
        fig = go.Figure()
        
        # Equilibrium curve
        fig.add_trace(go.Scatter(
            x=Xeq, 
            y=Yeq,
            mode='lines',
            name='Courbe d\'équilibre (Y = mX)',
            line=dict(color='lime', width=3)
        ))
        
        # Calculate stages
        results = []
        for i in range(stages):
            # Intersection with equilibrium curve
            Xint = Ystart / (m + L / G)
            Yint = m * Xint
            
            # Operating line for this stage
            Xop = np.linspace(0, Xint, 100)
            Yop = -(L / G) * Xop + Ystart
            
            fig.add_trace(go.Scatter(
                x=Xop, 
                y=Yop,
                mode='lines',
                name=f'Droite opératoire étage {i+1}',
                line=dict(color='magenta', width=2)
            ))
            
            # Intersection point
            fig.add_trace(go.Scatter(
                x=[Xint], 
                y=[Yint],
                mode='markers',
                name=f'Point étage {i+1}',
                marker=dict(color='cyan', size=10)
            ))
            
            # Store results
            results.append({
                'stage': i + 1,
                'X_int': Xint,
                'Y_int': Yint,
                'Y_start': Ystart
            })
            
            Ystart = Yint
        
        # Calculate absorption rate
        taux = (Y0 - Yint) / Y0 * 100 if Y0 > 0 else 0
        
        # Layout configuration
        fig.update_layout(
            title="Diagramme McCabe-Thiele - Absorption a courant croise",
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
        Generate McCabe-Thiele diagram for absorption with unknown number of stages
        Automatically calculates required number of stages
        
        Args:
            G: Gas molar flow rate (mol/h)
            L: Solvent molar flow rate (mol/h)
            m: Equilibrium constant
            y0: Inlet gas mole fraction
            x0: Inlet liquid mole fraction
            y_objectif: Target outlet mole fraction
            
        Returns:
            Dictionary with graph JSON and results
        """
        
        # Convert to molar ratios
        Y0 = y0 / (1 - y0)
        X0 = x0 / (1 - x0) if x0 > 0 else 0
        Y_objectif = y_objectif / (1 - y_objectif)
        
        A = L / (m * G)
        Ystart = Y0
        
        # Equilibrium curve
        Xeq = np.linspace(0, 0.2, 100)
        Yeq = m * Xeq
        
        fig = go.Figure()
        
        # Equilibrium curve
        fig.add_trace(go.Scatter(
            x=Xeq, 
            y=Yeq, 
            mode='lines', 
            name='Courbe d\'équilibre (Y = mX)',
            line=dict(color='lime', width=3)
        ))
        
        # Iterative calculation until target is reached
        i = 0
        results = []
        
        while Ystart > Y_objectif and i < 50:  # Safety limit
            # Intersection with equilibrium curve
            Xint = Ystart / (m + L / G)
            Yint = m * Xint
            
            # Operating line
            Xop = np.linspace(0, Xint, 100)
            Yop = (L / G) * Xop + Ystart
            
            fig.add_trace(go.Scatter(
                x=Xop, 
                y=Yop, 
                mode='lines', 
                name=f'Droite opératoire étage {i+1}',
                line=dict(color='magenta', width=2)
            ))
            
            # Intersection point
            fig.add_trace(go.Scatter(
                x=[Xint], 
                y=[Yint], 
                mode='markers', 
                name=f'Point étage {i+1}',
                marker=dict(color='cyan', size=10)
            ))
            
            # Store results
            results.append({
                'stage': i + 1,
                'X_int': Xint,
                'Y_int': Yint,
                'Y_start': Ystart
            })
            
            Ystart = Yint
            i += 1
        
        # Calculate absorption rate
        taux = (Y0 - Yint) / Y0 * 100 if Y0 > 0 else 0
        
        # Layout configuration
        fig.update_layout(
            title=f"Absorption a courant croise - {i} etages necessaires (Taux: {taux:.1f}%)",
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
        Generate McCabe-Thiele diagram for cross-current desorption
        
        Args:
            G: Gas molar flow rate (mol/h)
            L: Liquid molar flow rate (mol/h)
            m: Equilibrium constant
            y0: Inlet gas mole fraction
            x0: Inlet liquid mole fraction
            stages: Number of stages
            
        Returns:
            Dictionary with graph JSON and results
        """
        
        # Convert to molar ratios
        Y0 = y0 / (1 - y0) if y0 > 0 else 0
        X0 = x0 / (1 - x0)
        
        A = L / (m * G)
        S = m * G / L
        
        # Calculate x values for each stage
        x_values = []
        x_temp = x0
        for i in range(stages):
            xi = x_temp / (1 + S)
            x_values.append(xi)
            x_temp = xi
        
        Ystart = Y0
        
        # Equilibrium curve
        Xeq = np.linspace(0, 0.2, 100)
        Yeq = m * Xeq
        
        fig = go.Figure()
        
        # Equilibrium curve
        fig.add_trace(go.Scatter(
            x=Xeq, 
            y=Yeq,
            mode='lines',
            name='Courbe d\'équilibre (Y = mX)',
            line=dict(color='lime', width=3)
        ))
        
        # Calculate desorption stages
        results = []
        for i in range(stages):
            # Intersection with equilibrium curve
            Xint = Ystart / (m + L / G)
            Yint = m * Xint
            
            # Operating line for desorption (corrected logic)
            Yop = np.linspace(0, Yint, 100)
            Xop = (Ystart - Yop) * (G / L)
            
            fig.add_trace(go.Scatter(
                x=Xop, 
                y=Yop,
                mode='lines',
                name=f'Droite opératoire étage {i+1}',
                line=dict(color='magenta', width=2)
            ))
            
            # Intersection point
            fig.add_trace(go.Scatter(
                x=[Xint], 
                y=[Yint],
                mode='markers',
                name=f'Point étage {i+1}',
                marker=dict(color='cyan', size=10)
            ))
            
            # Store results
            results.append({
                'stage': i + 1,
                'X_int': Xint,
                'Y_int': Yint,
                'Y_start': Ystart,
                'x_value': x_values[i] if i < len(x_values) else None
            })
            
            Ystart = Yint
        
        # Calculate desorption rate
        taux = (Y0 - Yint) / Y0 * 100 if Y0 > 0 else 0
        
        # Layout configuration
        fig.update_layout(
            title="Diagramme McCabe-Thiele - Desorption a courant croise",
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
    
    # ========================================================================
    # 3D SURFACE PLOTS - Parameter sensitivity analysis
    # ========================================================================
    
    def generate_3d_surface_plot(self, calculation_type, results):
        """
        Generate 3D surface plot to visualize parameter variations
        
        Args:
            calculation_type: 'absorption' or 'desorption'
            results: Calculation results
            
        Returns:
            JSON string of Plotly figure
        """
        
        if calculation_type == 'absorption':
            return self._generate_3d_absorption_surface(results)
        else:
            return self._generate_3d_desorption_surface(results)
    
    def _generate_3d_absorption_surface(self, results):
        """Generate 3D surface for absorption"""
        
        # Create parameter grid
        m_range = np.linspace(0.1, 2.0, 20)
        L_G_ratio = np.linspace(0.5, 3.0, 20)
        
        M, LG = np.meshgrid(m_range, L_G_ratio)
        
        # Calculate theoretical stages for each combination
        stages_surface = np.zeros_like(M)
        
        base_y0 = results.get('y0', 0.08)
        base_y_obj = results.get('y_objectif', 0.008)
        
        for i in range(len(m_range)):
            for j in range(len(L_G_ratio)):
                # Simplified simulation for surface
                Y0 = base_y0 / (1 - base_y0)
                Y_obj = base_y_obj / (1 - base_y_obj)
                
                m_val = M[j, i]
                lg_ratio = LG[j, i]
                
                # Stage estimation
                if m_val > 0 and lg_ratio > 0:
                    A = 1 / (m_val * lg_ratio)
                    if A > 1:
                        stages_surface[j, i] = np.log(Y_obj/Y0) / np.log(1/A)
                    else:
                        stages_surface[j, i] = 50  # Maximum
                else:
                    stages_surface[j, i] = 50
                
                # Limit values
                stages_surface[j, i] = min(max(stages_surface[j, i], 1), 50)
        
        # Create 3D figure
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
        """Generate 3D surface for desorption"""
        
        # Create parameter grid
        m_range = np.linspace(0.1, 2.0, 20)
        G_L_ratio = np.linspace(0.5, 3.0, 20)
        
        M, GL = np.meshgrid(m_range, G_L_ratio)
        
        # Calculate theoretical stages for each combination
        stages_surface = np.zeros_like(M)
        
        base_x0 = results.get('x0', 0.06)
        base_x_obj = results.get('x_obj', 0.006)
        
        for i in range(len(m_range)):
            for j in range(len(G_L_ratio)):
                # Simplified simulation for surface
                X0 = base_x0 / (1 - base_x0)
                X_obj = base_x_obj / (1 - base_x_obj)
                
                m_val = M[j, i]
                gl_ratio = GL[j, i]
                
                # Stage estimation
                if m_val > 0 and gl_ratio > 0:
                    S = m_val * gl_ratio
                    if S > 1:
                        stages_surface[j, i] = np.log(X_obj/X0) / np.log(1/S)
                    else:
                        stages_surface[j, i] = 50  # Maximum
                else:
                    stages_surface[j, i] = 50
                
                # Limit values
                stages_surface[j, i] = min(max(abs(stages_surface[j, i]), 1), 50)
        
        # Create 3D figure
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
    
    # ========================================================================
    # CONCENTRATION PROFILES AND COLUMN SCHEMATICS
    # ========================================================================
    
    def generate_absorption_graphs(self, G, L, m_cst, y_in, x_in, y_out, calc_results=None):
        """
        Generate concentration and column schematic graphs for absorption
        If calc_results is provided, uses pre-calculated stages (avoids divergence)
        
        Args:
            G: Gas molar flow rate (mol/h)
            L: Liquid molar flow rate (mol/h)
            m_cst: Equilibrium constant
            y_in: Inlet gas mole fraction
            x_in: Inlet liquid mole fraction
            y_out: Outlet gas mole fraction
            calc_results: Pre-calculated results (optional)
            
        Returns:
            Dictionary with success status and graph JSONs
        """
        try:
            # Convert to molar ratios
            Y_in = y_in / (1 - y_in) if y_in < 1 else 0
            X_in = x_in / (1 - x_in) if x_in != 1 and x_in > 0 else 0
            Y_out = y_out / (1 - y_out) if y_out < 1 else 0
            X_out = X_in + (G / L) * (Y_in - Y_out)

            X_eq_max = max(X_out, Y_in / m_cst) * 1.2

            # Use pre-calculated stages if available
            if calc_results and 'resultats' in calc_results:
                resultats = calc_results['resultats']
                stage_count = len(resultats)

                # Use pre-calculated x_steps/y_steps if available
                if 'x_steps' in calc_results and 'y_steps' in calc_results:
                    x_steps   = calc_results['x_steps']
                    y_steps   = calc_results['y_steps']
                    stages_list = calc_results.get('stages_list', list(range(stage_count + 1)))
                    X_prof    = calc_results.get('X_prof', [X_in])
                    Y_prof    = calc_results.get('Y_prof', [Y_out])
                else:
                    # Reconstruct from resultats
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
                # Fallback: local recalculation
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
            
            # 1. McCabe-Thiele graph with Plotly
            X_line = np.linspace(0, X_eq_max, 100)
            Y_eq_line = m_cst * X_line
            
            fig_plotly = go.Figure()
            
            # Equilibrium curve
            fig_plotly.add_trace(go.Scatter(
                x=X_line,
                y=Y_eq_line,
                mode='lines',
                name="Courbe d'équilibre (Y = mX)",
                line=dict(color='#ef4444', width=2.5),
                hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
            ))
            
            # Operating line
            fig_plotly.add_trace(go.Scatter(
                x=[X_in, X_out],
                y=[Y_out, Y_in],
                mode='lines+markers',
                name="Droite opératoire (Absorption)",
                line=dict(color='#00FFFF', width=3),
                marker=dict(size=10, color='#00FFFF'),
                hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
            ))
            
            # Stages
            fig_plotly.add_trace(go.Scatter(
                x=x_steps,
                y=y_steps,
                mode='lines',
                name=f"Nombre d'étages = {stage_count}",
                line=dict(color='#FF00FF', width=2),
                hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
            ))
            
            # Layout
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
            
            # 2. Concentration evolution graph
            fig_concentration = go.Figure()
            
            # Liquid (X) - Green
            fig_concentration.add_trace(go.Scatter(
                x=stages_list,
                y=X_prof,
                mode='lines+markers',
                name='Liquide (X)',
                line=dict(color='#10b981', width=3),
                marker=dict(size=8, color='#10b981', symbol='circle')
            ))
            
            # Gas (Y) - Blue
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
            
            # 3. Column schematic
            plot_3d = self._generate_column_schematic_absorption(G, L, X_in, X_out, Y_in, Y_out, stage_count)
            
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
        Generate concentration and column schematic graphs for desorption
        If calc_results is provided, uses pre-calculated stages
        
        Args:
            G: Gas molar flow rate (mol/h)
            L: Liquid molar flow rate (mol/h)
            m_cst: Equilibrium constant
            y_in: Inlet gas mole fraction
            x_in: Inlet liquid mole fraction
            x_out: Outlet liquid mole fraction
            calc_results: Pre-calculated results (optional)
            
        Returns:
            Dictionary with success status and graph JSONs
        """
        try:
            # Convert to molar ratios
            Y_in = y_in / (1 - y_in) if y_in < 1 and y_in > 0 else 0
            X_in = x_in / (1 - x_in) if x_in != 1 and x_in > 0 else 0
            X_out = x_out / (1 - x_out) if x_out != 1 and x_out > 0 else 0
            Y_out = Y_in + (L / G) * (X_in - X_out)

            X_eq_max = X_in * 1.3

            # Use pre-calculated stages if available
            if calc_results and 'resultats' in calc_results:
                resultats = calc_results['resultats']
                stage_count = len(resultats)

                # Use pre-calculated x_steps/y_steps if available
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
                # Fallback: local recalculation
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
            
            # 1. McCabe-Thiele graph with Plotly
            X_line = np.linspace(0, X_eq_max, 100)
            Y_eq_line = m_cst * X_line
            
            fig_plotly = go.Figure()
            
            # Equilibrium curve
            fig_plotly.add_trace(go.Scatter(
                x=X_line,
                y=Y_eq_line,
                mode='lines',
                name="Courbe d'équilibre (Y = mX)",
                line=dict(color='#ef4444', width=2.5),
                hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
            ))
            
            # Operating line
            fig_plotly.add_trace(go.Scatter(
                x=[X_out, X_in],
                y=[Y_in, Y_out],
                mode='lines+markers',
                name="Droite opératoire (Désorption)",
                line=dict(color='#FFD700', width=3),
                marker=dict(size=10, color='#FFD700'),
                hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
            ))
            
            # Stages
            fig_plotly.add_trace(go.Scatter(
                x=x_steps,
                y=y_steps,
                mode='lines',
                name=f"Nombre d'étages = {stage_count}",
                line=dict(color='#FF00FF', width=2),
                hovertemplate='X: %{x:.4f}<br>Y: %{y:.4f}<extra></extra>'
            ))
            
            # Layout
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
            
            # 2. Concentration evolution graph
            fig_concentration = go.Figure()
            
            # Liquid (X) - Green
            fig_concentration.add_trace(go.Scatter(
                x=stages_list,
                y=X_prof,
                mode='lines+markers',
                name='Liquide (X)',
                line=dict(color='#10b981', width=3),
                marker=dict(size=8, color='#10b981', symbol='circle')
            ))
            
            # Gas (Y) - Blue
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
            
            # 3. Column schematic
            plot_3d = self._generate_column_schematic_desorption(G, L, X_in, X_out, Y_in, Y_out, stage_count)
            
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
    
    # ========================================================================
    # HELPER METHODS - Internal step drawing and column schematics
    # ========================================================================
    
    def _add_mccabe_steps_absorption(self, fig, stages_data, m, L_prime, G_prime, X_in, Y_in):
        """Add McCabe-Thiele steps for absorption"""
        
        x_current = X_in
        y_current = Y_in
        
        for i, stage in enumerate(stages_data):
            # Horizontal line to equilibrium curve
            x_eq = y_current / m
            
            fig.add_trace(go.Scatter(
                x=[x_current, x_eq],
                y=[y_current, y_current],
                mode='lines',
                showlegend=False,
                line=dict(color=self.colors['steps'], width=2, dash='solid'),
                hovertemplate=f'Étage {i+1} - Horizontal<br>X: %{{x:.4f}}<br>Y: %{{y:.4f}}<extra></extra>'
            ))
            
            # Vertical line to operating line
            y_new = (L_prime/G_prime) * (x_eq - X_in) + Y_in
            
            fig.add_trace(go.Scatter(
                x=[x_eq, x_eq],
                y=[y_current, y_new],
                mode='lines',
                showlegend=False,
                line=dict(color=self.colors['steps'], width=2, dash='solid'),
                hovertemplate=f'Étage {i+1} - Vertical<br>X: %{{x:.4f}}<br>Y: %{{y:.4f}}<extra></extra>'
            ))
            
            # Stage numbering
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
    
    def _add_mccabe_steps_desorption_corrected(self, fig, stages_data, m, L, G, X_in, Y_in, X_out, Y_out):
        """
        Draw correct McCabe-Thiele staircase for desorption
        
        The staircase starts from (X_in, Y_out) at the top and descends:
          - Horizontal left → X_eq = Y_c / m  (equilibrium curve)
          - Vertical down   → Y_op = Y_in + (L/G)*(X_eq - X_out)  (operating line)
        """
        x_steps = [X_in]
        y_steps = [Y_out]

        Y_c = Y_out
        for i, stage in enumerate(stages_data):
            X_eq = stage['X_sortie']   # = Y_c / m
            Y_op = stage['Y_sortie']   # = Y_in + (L/G)*(X_eq - X_out)

            # Horizontal: (x_prev, Y_c) → (X_eq, Y_c)
            x_steps.append(X_eq)
            y_steps.append(Y_c)

            # Vertical: (X_eq, Y_c) → (X_eq, Y_op)
            x_steps.append(X_eq)
            y_steps.append(Y_op)

            # Stage number annotation
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
    
    def _generate_column_schematic_absorption(self, G, L, X_in, X_out, Y_in, Y_out, stage_count):
        """Generate column schematic for absorption"""
        
        fig_schema = go.Figure()
        
        # Column body (rectangle)
        fig_schema.add_shape(
            type="rect",
            x0=0.35, y0=0.15, x1=0.65, y1=0.85,
            line=dict(color='#3b82f6', width=6),
            fillcolor='rgba(224,242,254,0.3)'
        )
        
        # Stage lines
        num_drawn = min(stage_count, 8) if stage_count > 0 else 3
        for i in range(1, num_drawn):
            y_pos = 0.15 + i * (0.7 / num_drawn)
            fig_schema.add_shape(
                type="line",
                x0=0.35, y0=y_pos, x1=0.65, y1=y_pos,
                line=dict(color='#0284c7', width=3, dash='dash')
            )
        
        # Stage count box
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
        
        # Arrows and annotations
        # Liquid Inlet (top)
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
        
        # Liquid Outlet (bottom)
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
        
        # Gas Inlet (left bottom)
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
        
        # Gas Outlet (right top)
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
        
        # Title
        fig_schema.add_annotation(
            x=0.05, y=0.95,
            text="Colonne d'Absorption a contre-courant",
            showarrow=False,
            font=dict(size=18, color='#1e293b', family='Arial Black'),
            xanchor='left'
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
        
        return fig_schema.to_json()
    
    def _generate_column_schematic_desorption(self, G, L, X_in, X_out, Y_in, Y_out, stage_count):
        """Generate column schematic for desorption"""
        
        fig_schema = go.Figure()
        
        # Column body (rectangle)
        fig_schema.add_shape(
            type="rect",
            x0=0.35, y0=0.15, x1=0.65, y1=0.85,
            line=dict(color='#3b82f6', width=6),
            fillcolor='rgba(224,242,254,0.3)'
        )
        
        # Stage lines
        num_drawn = min(stage_count, 8) if stage_count > 0 else 3
        for i in range(1, num_drawn):
            y_pos = 0.15 + i * (0.7 / num_drawn)
            fig_schema.add_shape(
                type="line",
                x0=0.35, y0=y_pos, x1=0.65, y1=y_pos,
                line=dict(color='#0284c7', width=3, dash='dash')
            )
        
        # Stage count box
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
        
        # Arrows and annotations
        # Liquid Inlet (top)
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
        
        # Liquid Outlet (bottom)
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
        
        # Gas Inlet (left bottom)
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
        
        # Gas Outlet (right top)
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
        
        # Title
        fig_schema.add_annotation(
            x=0.05, y=0.95,
            text="Colonne de Desorption a contre-courant",
            showarrow=False,
            font=dict(size=18, color='#1e293b', family='Arial Black'),
            xanchor='left'
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
        
        return fig_schema.to_json()


# Global service instance
visualization_service = VisualizationService()
