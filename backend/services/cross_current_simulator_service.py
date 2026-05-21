from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True, slots=True)
class CrossCurrentExercise1Params:
    G_prime: float = 150.0
    L_prime: float = 200.0
    m: float = 0.5
    y0: float = 0.06
    N_etages: int = 3

    @classmethod
    def from_form(cls, form: Any) -> "CrossCurrentExercise1Params":
        def _get(key: str, default: float) -> float:
            val = form.get(key, default)
            return float(val)

        def _get_int(key: str, default: int) -> int:
            val = form.get(key, default)
            return int(val)

        params = cls(
            G_prime=_get("G_prime", cls.G_prime),
            L_prime=_get("L_prime", cls.L_prime),
            m=_get("m", cls.m),
            y0=_get("y0", cls.y0),
            N_etages=_get_int("N_etages", cls.N_etages),
        )
        params._validate()
        return params

    def _validate(self) -> None:
        if self.G_prime <= 0 or self.L_prime <= 0:
            raise ValueError("G_prime and L_prime must be > 0")
        if self.m <= 0:
            raise ValueError("m must be > 0")
        if not (0 < self.y0 < 1):
            raise ValueError("y0 must be in (0,1)")
        if self.N_etages < 1:
            raise ValueError("N_etages must be >= 1")


@dataclass(frozen=True, slots=True)
class CrossCurrentExercise3Params:
    L_prime: float = 100.0
    G_prime: float = 150.0
    m: float = 1.2
    x0: float = 0.05
    N_etages: int = 3

    @classmethod
    def from_form(cls, form: Any) -> "CrossCurrentExercise3Params":
        def _get(key: str, default: float) -> float:
            val = form.get(key, default)
            return float(val)

        def _get_int(key: str, default: int) -> int:
            val = form.get(key, default)
            return int(val)

        params = cls(
            L_prime=_get("L_prime_d", cls.L_prime),
            G_prime=_get("G_prime_d", cls.G_prime),
            m=_get("m_d", cls.m),
            x0=_get("x0", cls.x0),
            N_etages=_get_int("N_etages_d", cls.N_etages),
        )
        params._validate()
        return params

    def _validate(self) -> None:
        if self.L_prime <= 0 or self.G_prime <= 0:
            raise ValueError("L_prime and G_prime must be > 0")
        if self.m <= 0:
            raise ValueError("m must be > 0")
        if not (0 < self.x0 < 1):
            raise ValueError("x0 must be in (0,1)")
        if self.N_etages < 1:
            raise ValueError("N_etages must be >= 1")


def y_to_Y(y: float) -> float:
    return y / (1 - y)


def Y_to_y(Y: float) -> float:
    return Y / (1 + Y)


def run_cross_current(params: CrossCurrentExercise1Params | CrossCurrentExercise3Params) -> dict[str, Any]:
    if isinstance(params, CrossCurrentExercise1Params):
        return _calcul_exercice1(params)
    return _calcul_exercice3(params)


def _calcul_exercice1(p: CrossCurrentExercise1Params) -> dict[str, Any]:
    Y0 = y_to_Y(p.y0)
    A = p.L_prime / (p.m * p.G_prime)
    pente = -p.L_prime / p.G_prime

    Y_vals: list[float] = [Y0]
    X_vals: list[float] = [0.0]

    for _ in range(1, p.N_etages + 1):
        Y_prev = Y_vals[-1]
        Yi = Y_prev / (1 + A)
        Xi = Yi / p.m
        Y_vals.append(Yi)
        X_vals.append(Xi)

    taux = (Y0 - Y_vals[-1]) / Y0
    benz_abs = p.G_prime * (Y0 - Y_vals[-1])
    n_min = int(np.ceil(np.log(10) / np.log(1 + A)))

    return {
        "type": "absorption",
        "G_prime": p.G_prime,
        "L_prime": p.L_prime,
        "m": p.m,
        "y0": p.y0,
        "Y0": Y0,
        "A": A,
        "pente": pente,
        "N_etages": p.N_etages,
        "Y_vals": Y_vals,
        "X_vals": X_vals,
        "taux": taux,
        "benz_abs": benz_abs,
        "n_min": n_min,
        "suffisant": taux >= 0.9,
    }


def _calcul_exercice3(p: CrossCurrentExercise3Params) -> dict[str, Any]:
    X0 = p.x0 / (1 - p.x0)
    S = (p.m * p.G_prime) / p.L_prime
    pente = p.L_prime / p.G_prime

    X_vals: list[float] = [X0]
    Y_vals: list[float] = [0.0]

    for _ in range(1, p.N_etages + 1):
        X_prev = X_vals[-1]
        Xi = X_prev / (1 + S)
        Yi = p.m * Xi
        X_vals.append(Xi)
        Y_vals.append(Yi)

    taux = (X0 - X_vals[-1]) / X0
    NH3_desorbe = p.L_prime * (X0 - X_vals[-1])

    return {
        "type": "desorption",
        "L_prime": p.L_prime,
        "G_prime": p.G_prime,
        "m": p.m,
        "x0": p.x0,
        "X0": X0,
        "S": S,
        "pente": pente,
        "N_etages": p.N_etages,
        "X_vals": X_vals,
        "Y_vals": Y_vals,
        "taux": taux,
        "NH3_desorbe": NH3_desorbe,
    }

