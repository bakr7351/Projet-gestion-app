"""
Routes pour le module de séchage psychrométrique
"""
import os
import time
from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.sechage_psychrometrique import (
    simuler_sechage,
    tracer_diagramme_psychrochart,
    resultats_pour_web,
    SechagePsychrometrique
)
from backend.services.history_service import history_service
from scipy.optimize import fsolve
import psychrolib

sechage_bp = Blueprint('sechage', __name__)

# Configuration
# Chemin absolu vers le dossier static/sechage
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "sechage")
PLOT_PATH = os.path.join(STATIC_DIR, "plot.png")

psychrolib.SetUnitSystem(psychrolib.SI)
P = psychrolib.GetStandardAtmPressure(0.0)


def _ensure_static():
    """Crée le dossier static si nécessaire"""
    os.makedirs(STATIC_DIR, exist_ok=True)


def _params_depuis_formulaire(form) -> dict:
    """Extrait les paramètres du formulaire"""
    type_h1 = form.get("humidite_init_type", "HR")
    val_h1 = float(form["humidite_init_val"])
    type_sortie = form.get("sortie_type", "HR")
    val_sortie = float(form["sortie_val"])
    adiabatique = form.get("adiabatique") == "on"
    
    T3_mesure = None
    if not adiabatique and form.get("T3_mesure"):
        T3_mesure = float(form["T3_mesure"])
    
    return {
        "T1": float(form["T1"]),
        "humidite_init": (type_h1, val_h1),
        "debit_m3_h": float(form["debit_m3_h"]),
        "T2": float(form["T2"]),
        "sortie": (type_sortie, val_sortie),
        "adiabatique": adiabatique,
        "T3_mesure": T3_mesure,
    }


@sechage_bp.route("/sechage", methods=["GET", "POST"])
def index_sechage():
    """Page principale du module séchage"""
    erreur = None
    resultats = None
    
    if request.method == "POST":
        try:
            params = _params_depuis_formulaire(request.form)
            points, bilans_dict = simuler_sechage(params)
            
            _ensure_static()
            tracer_diagramme_psychrochart(
                points,
                fichier_sortie=PLOT_PATH,
                afficher=False,
            )
            
            resultats = resultats_pour_web(points, bilans_dict)
            current_app.config["LAST_SECHAGE"] = resultats
            
        except Exception as exc:
            erreur = str(exc)
            import traceback
            traceback.print_exc()
    
    return render_template(
        "sechage/index.html",
        resultats=resultats,
        erreur=erreur,
        plot_ts=int(time.time()) if resultats else None,
    )


@sechage_bp.route("/sechage/point", methods=["GET", "POST"])
def calculateur_point():
    """Calculateur de point psychrométrique (2 paramètres)"""
    results = None
    erreur = None
    
    if request.method == "POST":
        try:
            p1 = request.form["param1"]
            p2 = request.form["param2"]
            v1 = float(request.form["value1"])
            v2 = float(request.form["value2"])
            
            # Résolution des équations
            def equations(vars, p1, p2, v1, v2):
                T, w = vars
                
                def calc(param, val):
                    if param == "T":
                        return T - val
                    if param == "RH":
                        return psychrolib.GetRelHumFromHumRatio(T, w, P) - val / 100
                    if param == "W":
                        return w - val / 1000
                    if param == "Twb":
                        return psychrolib.GetTWetBulbFromHumRatio(T, w, P) - val
                    if param == "Tdp":
                        return psychrolib.GetTDewPointFromHumRatio(T, w, P) - val
                    if param == "h":
                        return psychrolib.GetMoistAirEnthalpy(T, w) / 1000 - val
                    if param == "v":
                        return psychrolib.GetMoistAirVolume(T, w, P) - val
                    return 0.0
                
                return [calc(p1, v1), calc(p2, v2)]
            
            T, w = fsolve(equations, (25, 0.01), args=(p1, p2, v1, v2))
            
            # Calcul de toutes les propriétés
            RH = psychrolib.GetRelHumFromHumRatio(T, w, P)
            h = psychrolib.GetMoistAirEnthalpy(T, w)
            Twb = psychrolib.GetTWetBulbFromHumRatio(T, w, P)
            Tdp = psychrolib.GetTDewPointFromHumRatio(T, w, P)
            v = psychrolib.GetMoistAirVolume(T, w, P)
            
            results = {
                "T": round(T, 2),
                "RH": round(RH * 100, 2),
                "w": round(w * 1000, 2),
                "h": round(h / 1000, 2),
                "Twb": round(Twb, 2),
                "Tdp": round(Tdp, 2),
                "v": round(v, 3),
            }
            
            # Tracer le diagramme
            import matplotlib.pyplot as plt
            import numpy as np
            
            T_range = np.linspace(0, 50, 100)
            RH_lines = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            
            plt.figure(figsize=(10, 6))
            
            for rh in RH_lines:
                w_curve = [
                    psychrolib.GetHumRatioFromRelHum(t, rh, P) * 1000 
                    for t in T_range
                ]
                plt.plot(T_range, w_curve, color="gray", alpha=0.5)
            
            w_sat = [
                psychrolib.GetHumRatioFromRelHum(t, 1.0, P) * 1000 
                for t in T_range
            ]
            plt.plot(T_range, w_sat, color="blue", linewidth=2, label="Saturation")
            
            plt.scatter(T, w * 1000, color="red", s=150, zorder=5, label="Point calculé")
            plt.xlabel("Température (°C)")
            plt.ylabel("Humidité absolue (g/kg)")
            plt.title("Diagramme psychrométrique")
            plt.legend()
            plt.grid(alpha=0.3)
            
            _ensure_static()
            plot_point_path = os.path.join(STATIC_DIR, "plot_point.png")
            plt.savefig(plot_point_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            current_app.config["LAST_POINT"] = results
            
        except Exception as exc:
            erreur = str(exc)
            import traceback
            traceback.print_exc()
    
    return render_template(
        "sechage/point.html", 
        results=results, 
        erreur=erreur,
        plot_ts=int(time.time()) if results else None,
    )


@sechage_bp.route("/sechage/api/save", methods=["POST"])
@jwt_required()
def save_sechage_calculation():
    """API pour enregistrer un calcul de séchage dans l'historique"""
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Paramètres d'entrée
        input_params = {
            "T1": data["T1"],
            "humidite_init_type": data.get("humidite_init_type", "HR"),
            "humidite_init_val": data["humidite_init_val"],
            "debit_m3_h": data["debit_m3_h"],
            "T2": data["T2"],
            "sortie_type": data.get("sortie_type", "HR"),
            "sortie_val": data["sortie_val"],
            "adiabatique": data.get("adiabatique", False),
            "T3_mesure": data.get("T3_mesure"),
        }
        
        # Résumé des résultats
        result_summary = {
            "points": data["points"],
            "bilans": data["bilans"]
        }
        
        custom_name = data.get("custom_name", f"Séchage - {data['T1']}°C → {data['T2']}°C")
        
        entry = history_service.save_entry(
            user_id=user_id,
            calc_type="sechage",
            input_params=input_params,
            result_summary=result_summary,
            custom_name=custom_name
        )
        
        return jsonify({
            "success": True,
            "message": "Calcul enregistré dans l'historique",
            "entry_id": entry.id
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@sechage_bp.route("/sechage/api/calcul", methods=["POST"])
def api_calcul_sechage():
    """API REST pour le calcul de séchage"""
    try:
        data = request.get_json()
        
        params = {
            "T1": data["T1"],
            "humidite_init": (data.get("humidite_init_type", "HR"), data["humidite_init_val"]),
            "debit_m3_h": data["debit_m3_h"],
            "T2": data["T2"],
            "sortie": (data.get("sortie_type", "HR"), data["sortie_val"]),
            "adiabatique": data.get("adiabatique", False),
            "T3_mesure": data.get("T3_mesure"),
        }
        
        points, bilans = simuler_sechage(params)
        
        return jsonify({
            "success": True,
            "points": points,
            "bilans": bilans
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@sechage_bp.route("/sechage/pdf")
def generer_pdf_sechage():
    """Génère un PDF des résultats de séchage"""
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        
        data = current_app.config.get("LAST_SECHAGE")
        
        if not data:
            return jsonify({"error": "Aucune donnée de séchage disponible"}), 400
        
        pdf_path = os.path.join(STATIC_DIR, "result_sechage.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Titre
        elements.append(Paragraph("Simulation de Séchage par Entraînement", styles['Title']))
        elements.append(Spacer(1, 0.5 * cm))
        
        # Tableau des points
        table_data = [
            ["Point", "T (°C)", "HR (%)", "w (g/kg)", "h (kJ/kg)", "v (m³/kg)"],
        ]
        
        for p in data["points"]:
            table_data.append([
                p["nom"],
                str(p["T"]),
                str(p["HR"]),
                str(p["w"]),
                str(p["h"]),
                str(p["v"]),
            ])
        
        t = Table(table_data)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.5 * cm))
        
        # Bilans
        elements.append(Paragraph("Bilans:", styles['Heading2']))
        elements.append(Spacer(1, 0.3 * cm))
        
        bilans_data = [
            ["Paramètre", "Valeur"],
            ["Eau évaporée", f"{data['bilans']['eau_evaporee_kg_h']} kg/h"],
            ["Puissance préchauffage", f"{data['bilans']['puissance_prechauffage_kW']} kW"],
            ["Puissance séchage", f"{data['bilans']['puissance_sechage_kW']} kW"],
            ["Débit massique air sec", f"{data['bilans']['debit_mass_as_kg_h']} kg/h"],
        ]
        
        t_bilans = Table(bilans_data)
        t_bilans.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]))
        elements.append(t_bilans)
        elements.append(Spacer(1, 0.5 * cm))
        
        # Diagramme
        if os.path.isfile(PLOT_PATH):
            elements.append(Paragraph("Diagramme Psychrométrique:", styles['Heading2']))
            elements.append(Spacer(1, 0.3 * cm))
            elements.append(Image(PLOT_PATH, width=15*cm, height=10*cm))
        
        doc.build(elements)
        
        return send_file(pdf_path, as_attachment=True, download_name="resultat_sechage.pdf")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
