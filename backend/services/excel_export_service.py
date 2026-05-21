"""
Excel Export Service
Generates .xlsx files with calculation results.
Uses xlsxwriter for write-only operations (lighter than openpyxl).
"""
import io
import logging
from datetime import datetime

try:
    import xlsxwriter
    XLSXWRITER_AVAILABLE = True
except ImportError:
    XLSXWRITER_AVAILABLE = False

logger = logging.getLogger(__name__)

# ── Style constants ────────────────────────────────────────────────────────────
_HEADER_FILL   = "#4F46E5"   # indigo-600
_SUBHEAD_FILL  = "#818CF8"   # indigo-400
_ALT_ROW_FILL  = "#EEF2FF"   # indigo-50
_TITLE_BG      = "#E0E7FF"   # indigo-100


def _make_formats(workbook):
    """Create and return a dict of reusable xlsxwriter formats."""
    return {
        "header": workbook.add_format({
            "bold": True,
            "font_color": "#FFFFFF",
            "bg_color": _HEADER_FILL,
            "align": "center",
            "valign": "vcenter",
            "text_wrap": True,
            "border": 1,
            "border_color": "#C7D2FE",
            "font_size": 11,
        }),
        "label": workbook.add_format({
            "bold": True,
            "font_color": "#3730A3",
            "align": "left",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#C7D2FE",
            "font_size": 10,
        }),
        "value": workbook.add_format({
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#C7D2FE",
            "font_size": 10,
        }),
        "value_alt": workbook.add_format({
            "align": "center",
            "valign": "vcenter",
            "border": 1,
            "border_color": "#C7D2FE",
            "bg_color": _ALT_ROW_FILL,
            "font_size": 10,
        }),
        "title": workbook.add_format({
            "bold": True,
            "font_color": "#1E1B4B",
            "bg_color": _TITLE_BG,
            "align": "center",
            "valign": "vcenter",
            "font_size": 14,
        }),
        "date": workbook.add_format({
            "italic": True,
            "font_color": "#6B7280",
            "align": "center",
            "font_size": 9,
        }),
        "title_desorption": workbook.add_format({
            "bold": True,
            "font_color": "#1E1B4B",
            "bg_color": "#FCE7F3",
            "align": "center",
            "valign": "vcenter",
            "font_size": 14,
        }),
    }


# ── Absorption Excel ───────────────────────────────────────────────────────────

def generate_absorption_excel(results: dict, graphs_b64: dict | None = None) -> bytes:
    """
    Generate an Excel workbook for absorption results.

    Args:
        results: calculation_results dict from the absorption calculator.
        graphs_b64: optional dict (ignoré - diagrammes non inclus dans Excel)

    Returns:
        Raw bytes of the .xlsx file.
    """
    if not XLSXWRITER_AVAILABLE:
        raise RuntimeError("xlsxwriter is not installed")

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    fmt = _make_formats(workbook)

    _add_summary_sheet_absorption(workbook, fmt, results)
    _add_stages_sheet_absorption(workbook, fmt, results)
    
    # Note: Les diagrammes McCabe-Thiele ne sont plus inclus dans l'export Excel
    # pour des raisons de performance et de compatibilité

    workbook.close()
    output.seek(0)
    return output.read()


def _add_summary_sheet_absorption(workbook, fmt, results):
    ws = workbook.add_worksheet("Résumé")
    ws.hide_gridlines(2)

    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Title row (row 0, cols A:D merged)
    ws.merge_range("A1:D1", "Rapport d'Absorption — Contre-Courant", fmt["title"])
    ws.set_row(0, 30)

    # Date row
    ws.merge_range("A2:D2", f"Généré le {now}", fmt["date"])
    ws.set_row(1, 16)

    # Spacer
    ws.set_row(2, 8)

    # Section header: Input parameters (row 3, 0-indexed)
    ws.merge_range("A4:D4", "Paramètres d'entrée", fmt["header"])
    ws.set_row(3, 22)

    params = [
        ("Débit gaz G′ (mol/h)",       results.get("G_prime")),
        ("Débit solvant L′ (mol/h)",    results.get("L_prime")),
        ("Constante d'équilibre m",     results.get("m")),
        ("Fraction molaire entrée y₀",  results.get("y0")),
        ("Fraction molaire solvant x₀", results.get("x0", 0)),
        ("Fraction objectif y_obj",     results.get("y_objectif")),
        ("Facteur d'absorption A",      results.get("facteur_A")),
    ]
    for i, (label, value) in enumerate(params):
        row = 4 + i  # 0-indexed: rows 4..10
        alt = (row % 2 == 0)
        val_fmt = fmt["value_alt"] if alt else fmt["value"]
        ws.write(row, 0, label, fmt["label"])
        ws.merge_range(row, 1, row, 3, value, val_fmt)
        ws.set_row(row, 18)

    spacer_row = 4 + len(params)
    ws.set_row(spacer_row, 8)

    # Section header: Key results
    res_start = spacer_row + 1
    ws.merge_range(res_start, 0, res_start, 3, "Résultats clés", fmt["header"])
    ws.set_row(res_start, 22)

    key_results = [
        ("Nombre d'étages nécessaires", results.get("nb_etages")),
        ("Taux d'absorption (%)",        results.get("taux")),
        ("Quantité absorbée (mol/h)",    results.get("quantite")),
        ("Convergence",                  results.get("performance", {}).get("convergence", "—")),
        ("Temps d'exécution (ms)",       results.get("performance", {}).get("execution_time_ms")),
    ]
    for i, (label, value) in enumerate(key_results):
        row = res_start + 1 + i
        alt = (row % 2 == 0)
        val_fmt = fmt["value_alt"] if alt else fmt["value"]
        ws.write(row, 0, label, fmt["label"])
        ws.merge_range(row, 1, row, 3, value, val_fmt)
        ws.set_row(row, 18)

    ws.set_column(0, 0, 32)
    ws.set_column(1, 3, 14)


def _add_stages_sheet_absorption(workbook, fmt, results):
    ws = workbook.add_worksheet("Détails par étage")
    ws.hide_gridlines(2)

    headers = ["Étage", "Y entrée", "X sortie", "Y sortie", "y sortie (fraction)"]
    for col, h in enumerate(headers):
        ws.write(0, col, h, fmt["header"])
    ws.set_row(0, 22)

    for row_idx, r in enumerate(results.get("resultats", []), start=1):
        alt = (row_idx % 2 == 0)
        val_fmt = fmt["value_alt"] if alt else fmt["value"]
        ws.write(row_idx, 0, r.get("etage"), val_fmt)
        ws.write(row_idx, 1, r.get("Y_entree"), val_fmt)
        ws.write(row_idx, 2, r.get("X_sortie"), val_fmt)
        ws.write(row_idx, 3, r.get("Y_sortie"), val_fmt)
        ws.write(row_idx, 4, r.get("y_sortie"), val_fmt)
        ws.set_row(row_idx, 16)

    ws.freeze_panes(1, 0)
    ws.set_column(0, 4, 18)


# ── Desorption Excel ───────────────────────────────────────────────────────────

def generate_desorption_excel(results: dict, graphs_b64: dict | None = None) -> bytes:
    """
    Generate an Excel workbook for desorption results.

    Args:
        results: calculation_results dict from the desorption calculator.
        graphs_b64: optional dict (ignoré - diagrammes non inclus dans Excel)

    Returns:
        Raw bytes of the .xlsx file.
    """
    if not XLSXWRITER_AVAILABLE:
        raise RuntimeError("xlsxwriter is not installed")

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {"in_memory": True})
    fmt = _make_formats(workbook)

    _add_summary_sheet_desorption(workbook, fmt, results)
    _add_stages_sheet_desorption(workbook, fmt, results)
    
    # Note: Les diagrammes McCabe-Thiele ne sont plus inclus dans l'export Excel
    # pour des raisons de performance et de compatibilité

    workbook.close()
    output.seek(0)
    return output.read()


def _add_summary_sheet_desorption(workbook, fmt, results):
    ws = workbook.add_worksheet("Résumé")
    ws.hide_gridlines(2)

    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    ws.merge_range("A1:D1", "Rapport de Désorption — Contre-Courant", fmt["title_desorption"])
    ws.set_row(0, 30)

    ws.merge_range("A2:D2", f"Généré le {now}", fmt["date"])
    ws.set_row(1, 16)
    ws.set_row(2, 8)

    ws.merge_range("A4:D4", "Paramètres d'entrée", fmt["header"])
    ws.set_row(3, 22)

    params = [
        ("Débit gaz G (mol/h)",          results.get("G")),
        ("Débit liquide L (mol/h)",       results.get("L")),
        ("Constante d'équilibre m",       results.get("m")),
        ("Fraction molaire entrée x₀",    results.get("x0")),
        ("Fraction molaire gaz y₀",       results.get("y0", 0)),
        ("Fraction objectif x_obj",       results.get("x_obj")),
        ("Facteur de désorption S",       results.get("facteur_S")),
    ]
    for i, (label, value) in enumerate(params):
        row = 4 + i
        alt = (row % 2 == 0)
        val_fmt = fmt["value_alt"] if alt else fmt["value"]
        ws.write(row, 0, label, fmt["label"])
        ws.merge_range(row, 1, row, 3, value, val_fmt)
        ws.set_row(row, 18)

    spacer_row = 4 + len(params)
    ws.set_row(spacer_row, 8)
    res_start = spacer_row + 1

    ws.merge_range(res_start, 0, res_start, 3, "Résultats clés", fmt["header"])
    ws.set_row(res_start, 22)

    key_results = [
        ("Nombre d'étages nécessaires", results.get("nb_etages")),
        ("Taux de désorption (%)",       results.get("taux")),
        ("Quantité désorbée (mol/h)",    results.get("quantite")),
        ("Convergence",                  results.get("performance", {}).get("convergence", "—")),
        ("Temps d'exécution (ms)",       results.get("performance", {}).get("execution_time_ms")),
    ]
    for i, (label, value) in enumerate(key_results):
        row = res_start + 1 + i
        alt = (row % 2 == 0)
        val_fmt = fmt["value_alt"] if alt else fmt["value"]
        ws.write(row, 0, label, fmt["label"])
        ws.merge_range(row, 1, row, 3, value, val_fmt)
        ws.set_row(row, 18)

    ws.set_column(0, 0, 32)
    ws.set_column(1, 3, 14)


def _add_stages_sheet_desorption(workbook, fmt, results):
    ws = workbook.add_worksheet("Détails par étage")
    ws.hide_gridlines(2)

    headers = ["Étage", "X entrée", "Y entrée", "X sortie", "Y sortie", "x sortie (fraction)"]
    for col, h in enumerate(headers):
        ws.write(0, col, h, fmt["header"])
    ws.set_row(0, 22)

    for row_idx, r in enumerate(results.get("resultats", []), start=1):
        alt = (row_idx % 2 == 0)
        val_fmt = fmt["value_alt"] if alt else fmt["value"]
        ws.write(row_idx, 0, r.get("etage"), val_fmt)
        ws.write(row_idx, 1, r.get("X_entree"), val_fmt)
        ws.write(row_idx, 2, r.get("Y_entree"), val_fmt)
        ws.write(row_idx, 3, r.get("X_sortie"), val_fmt)
        ws.write(row_idx, 4, r.get("Y_sortie"), val_fmt)
        ws.write(row_idx, 5, r.get("x_sortie"), val_fmt)
        ws.set_row(row_idx, 16)

    ws.freeze_panes(1, 0)
    ws.set_column(0, 5, 18)
