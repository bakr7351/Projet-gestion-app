from __future__ import annotations

import logging

from flask import Blueprint, render_template, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from backend.services.cross_current_plot_service import (
    build_absorption_plots,
    build_desorption_plots,
)
from backend.services.cross_current_simulator_service import (
    CrossCurrentExercise1Params,
    CrossCurrentExercise3Params,
    run_cross_current,
)

logger = logging.getLogger(__name__)

cross_current_simulator_bp = Blueprint("cross_current_simulator_bp", __name__)


def _save_to_history(resultats: dict, exercice: str, params: dict) -> None:
    try:
        verify_jwt_in_request(optional=True)
        uid = get_jwt_identity()
        if uid is None:
            return

        from backend.services.history_service import history_service

        calc_type = "absorption" if resultats["type"] == "absorption" else "desorption"
        history_service.save_entry(
            user_id=int(uid),
            calc_type=calc_type,
            input_params={**params, "flow_type": "cross-current"},
            result_summary={
                "nb_etages": resultats["N_etages"],
                "taux": round(resultats["taux"] * 100, 2),
                "facteur_A": round(resultats.get("A", 0), 4)
                if resultats["type"] == "absorption"
                else None,
                "facteur_S": round(resultats.get("S", 0), 4)
                if resultats["type"] == "desorption"
                else None,
            },
        )
    except Exception:
        logger.debug("Historique courant croisé non enregistré", exc_info=True)


@cross_current_simulator_bp.route("/cross-current-simulator", methods=["GET", "POST"])
def cross_current_simulator():
    """Simulateur d'exercices à courant croisé (Absorption / Désorption)."""

    resultats = None
    plot_url = None
    plot_evolution_url = None
    plot_schema_url = None
    exercice = "1"

    params_abs = {
        "G_prime": 150.0,
        "L_prime": 200.0,
        "m": 0.5,
        "y0": 0.06,
        "N_etages": 3,
    }
    params_des = {
        "L_prime": 100.0,
        "G_prime": 150.0,
        "m": 1.2,
        "x0": 0.05,
        "N_etages": 3,
    }

    if request.method == "POST":
        exercice = request.form.get("exercice", "1")

        if exercice == "1":
            try:
                typed = CrossCurrentExercise1Params.from_form(request.form)
            except ValueError:
                typed = CrossCurrentExercise1Params(**params_abs)

            params_abs = {
                "G_prime": typed.G_prime,
                "L_prime": typed.L_prime,
                "m": typed.m,
                "y0": typed.y0,
                "N_etages": typed.N_etages,
            }
            resultats = run_cross_current(typed)
            plot_url, plot_evolution_url, plot_schema_url = build_absorption_plots(resultats)
            _save_to_history(resultats, exercice, params_abs)

        else:
            try:
                typed = CrossCurrentExercise3Params.from_form(request.form)
            except ValueError:
                typed = CrossCurrentExercise3Params(**params_des)

            params_des = {
                "L_prime": typed.L_prime,
                "G_prime": typed.G_prime,
                "m": typed.m,
                "x0": typed.x0,
                "N_etages": typed.N_etages,
            }
            resultats = run_cross_current(typed)
            plot_url, plot_evolution_url, plot_schema_url = build_desorption_plots(resultats)
            _save_to_history(resultats, exercice, params_des)

    return render_template(
        "cross_current_simulator.html",
        resultats=resultats,
        plot_url=plot_url,
        plot_evolution_url=plot_evolution_url,
        plot_schema_url=plot_schema_url,
        exercice=exercice,
        params_abs=params_abs,
        params_des=params_des,
    )
