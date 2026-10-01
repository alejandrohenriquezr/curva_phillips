"""Datos y estimaciones anuales reproducibles de inflación y desempleo."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

from .rutas import DATA_DIR, RESULTS_DIR

NAIRU = 8.25
FUENTE = DATA_DIR / "datos_anualizados2.xlsx"
COLUMNAS = {"Año": "anio", "Tasa desocupación": "desocupacion", "IPC": "ipc_anual",
            "PIB volumen a precios del año anterior encadenado": "pib_anual"}
NOTA_2026 = ("2026 corresponde al corte julio 2026 respecto de julio 2025 entregado por el usuario; "
             "no es un año calendario completo. Sus valores se conservan sin sustituciones.")


def cargar_anual(ruta: Path = FUENTE) -> pd.DataFrame:
    ruta = Path(ruta)
    raw = pd.read_excel(ruta) if ruta.suffix.lower() == ".xlsx" else pd.read_csv(ruta)
    if not set(COLUMNAS).issubset(raw.columns):
        raise ValueError(f"Se requieren las columnas: {list(COLUMNAS)}")
    data = raw[list(COLUMNAS)].rename(columns=COLUMNAS).apply(pd.to_numeric, errors="raise")
    if not np.isfinite(data.to_numpy(dtype=float)).all():
        raise ValueError("Los datos deben ser finitos y no contener faltantes")
    if (data.anio % 1 != 0).any() or data.anio.duplicated().any():
        raise ValueError("Los años deben ser enteros y únicos")
    data.anio = data.anio.astype(int)
    data = data.sort_values("anio").reset_index(drop=True)
    if data.anio.tolist() != list(range(1997, 2027)):
        raise ValueError("Esta edición requiere todos los años 1997–2026; revisar metodología si cambia la cobertura")
    if not data.desocupacion.between(0, 100).all():
        raise ValueError("La tasa de desocupación debe estar entre 0 y 100")
    data["corte"] = np.where(data.anio.eq(2026), "julio 2026 vs julio 2025", "anual según tabla")
    data["comparable"] = data.anio.lt(2026)
    data["brecha_desempleo"] = data.desocupacion - NAIRU
    # Los rezagos se calculan antes de ordenar la visualización por desempleo.
    data["ipc_rezago_1"] = data.ipc_anual.shift(1)
    data["delta_ipc"] = data.ipc_anual.diff()
    return data


def importar_fuente(ruta: Path = FUENTE) -> dict:
    data = cargar_anual(ruta)
    csv = data[list(COLUMNAS.values())].rename(columns={v: k for k, v in COLUMNAS.items()})
    csv.to_csv(DATA_DIR / "datos_anualizados.csv", index=False, encoding="utf-8")
    metadata = {"archivo": Path(ruta).name, "sha256": hashlib.sha256(Path(ruta).read_bytes()).hexdigest(),
                "filas": len(data), "periodo": [1997, 2026], "nota_2026": NOTA_2026,
                "transformacion": "Sin reemplazar, reescalar ni corregir valores; orden cronológico para cálculos",
                "pib": "Variable de la tabla del usuario; se interpreta como variación según su indicación, no como brecha de producto"}
    (DATA_DIR / "metadatos").mkdir(exist_ok=True)
    (DATA_DIR / "metadatos" / "fuente_anual.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return metadata


def ajustar(data, dependiente, explicativas, intercepto=True, hac_lags=1):
    sample = data[[dependiente, *explicativas]].dropna()
    x = sample[explicativas].astype(float)
    if intercepto:
        x = sm.add_constant(x, has_constant="add")
    if len(sample) <= x.shape[1] + 2 or np.linalg.matrix_rank(x) < x.shape[1]:
        raise ValueError("Muestra insuficiente o matriz de diseño singular")
    return sm.OLS(sample[dependiente], x).fit(cov_type="HAC", cov_kwds={"maxlags": hac_lags, "use_correction": True}, use_t=True)


def analizar_anual(data):
    modelos, filas, coef = {}, [], []
    specs = {
        "estatica": ("ipc_anual", ["brecha_desempleo"], True),
        "aceleracion": ("delta_ipc", ["brecha_desempleo"], True),
        "persistencia": ("ipc_anual", ["ipc_rezago_1", "brecha_desempleo"], True),
        "persistencia_pib": ("ipc_anual", ["ipc_rezago_1", "brecha_desempleo", "pib_anual"], True),
        "aceleracion_pib": ("delta_ipc", ["brecha_desempleo", "pib_anual"], True),
        "nairu_restringida": ("delta_ipc", ["brecha_desempleo"], False),
    }
    # Muestras comunes: comparabilidad de AIC/BIC dentro de dependiente y escenario.
    for escenario, limite in [("historica", 2025), ("sensibilidad_2026", 2026)]:
        muestra = data.loc[data.anio.between(1998, limite)]
        for nombre, (dep, xs, intercepto) in specs.items():
            key = f"{escenario}_{nombre}"
            fit = ajustar(muestra, dep, xs, intercepto)
            modelos[key] = fit
            filas.append({"modelo": key, "escenario": escenario, "dependiente": dep,
                          "desde": int(muestra.anio.min()), "hasta": limite, "n": int(fit.nobs),
                          "r2": float(fit.rsquared), "tipo_r2": "centrado" if intercepto else "no centrado",
                          "aic": float(fit.aic), "bic": float(fit.bic)})
            ci = fit.conf_int()
            for term in fit.params.index:
                coef.append({"modelo": key, "termino": term, "coeficiente": float(fit.params[term]),
                             "error_hac": float(fit.bse[term]), "p_valor": float(fit.pvalues[term]),
                             "ic95_inferior": float(ci.loc[term, 0]), "ic95_superior": float(ci.loc[term, 1])})
    estabilidad = []
    historica = data.loc[data.anio.between(1998, 2025)]
    ventanas = {"1998–2009": historica.anio.le(2009), "2010–2019": historica.anio.between(2010, 2019),
                "2011–2025": historica.anio.ge(2011), "sin 2020–2023": ~historica.anio.between(2020, 2023)}
    for etiqueta, mask in ventanas.items():
        fit = ajustar(historica.loc[mask], "delta_ipc", ["brecha_desempleo"], False)
        estabilidad.append({"ventana": etiqueta, "n": int(fit.nobs), "beta": float(fit.params.iloc[0]),
                            "p_hac": float(fit.pvalues.iloc[0]), "ic95_inferior": float(fit.conf_int().iloc[0, 0]),
                            "ic95_superior": float(fit.conf_int().iloc[0, 1])})
    # Exclusión de observaciones después de calcular rezagos: no une años separados.
    influencia = []
    for year in historica.anio:
        fit = ajustar(historica.loc[historica.anio.ne(year)], "delta_ipc", ["brecha_desempleo"], False)
        influencia.append({"anio_excluido": int(year), "beta": float(fit.params.iloc[0])})
    robustez = []
    for u in [8.0, 8.25, 8.5]:
        for lag in [0, 1, 2]:
            sample = historica.assign(brecha_desempleo=historica.desocupacion-u)
            fit = ajustar(sample, "delta_ipc", ["brecha_desempleo"], False, lag)
            robustez.append({"referencia_desempleo": u, "rezagos_hac": lag,
                             "beta": float(fit.params.iloc[0]), "p_hac": float(fit.pvalues.iloc[0])})
    descriptivos = []
    for lo, hi in [(1997, 2009), (2010, 2019), (2020, 2025)]:
        sample = data.loc[data.anio.between(lo, hi)]
        descriptivos.append({"periodo": f"{lo}–{hi}", "n": len(sample), "desocupacion_media": sample.desocupacion.mean(),
                             "ipc_medio": sample.ipc_anual.mean(), "pib_medio": sample.pib_anual.mean(),
                             "correlacion_ipc_desocupacion": sample.ipc_anual.corr(sample.desocupacion)})
    return {"data": data, "modelos": modelos, "comparacion": pd.DataFrame(filas), "coeficientes": pd.DataFrame(coef),
            "estabilidad": pd.DataFrame(estabilidad), "influencia": pd.DataFrame(influencia),
            "robustez": pd.DataFrame(robustez), "descriptivos": pd.DataFrame(descriptivos)}


def exportar_resultados(resultado, destino=RESULTS_DIR):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    for key in ["comparacion", "coeficientes", "estabilidad", "influencia", "robustez", "descriptivos"]:
        resultado[key].to_csv(destino / f"{key}_anuales.csv", index=False, encoding="utf-8")
    resultado["data"].to_csv(destino / "datos_anuales_cronologicos.csv", index=False)
    resultado["data"].sort_values(["desocupacion", "anio"]).to_csv(destino / "datos_phillips.csv", index=False)
    resumen = {"referencia_desempleo": NAIRU, "nota_2026": NOTA_2026,
               "inferencia": "HAC con corrección de muestra y distribución t; rezago 1 por defecto",
               "fuente_sha256": hashlib.sha256(FUENTE.read_bytes()).hexdigest(),
               "observacion_2026": resultado["data"].iloc[-1][["anio", "desocupacion", "ipc_anual", "pib_anual", "corte"]].to_dict(),
               "modelos": resultado["comparacion"].to_dict(orient="records"),
               "coeficientes": resultado["coeficientes"].to_dict(orient="records")}
    (destino / "resumen_modelos.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2, allow_nan=False)+"\n", encoding="utf-8")
