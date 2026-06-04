"""
Module de calcul pour le séchage par entraînement (psychrométrie)
Opération unitaire : Séchage
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
try:
    import psychrolib
    psychrolib.SetUnitSystem(psychrolib.SI)
    PSYCHROLIB_AVAILABLE = True
except ImportError:
    PSYCHROLIB_AVAILABLE = False
    print("⚠️ psychrolib non disponible. Installez-le avec: pip install psychrolib")


class SechagePsychrometrique:
    """Classe pour les calculs de séchage par entraînement"""
    
    def __init__(self, altitude=0.0):
        """
        Initialise le calculateur de séchage
        
        Args:
            altitude: Altitude en mètres (défaut: 0 = niveau de la mer)
        """
        if not PSYCHROLIB_AVAILABLE:
            raise ImportError("psychrolib est requis pour ce module")
        
        self.P = psychrolib.GetStandardAtmPressure(altitude)
    
    def calculer_point(self, T, type_humidite, valeur_humidite):
        """
        Calcule toutes les propriétés d'un point psychrométrique
        
        Args:
            T: Température sèche (°C)
            type_humidite: 'HR' (%), 'W' (g/kg), 'Twb' (°C), 'Tdp' (°C), 'h' (kJ/kg)
            valeur_humidite: Valeur correspondant au type
            
        Returns:
            dict avec toutes les propriétés
        """
        # Calcul du rapport d'humidité w (kg eau / kg air sec)
        if type_humidite == "HR":
            w = psychrolib.GetHumRatioFromRelHum(T, valeur_humidite / 100.0, self.P)
        elif type_humidite == "W":
            w = valeur_humidite / 1000.0  # g/kg → kg/kg
        elif type_humidite == "Twb":
            w = psychrolib.GetHumRatioFromTWetBulb(T, valeur_humidite, self.P)
        elif type_humidite == "Tdp":
            w = psychrolib.GetHumRatioFromTDewPoint(valeur_humidite, self.P)
        elif type_humidite == "h":
            # Résolution itérative pour h
            w = self._w_depuis_enthalpie(T, valeur_humidite * 1000)
        else:
            raise ValueError(f"Type d'humidité inconnu: {type_humidite}")
        
        # Calcul de toutes les propriétés
        return {
            'T': round(T, 2),
            'w': round(w * 1000, 3),  # g/kg
            'HR': round(psychrolib.GetRelHumFromHumRatio(T, w, self.P) * 100, 2),
            'h': round(psychrolib.GetMoistAirEnthalpy(T, w) / 1000, 2),  # kJ/kg
            'Twb': round(psychrolib.GetTWetBulbFromHumRatio(T, w, self.P), 2),
            'Tdp': round(psychrolib.GetTDewPointFromHumRatio(T, w, self.P), 2),
            'v': round(psychrolib.GetMoistAirVolume(T, w, self.P), 3),  # m³/kg
        }
    
    def _w_depuis_enthalpie(self, T, h_target, tol=1e-6):
        """Calcule w depuis T et h par méthode itérative"""
        from scipy.optimize import fsolve
        def equation(w):
            return psychrolib.GetMoistAirEnthalpy(T, w) - h_target
        w_init = 0.01
        w_solution = fsolve(equation, w_init)[0]
        return w_solution
    
    def simuler_sechage(self, params):
        """
        Simule un processus de séchage complet
        
        Args:
            params: dict avec:
                - T1: Température air ambiant (°C)
                - humidite_init: (type, valeur)
                - debit_m3_h: Débit volumique (m³/h)
                - T2: Température après préchauffage (°C)
                - sortie: (type, valeur) conditions de sortie
                - adiabatique: bool
                - T3_mesure: Température mesurée en sortie (optionnel)
        
        Returns:
            (points, bilans) où:
                points: liste de dict avec les propriétés de chaque point
                bilans: dict avec les bilans massiques et énergétiques
        """
        # Point 1: Air ambiant
        type_h1, val_h1 = params['humidite_init']
        point1 = self.calculer_point(params['T1'], type_h1, val_h1)
        point1['nom'] = 'Point 1 (Ambiant)'
        point1['label'] = '1'
        
        # Calcul du débit massique d'air sec
        debit_mass_as = params['debit_m3_h'] / point1['v']  # kg_as/h
        
        # Point 2: Après préchauffage (w constant, T augmente)
        point2 = self.calculer_point(params['T2'], 'W', point1['w'])
        point2['nom'] = 'Point 2 (Préchauffage)'
        point2['label'] = '2'
        
        # Point 3: Sortie du séchoir
        type_sortie, val_sortie = params['sortie']
        if params.get('T3_mesure'):
            T3 = params['T3_mesure']
        else:
            # Estimer T3 selon le type de sortie
            if type_sortie == 'HR':
                # Pour adiabatique, utiliser Twb
                T3 = point2['Twb'] if params.get('adiabatique') else point2['T'] - 10
            else:
                T3 = point2['T'] - 10
        
        point3 = self.calculer_point(T3, type_sortie, val_sortie)
        point3['nom'] = 'Point 3 (Sortie)'
        point3['label'] = '3'
        
        # Bilans
        eau_evaporee_kg_h = debit_mass_as * (point3['w'] - point2['w']) / 1000  # kg/h
        puissance_prechauffage_kW = debit_mass_as * (point2['h'] - point1['h']) / 3600  # kW
        
        if params.get('adiabatique'):
            puissance_sechage_kW = 0.0
        else:
            puissance_sechage_kW = debit_mass_as * (point3['h'] - point2['h']) / 3600  # kW
        
        bilans = {
            'debit_mass_as_kg_h': round(debit_mass_as, 2),
            'eau_evaporee_kg_h': round(eau_evaporee_kg_h, 3),
            'puissance_prechauffage_kW': round(puissance_prechauffage_kW, 2),
            'puissance_sechage_kW': round(puissance_sechage_kW, 2),
        }
        
        return [point1, point2, point3], bilans
    
    def tracer_diagramme(self, points, fichier_sortie=None, afficher=True):
        """
        Trace le diagramme psychrométrique avec les points du procédé
        
        Args:
            points: liste de points (résultat de simuler_sechage)
            fichier_sortie: chemin du fichier de sortie (optionnel)
            afficher: afficher le diagramme (True) ou sauvegarder (False)
        """
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plage de températures
        T_range = np.linspace(-10, 60, 200)
        
        # Courbes d'humidité relative
        HR_lines = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        for hr in HR_lines:
            w_curve = []
            for t in T_range:
                try:
                    w = psychrolib.GetHumRatioFromRelHum(t, hr, self.P) * 1000
                    if w > 0 and w < 40:  # Limiter l'axe Y
                        w_curve.append(w)
                    else:
                        w_curve.append(np.nan)
                except:
                    w_curve.append(np.nan)
            
            label = f'{int(hr*100)}%' if hr in [0.2, 0.4, 0.6, 0.8, 1.0] else None
            ax.plot(T_range, w_curve, 'gray', linewidth=0.8, alpha=0.6, label=label)
        
        # Courbe de saturation (HR=100%)
        w_sat = []
        for t in T_range:
            try:
                w = psychrolib.GetHumRatioFromRelHum(t, 1.0, self.P) * 1000
                if w > 0 and w < 40:
                    w_sat.append(w)
                else:
                    w_sat.append(np.nan)
            except:
                w_sat.append(np.nan)
        ax.plot(T_range, w_sat, 'b-', linewidth=2, label='Saturation (100%)')
        
        # Tracer les points du procédé
        colors = ['green', 'orange', 'red']
        for i, point in enumerate(points):
            color = colors[i] if i < len(colors) else 'purple'
            ax.scatter(point['T'], point['w'], s=150, c=color, edgecolors='black', linewidth=2, zorder=5)
            ax.annotate(point['label'], (point['T'], point['w']), 
                       xytext=(10, 10), textcoords='offset points',
                       fontsize=12, fontweight='bold', color=color)
        
        # Tracer les transformations
        if len(points) >= 2:
            # 1→2: Préchauffage (ligne horizontale w constant)
            ax.plot([points[0]['T'], points[1]['T']], [points[0]['w'], points[1]['w']], 
                   'b--', linewidth=2, label='Préchauffage')
        
        if len(points) >= 3:
            # 2→3: Séchage
            ax.plot([points[1]['T'], points[2]['T']], [points[1]['w'], points[2]['w']], 
                   'r--', linewidth=2, label='Séchage')
        
        ax.set_xlabel('Température sèche (°C)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Humidité absolue (g/kg air sec)', fontsize=12, fontweight='bold')
        ax.set_title('Diagramme Psychrométrique - Séchage par Entraînement', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left', fontsize=10)
        ax.set_xlim(-10, 60)
        ax.set_ylim(0, 30)
        
        plt.tight_layout()
        
        if fichier_sortie:
            plt.savefig(fichier_sortie, dpi=150, bbox_inches='tight')
        
        if afficher:
            plt.show()
        else:
            plt.close()


def resultats_pour_web(points, bilans):
    """Formatte les résultats pour l'affichage web"""
    return {
        'points': points,
        'bilans': bilans
    }


def tracer_diagramme_psychrochart(points, fichier_sortie, afficher=False):
    """Wrapper pour compatibilité avec le code existant"""
    calc = SechagePsychrometrique()
    calc.tracer_diagramme(points, fichier_sortie, afficher)


def simuler_sechage(params):
    """Wrapper pour compatibilité avec le code existant"""
    calc = SechagePsychrometrique()
    return calc.simuler_sechage(params)
