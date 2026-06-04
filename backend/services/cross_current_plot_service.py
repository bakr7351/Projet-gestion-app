from __future__ import annotations

import base64
import io
from typing import Any, Tuple


def _fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(
        buf,
        format="png",
        dpi=120,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    # Close the matplotlib figure to avoid memory growth
    import matplotlib.pyplot as plt

    plt.close(fig)

    return "data:image/png;base64," + img_b64


def build_absorption_plots(resultats: dict[str, Any]) -> Tuple[str | None, str | None, str | None]:
    """Retourne (plot_url, plot_evolution_url, plot_schema_url) sous forme data-uri base64."""

    import numpy as np

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    Y_vals = resultats["Y_vals"]
    X_vals = resultats["X_vals"]
    m = resultats["m"]
    pente = resultats["pente"]

    def generer_graphique_absorption() -> str:
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#f8fafc")

        X_max = max(X_vals) * 1.2 if max(X_vals) > 0 else 0.01
        X_eq = np.linspace(0, X_max, 100)
        Y_eq = m * X_eq
        ax.plot(X_eq, Y_eq, "b-", linewidth=2, label=f"Equilibre: Y = {m}*X")

        for i in range(len(Y_vals) - 1):
            Y_start = Y_vals[i]
            X_end = X_vals[i + 1]
            Y_end = Y_vals[i + 1]

            X_line = np.linspace(0, X_end, 50)
            Y_line = Y_start + pente * X_line

            ax.plot(X_line, Y_line, "r--", linewidth=2, label="Droite operatoire" if i == 0 else "_nolegend_")
            ax.plot(X_end, Y_end, "ro", markersize=10, label=f"Etage {i+1}")

        for i in range(1, len(Y_vals)):
            ax.plot([0, X_vals[i]], [Y_vals[i], Y_vals[i]], color="gray", linewidth=1, linestyle=":", alpha=0.6)

        ax.set_xlabel("X (rapport molaire liquide)", fontsize=12)
        ax.set_ylabel("Y (rapport molaire gaz)", fontsize=12)
        ax.set_title("Absorption à courant croisé - McCabe-Thiele", fontsize=13, fontweight="bold")
        ax.legend(loc="upper left", fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return _fig_to_base64(fig)

    def generer_graphique_evolution_absorption() -> str:
        fig, ax = plt.subplots(figsize=(9, 5))
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#f8fafc")

        etages = list(range(len(Y_vals)))
        ax.plot(etages, Y_vals, "g-o", linewidth=3, markersize=8, label="Gaz (Y)")
        ax.plot(etages, X_vals, "b-o", linewidth=3, markersize=8, label="Liquide (X)")

        ax.set_xlabel("Numero d'etage (0 = Entree liquide)", fontsize=12)
        ax.set_ylabel("Rapport molaire", fontsize=12)
        ax.set_title("Absorption - Évolution des concentrations", fontsize=13, fontweight="bold")
        ax.legend(loc="upper right", fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return _fig_to_base64(fig)

    def generer_schema_colonne_absorption() -> str:
        fig, ax = plt.subplots(figsize=(8, 7))
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#f8fafc")

        col = mpatches.FancyBboxPatch(
            (2, 1),
            2,
            4,
            boxstyle="round,pad=0.1",
            linewidth=3,
            edgecolor="#4f46e5",
            facecolor="#dbeafe",
        )
        ax.add_patch(col)

        n = resultats["N_etages"]
        ax.text(
            3,
            3,
            f"N = {n}\nEtages",
            ha="center",
            va="center",
            fontsize=16,
            fontweight="bold",
            color="#FF9500",
            bbox=dict(
                boxstyle="round,pad=0.5",
                facecolor="#FFD700",
                edgecolor="#FF9500",
                linewidth=2,
            ),
        )

        ax.annotate(
            f"Gaz Entrant\nG'={resultats['G_prime']:.1f} mol/h\nYin={resultats['Y_vals'][0]:.4f}",
            xy=(2, 4.5),
            xytext=(0.2, 4.5),
            fontsize=9,
            arrowprops=dict(arrowstyle="->", color="green", lw=2),
            bbox=dict(boxstyle="round", facecolor="white", edgecolor="green"),
            ha="center",
        )

        ax.annotate(
            f"Gaz Sortant\nG'={resultats['G_prime']:.1f} mol/h\nYout={resultats['Y_vals'][-1]:.4f}",
            xy=(4, 4.5),
            xytext=(5.8, 4.5),
            fontsize=9,
            arrowprops=dict(arrowstyle="<-", color="green", lw=2),
            bbox=dict(boxstyle="round", facecolor="white", edgecolor="green"),
            ha="center",
        )

        ax.annotate(
            f"Liquide Entrant\nL'={resultats['L_prime']:.1f} mol/h\nXin=0.0000",
            xy=(3, 5),
            xytext=(3, 6.3),
            fontsize=9,
            arrowprops=dict(arrowstyle="->", color="#4f46e5", lw=2),
            bbox=dict(boxstyle="round", facecolor="white", edgecolor="#4f46e5"),
            ha="center",
        )

        ax.annotate(
            f"Liquide Sortant\nL'={resultats['L_prime']:.1f} mol/h\nXout={resultats['X_vals'][-1]:.4f}",
            xy=(3, 1),
            xytext=(3, -0.3),
            fontsize=9,
            arrowprops=dict(arrowstyle="<-", color="#4f46e5", lw=2),
            bbox=dict(boxstyle="round", facecolor="white", edgecolor="#4f46e5"),
            ha="center",
        )

        ax.set_xlim(-1, 7)
        ax.set_ylim(-1, 7.5)
        ax.axis("off")
        plt.tight_layout()
        return _fig_to_base64(fig)

    return (
        generer_graphique_absorption(),
        generer_graphique_evolution_absorption(),
        generer_schema_colonne_absorption(),
    )


def build_desorption_plots(resultats: dict[str, Any]) -> Tuple[str | None, str | None, str | None]:
    import numpy as np

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    X_vals = resultats["X_vals"]
    Y_vals = resultats["Y_vals"]
    m = resultats["m"]
    pente = resultats["pente"]

    def generer_graphique_desorption() -> str:
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#f8fafc")

        X_max = max(X_vals) * 1.5 if max(X_vals) > 0 else 0.01
        X_eq = np.linspace(0, X_max, 100)
        Y_eq = m * X_eq
        ax.plot(X_eq, Y_eq, "b-", linewidth=2, label=f"Equilibre: Y = {m}*X")

        for i in range(1, len(X_vals)):
            X_prev = X_vals[i - 1]
            X_i = X_vals[i]
            Y_i = Y_vals[i]

            X_line = np.linspace(X_i, X_prev, 50)
            Y_line = pente * (X_prev - X_line)

            ax.plot(
                X_line,
                Y_line,
                "r--",
                linewidth=2,
                label="Droite operatoire" if i == 1 else "_nolegend_",
            )
            ax.plot(X_i, Y_i, "ro", markersize=10, label=f"Etage {i}")
            ax.plot([X_i, X_i], [0, Y_i], color="gray", linewidth=1, linestyle=":", alpha=0.6)

        ax.set_xlabel("X (rapport molaire liquide)", fontsize=12)
        ax.set_ylabel("Y (rapport molaire gaz)", fontsize=12)
        ax.set_title("Désorption à courant croisé - McCabe-Thiele", fontsize=13, fontweight="bold")
        ax.legend(loc="upper right", fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return _fig_to_base64(fig)

    def generer_graphique_evolution_desorption() -> str:
        fig, ax = plt.subplots(figsize=(9, 5))
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#f8fafc")

        etages = list(range(len(X_vals)))
        ax.plot(etages, X_vals, "b-o", linewidth=3, markersize=8, label="Liquide (X)")
        ax.plot(etages, Y_vals, "g-o", linewidth=3, markersize=8, label="Gaz Sortant (Y)")

        ax.set_xlabel("Numero d'etage (0 = Entree liquide)", fontsize=12)
        ax.set_ylabel("Rapport molaire", fontsize=12)
        ax.set_title("Désorption - Évolution des concentrations", fontsize=13, fontweight="bold")
        ax.legend(loc="upper right", fontsize=10)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return _fig_to_base64(fig)

    def generer_schema_colonne_desorption() -> str:
        fig, ax = plt.subplots(figsize=(8, 7))
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#f8fafc")

        col = mpatches.FancyBboxPatch(
            (2, 1),
            2,
            4,
            boxstyle="round,pad=0.1",
            linewidth=3,
            edgecolor="#4f46e5",
            facecolor="#dbeafe",
        )
        ax.add_patch(col)

        n = resultats["N_etages"]
        ax.text(
            3,
            3,
            f"N = {n}\nEtages",
            ha="center",
            va="center",
            fontsize=16,
            fontweight="bold",
            color="#FF9500",
            bbox=dict(
                boxstyle="round,pad=0.5",
                facecolor="#FFD700",
                edgecolor="#FF9500",
                linewidth=2,
            ),
        )

        ax.annotate(
            f"Gaz Entrant\nG'={resultats['G_prime']:.1f} mol/h\nYin=0.0000 (pur)",
            xy=(2, 4.5),
            xytext=(0.2, 4.5),
            fontsize=9,
            arrowprops=dict(arrowstyle="->", color="green", lw=2),
            bbox=dict(boxstyle="round", facecolor="white", edgecolor="green"),
            ha="center",
        )

        ax.annotate(
            f"Gaz Sortant\nG'={resultats['G_prime']:.1f} mol/h\nYout={resultats['Y_vals'][-1]:.4f}",
            xy=(4, 4.5),
            xytext=(5.8, 4.5),
            fontsize=9,
            arrowprops=dict(arrowstyle="<-", color="green", lw=2),
            bbox=dict(boxstyle="round", facecolor="white", edgecolor="green"),
            ha="center",
        )

        ax.annotate(
            f"Liquide Entrant\nL'={resultats['L_prime']:.1f} mol/h\nXin={resultats['X_vals'][0]:.4f}",
            xy=(3, 5),
            xytext=(3, 6.3),
            fontsize=9,
            arrowprops=dict(arrowstyle="->", color="#4f46e5", lw=2),
            bbox=dict(boxstyle="round", facecolor="white", edgecolor="#4f46e5"),
            ha="center",
        )

        ax.annotate(
            f"Liquide Sortant\nL'={resultats['L_prime']:.1f} mol/h\nXout={resultats['X_vals'][-1]:.4f}",
            xy=(3, 1),
            xytext=(3, -0.3),
            fontsize=9,
            arrowprops=dict(arrowstyle="<-", color="#4f46e5", lw=2),
            bbox=dict(boxstyle="round", facecolor="white", edgecolor="#4f46e5"),
            ha="center",
        )

        ax.set_xlim(-1, 7)
        ax.set_ylim(-1, 7.5)
        ax.axis("off")
        plt.tight_layout()
        return _fig_to_base64(fig)

    return (
        generer_graphique_desorption(),
        generer_graphique_evolution_desorption(),
        generer_schema_colonne_desorption(),
    )

