"""Genera dos informes de Curva de Phillips para Chile y un HTML con dos pestañas.

El análisis anual usa la tabla anualizada entregada por el usuario y fija la NAIRU
referencial en 8,25%. El análisis mensual reutiliza las 186 observaciones comunes
del proyecto (ENE, IPC oficial no desestacionalizado, IR real e IMACEC) mediante
``phillips.load_data``.

Salidas principales:
- resultados/informe_phillips_anual.html
- resultados/informe_phillips_mensual.html
- resultados/informe_phillips_dual.html
- resultados/modelos_anuales.csv
- resultados/modelos_mensuales.csv
- resultados/resumen_modelos.json
"""

from __future__ import annotations

# -----------------------------------------------------------------------------
# Importaciones y configuración general.
# -----------------------------------------------------------------------------
import argparse
import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import statsmodels.api as sm
from plotly.offline import get_plotlyjs

from .phillips import load_data

from .rutas import PROJECT_ROOT, DATA_DIR, RESULTS_DIR, REPORTS_DIR
ROOT = PROJECT_ROOT
NAIRU = 8.25
META_INFLACION = 3.0
EPISODIO_DESDE = pd.Timestamp("2020-03-01")
EPISODIO_HASTA = pd.Timestamp("2023-08-01")


# -----------------------------------------------------------------------------
# Utilidades de estimación econométrica.
# -----------------------------------------------------------------------------
def ajustar_ols_hac(
    data: pd.DataFrame,
    dependiente: str,
    explicativas: Iterable[str],
    *,
    intercepto: bool = True,
    hac_lags: int = 1,
):
    """Ajusta OLS y calcula errores estándar HAC/Newey-West.

    El criterio AIC/BIC corresponde al ajuste OLS; los p-valores y errores estándar
    se obtienen con la matriz de covarianzas HAC. Esto permite comparar modelos con
    la misma variable dependiente sin tratar la dependencia serial como inexistente.
    """
    explicativas = list(explicativas)
    columnas = [dependiente, *explicativas]
    muestra = data[columnas].replace([np.inf, -np.inf], np.nan).dropna().copy()

    x = muestra[explicativas].astype(float)
    if intercepto:
        x = sm.add_constant(x, has_constant="add")

    y = muestra[dependiente].astype(float)
    return sm.OLS(y, x).fit(cov_type="HAC", cov_kwds={"maxlags": hac_lags})


def fila_modelo(nombre: str, resultado, dependiente: str, nota: str = "") -> dict:
    """Convierte un resultado de statsmodels en una fila tabular compacta."""
    return {
        "modelo": nombre,
        "dependiente": dependiente,
        "n": int(resultado.nobs),
        "r2": float(resultado.rsquared),
        "r2_ajustado": float(resultado.rsquared_adj),
        "aic": float(resultado.aic),
        "bic": float(resultado.bic),
        "nota": nota,
    }


def coeficientes_modelo(nombre: str, resultado) -> list[dict]:
    """Devuelve coeficientes, errores HAC, estadísticos z y p-valores."""
    filas = []
    for termino in resultado.params.index:
        filas.append(
            {
                "modelo": nombre,
                "termino": str(termino),
                "coeficiente": float(resultado.params[termino]),
                "error_hac": float(resultado.bse[termino]),
                "z": float(resultado.tvalues[termino]),
                "p_valor": float(resultado.pvalues[termino]),
            }
        )
    return filas


# -----------------------------------------------------------------------------
# Carga y preparación de los datos anuales.
# -----------------------------------------------------------------------------
def cargar_anual(ruta: Path | None = None) -> pd.DataFrame:
    """Carga la tabla anualizada desde XLSX si existe; si no, usa el CSV del repo."""
    if ruta is None:
        xlsx = DATA_DIR / "datos_anualizados.xlsx"
        csv = DATA_DIR / "datos_anualizados.csv"
        ruta = xlsx if xlsx.exists() else csv

    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el archivo anual: {ruta}")

    # Se admite el XLSX original del usuario o el CSV reproducible incluido en la rama.
    if ruta.suffix.lower() in {".xlsx", ".xls"}:
        data = pd.read_excel(ruta)
    else:
        data = pd.read_csv(ruta)

    ren = {
        "Año": "anio",
        "Tasa desocupación": "desocupacion",
        "IPC": "ipc_anual",
        "IR": "ir_real_anual",
        "Actividad Económica": "actividad_anual",
    }
    faltan = [c for c in ren if c not in data.columns]
    if faltan:
        raise ValueError(f"Faltan columnas en los datos anuales: {faltan}")

    data = data.rename(columns=ren)[list(ren.values())].copy()
    data["anio"] = pd.to_numeric(data["anio"], errors="raise").astype(int)
    for c in ["desocupacion", "ipc_anual", "ir_real_anual", "actividad_anual"]:
        data[c] = pd.to_numeric(data[c], errors="coerce")

    data = data.sort_values("anio").drop_duplicates("anio").reset_index(drop=True)
    data["brecha_desempleo"] = data["desocupacion"] - NAIRU
    data["ipc_rezago_1"] = data["ipc_anual"].shift(1)
    data["delta_ipc"] = data["ipc_anual"] - data["ipc_rezago_1"]
    return data


# -----------------------------------------------------------------------------
# Estimación anual: réplica del cálculo central y modelos de contraste.
# -----------------------------------------------------------------------------
def analizar_anual(data: pd.DataFrame) -> dict:
    """Estima la especificación anual central y cuatro contrastes."""
    # 2010 se conserva solo para construir el rezago de inflación de 2011.
    muestra = data.loc[data["anio"].between(2011, 2025)].copy()

    modelos = {
        "A1_estatica": ajustar_ols_hac(muestra, "ipc_anual", ["brecha_desempleo"], hac_lags=1),
        "A2_aceleracion": ajustar_ols_hac(muestra, "delta_ipc", ["brecha_desempleo"], hac_lags=1),
        "A3_expectativas": ajustar_ols_hac(
            muestra, "ipc_anual", ["ipc_rezago_1", "brecha_desempleo"], hac_lags=1
        ),
        "A4_expectativas_actividad": ajustar_ols_hac(
            muestra,
            "ipc_anual",
            ["ipc_rezago_1", "brecha_desempleo", "actividad_anual"],
            hac_lags=1,
        ),
        # Modelo central: impone que con u = NAIRU la inflación no acelera.
        "A5_aceleracion_nairu": ajustar_ols_hac(
            muestra,
            "delta_ipc",
            ["brecha_desempleo"],
            intercepto=False,
            hac_lags=1,
        ),
    }

    comparacion = pd.DataFrame(
        [
            fila_modelo("A1_estatica", modelos["A1_estatica"], "IPC anual"),
            fila_modelo("A2_aceleracion", modelos["A2_aceleracion"], "Δ IPC anual"),
            fila_modelo("A3_expectativas", modelos["A3_expectativas"], "IPC anual"),
            fila_modelo(
                "A4_expectativas_actividad",
                modelos["A4_expectativas_actividad"],
                "IPC anual",
            ),
            fila_modelo(
                "A5_aceleracion_nairu",
                modelos["A5_aceleracion_nairu"],
                "Δ IPC anual",
                "Especificación central con NAIRU=8,25% e intercepto restringido a cero.",
            ),
        ]
    )
    coeficientes = pd.DataFrame(
        [fila for nombre, res in modelos.items() for fila in coeficientes_modelo(nombre, res)]
    )

    central = modelos["A5_aceleracion_nairu"]
    beta = float(central.params["brecha_desempleo"])
    return {
        "data": muestra,
        "modelos": modelos,
        "comparacion": comparacion,
        "coeficientes": coeficientes,
        "central": central,
        "ecuacion": f"Δπₜ = {beta:+.3f} · (uₜ − {NAIRU:.2f})",
    }


# -----------------------------------------------------------------------------
# Preparación y estimación mensual con las series oficiales del proyecto.
# -----------------------------------------------------------------------------
def preparar_mensual() -> pd.DataFrame:
    """Reutiliza la integración de ENE, IPC, IR e IMACEC ya validada por el proyecto."""
    data, _, _ = load_data(ipc_ajuste="original")
    data = data.copy().sort_values("fecha").reset_index(drop=True)
    data["brecha_desempleo"] = data["desocupacion"] - NAIRU
    data["ipc_rezago_1m"] = data["ipc_anual"].shift(1)
    data["ipc_rezago_12m"] = data["ipc_anual"].shift(12)
    data["delta_ipc_1m"] = data["ipc_anual"] - data["ipc_rezago_1m"]
    data["delta_ipc_12m"] = data["ipc_anual"] - data["ipc_rezago_12m"]
    data["episodio_2020_2023"] = data["fecha"].between(EPISODIO_DESDE, EPISODIO_HASTA).astype(int)
    return data


def analizar_mensual(data: pd.DataFrame) -> dict:
    """Compara especificaciones mensuales y selecciona por BIC dentro del grupo de niveles."""
    # HAC(12) es una corrección conservadora para series mensuales con tasas a 12 meses.
    modelos = {
        "M1_estatica": ajustar_ols_hac(data, "ipc_anual", ["brecha_desempleo"], hac_lags=12),
        "M2_adaptativa": ajustar_ols_hac(
            data, "ipc_anual", ["ipc_rezago_1m", "brecha_desempleo"], hac_lags=12
        ),
        "M3_adaptativa_actividad": ajustar_ols_hac(
            data,
            "ipc_anual",
            ["ipc_rezago_1m", "brecha_desempleo", "imacec_promedio_anual"],
            hac_lags=12,
        ),
        "M4_adaptativa_actividad_episodio": ajustar_ols_hac(
            data,
            "ipc_anual",
            [
                "ipc_rezago_1m",
                "brecha_desempleo",
                "imacec_promedio_anual",
                "episodio_2020_2023",
            ],
            hac_lags=12,
        ),
        "M5_rezago_12m": ajustar_ols_hac(
            data, "ipc_anual", ["ipc_rezago_12m", "brecha_desempleo"], hac_lags=12
        ),
        "M6_rezago_12m_actividad": ajustar_ols_hac(
            data,
            "ipc_anual",
            ["ipc_rezago_12m", "brecha_desempleo", "imacec_promedio_anual"],
            hac_lags=12,
        ),
        # Réplica mensual de la ecuación anual con NAIRU impuesta y sin intercepto.
        "M7_aceleracion_12m_nairu": ajustar_ols_hac(
            data,
            "delta_ipc_12m",
            ["brecha_desempleo"],
            intercepto=False,
            hac_lags=12,
        ),
        "M8_aceleracion_12m": ajustar_ols_hac(
            data, "delta_ipc_12m", ["brecha_desempleo"], hac_lags=12
        ),
        "M9_aceleracion_12m_actividad": ajustar_ols_hac(
            data,
            "delta_ipc_12m",
            ["brecha_desempleo", "imacec_promedio_anual"],
            hac_lags=12,
        ),
        "M10_aceleracion_12m_actividad_episodio": ajustar_ols_hac(
            data,
            "delta_ipc_12m",
            ["brecha_desempleo", "imacec_promedio_anual", "episodio_2020_2023"],
            hac_lags=12,
        ),
    }

    nivel = [f"M{i}_" for i in range(1, 7)]
    nombres_nivel = [n for n in modelos if any(n.startswith(pref) for pref in nivel)]
    mejor_nivel = min(nombres_nivel, key=lambda n: modelos[n].bic)

    comparacion = pd.DataFrame(
        [
            fila_modelo(nombre, res, "IPC anual" if nombre in nombres_nivel else "Δ12 IPC")
            for nombre, res in modelos.items()
        ]
    )
    coeficientes = pd.DataFrame(
        [fila for nombre, res in modelos.items() for fila in coeficientes_modelo(nombre, res)]
    )

    central = modelos["M7_aceleracion_12m_nairu"]
    beta = float(central.params["brecha_desempleo"])
    return {
        "data": data,
        "modelos": modelos,
        "comparacion": comparacion,
        "coeficientes": coeficientes,
        "central": central,
        "mejor_nivel": mejor_nivel,
        "ecuacion": f"Δ₁₂πₜ = {beta:+.3f} · (uₜ − {NAIRU:.2f})",
    }


# -----------------------------------------------------------------------------
# Figuras: evidencia observada y ecuación de aceleración con NAIRU fija.
# -----------------------------------------------------------------------------
def figura_phillips_anual(data: pd.DataFrame) -> go.Figure:
    """Nube anual de inflación y desempleo con referencias de política."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["desocupacion"],
            y=data["ipc_anual"],
            mode="markers+text",
            text=data["anio"].astype(str),
            textposition="top center",
            marker=dict(size=11, color=data["actividad_anual"], colorscale="RdBu", colorbar=dict(title="Actividad anual (%)")),
            customdata=np.column_stack([data["anio"], data["ir_real_anual"], data["actividad_anual"]]),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>Desocupación: %{x:.2f}%<br>IPC: %{y:.2f}%"
                "<br>IR real: %{customdata[1]:+.2f}%<br>Actividad: %{customdata[2]:+.2f}%<extra></extra>"
            ),
            name="Años",
        )
    )
    fig.add_vline(x=NAIRU, line_dash="dashdot", annotation_text=f"NAIRU ref. {NAIRU:.2f}%")
    fig.add_hline(y=META_INFLACION, line_dash="dash", annotation_text="Meta IPC 3%")
    fig.update_layout(
        template="plotly_white",
        title="Datos anuales: inflación y desempleo",
        xaxis_title="Tasa de desocupación (%)",
        yaxis_title="IPC anual (%)",
        height=560,
        margin=dict(l=70, r=80, t=80, b=60),
    )
    return fig


def figura_aceleracion(data: pd.DataFrame, central, mensual: bool) -> go.Figure:
    """Grafica la aceleración de inflación frente a la brecha de desempleo y la recta restringida."""
    ycol = "delta_ipc_12m" if mensual else "delta_ipc"
    etiqueta = "Mensual (Δ12 de inflación anual)" if mensual else "Anual"
    muestra = data[["brecha_desempleo", ycol]].dropna().copy()
    beta = float(central.params["brecha_desempleo"])
    xx = np.linspace(muestra["brecha_desempleo"].min(), muestra["brecha_desempleo"].max(), 120)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=muestra["brecha_desempleo"],
            y=muestra[ycol],
            mode="markers",
            marker=dict(size=8, opacity=0.72),
            name="Observaciones",
            hovertemplate="Brecha desempleo: %{x:+.2f} pp<br>Aceleración IPC: %{y:+.2f} pp<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=xx,
            y=beta * xx,
            mode="lines",
            line=dict(width=3),
            name="Modelo con NAIRU impuesta",
            hovertemplate="Brecha: %{x:+.2f} pp<br>Predicción: %{y:+.2f} pp<extra></extra>",
        )
    )
    fig.add_vline(x=0, line_dash="dot")
    fig.add_hline(y=0, line_dash="dot")
    fig.update_layout(
        template="plotly_white",
        title=f"{etiqueta}: aceleración de la inflación y brecha de desempleo",
        xaxis_title=f"u − {NAIRU:.2f}% (puntos porcentuales)",
        yaxis_title="Cambio de inflación (puntos porcentuales)",
        height=500,
        margin=dict(l=70, r=40, t=80, b=60),
    )
    return fig


def figura_mensual_contexto(data: pd.DataFrame) -> go.Figure:
    """Muestra conjuntamente inflación, desempleo e IMACEC para el análisis mensual."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["fecha"],
            y=data["ipc_anual"],
            mode="lines",
            name="IPC 12 meses",
            line=dict(width=2.2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data["fecha"],
            y=data["desocupacion"],
            mode="lines",
            name="Desocupación",
            yaxis="y2",
            line=dict(width=1.7),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=data["fecha"],
            y=data["imacec_promedio_anual"],
            mode="lines",
            name="IMACEC promedio 3m, 12 meses",
            line=dict(width=1.4, dash="dot"),
        )
    )
    fig.add_hline(y=META_INFLACION, line_dash="dash")
    fig.update_layout(
        template="plotly_white",
        title="Datos mensuales: inflación, desempleo y actividad",
        yaxis=dict(title="IPC / IMACEC (%)"),
        yaxis2=dict(title="Desocupación (%)", overlaying="y", side="right"),
        xaxis_title="Mes",
        hovermode="x unified",
        height=560,
        margin=dict(l=70, r=80, t=80, b=60),
    )
    return fig


# -----------------------------------------------------------------------------
# Construcción de tablas y textos interpretativos para los informes.
# -----------------------------------------------------------------------------
def tabla_html(df: pd.DataFrame, columnas: list[str] | None = None) -> str:
    """Convierte una tabla a HTML con redondeo legible."""
    tabla = df.copy()
    if columnas:
        tabla = tabla[columnas]
    for c in tabla.select_dtypes(include=["number"]).columns:
        tabla[c] = tabla[c].map(lambda v: "" if pd.isna(v) else f"{v:.4f}")
    return tabla.to_html(index=False, classes="tabla", border=0, escape=True)


def interpretacion_anual(resultado: dict) -> str:
    """Texto breve y no causal para el informe anual."""
    r = resultado["central"]
    b = float(r.params["brecha_desempleo"])
    p = float(r.pvalues["brecha_desempleo"])
    return (
        f"La especificación central impone una NAIRU de {NAIRU:.2f}% y estima una pendiente de "
        f"{b:+.3f}. El signo es compatible con la intuición de Phillips, pero el p-valor HAC es "
        f"{p:.3f} y el ajuste es muy bajo. Con solo 15 observaciones útiles, el resultado debe "
        "interpretarse como evidencia descriptiva, no como una estimación causal ni como validación "
        "de una relación estable."
    )


def interpretacion_mensual(resultado: dict) -> str:
    """Resume la evidencia mensual y la sensibilidad entre especificaciones."""
    central = resultado["central"]
    mejor = resultado["modelos"][resultado["mejor_nivel"]]
    b = float(central.params["brecha_desempleo"])
    p = float(central.pvalues["brecha_desempleo"])
    coef_gap_mejor = float(mejor.params.get("brecha_desempleo", np.nan))
    p_gap_mejor = float(mejor.pvalues.get("brecha_desempleo", np.nan))
    return (
        f"La réplica mensual de la ecuación con NAIRU fija entrega una pendiente de {b:+.3f} "
        f"(p HAC={p:.3f}). Entre los modelos en niveles comparables por BIC, el seleccionado es "
        f"{resultado['mejor_nivel']}; allí el coeficiente de la brecha de desempleo es "
        f"{coef_gap_mejor:+.3f} (p HAC={p_gap_mejor:.3f}). La inflación rezagada domina el ajuste "
        "de corto plazo y la actividad aporta información en algunas especificaciones. La magnitud "
        "y el signo de la brecha cambian al controlar episodios extraordinarios, lo que confirma "
        "que la relación no es estable y que los resultados no deben interpretarse causalmente."
    )


def contenido_informe_anual(resultado: dict, include_plotly: bool) -> str:
    """Genera el contenido HTML del informe anual."""
    fig1 = pio.to_html(
        figura_phillips_anual(resultado["data"]),
        full_html=False,
        include_plotlyjs=False,
        config={"responsive": True, "displaylogo": False},
    )
    fig2 = pio.to_html(
        figura_aceleracion(resultado["data"], resultado["central"], mensual=False),
        full_html=False,
        include_plotlyjs=False,
        config={"responsive": True, "displaylogo": False},
    )
    coef = resultado["coeficientes"]
    comp = resultado["comparacion"]
    return f"""
      <section class="bloque">
        <h2>Informe con datos anuales</h2>
        <p class="bajada">Años completos 2011–2025; 2010 se usa únicamente para construir la inflación rezagada de 2011. NAIRU fija: {NAIRU:.2f}%.</p>
        <div class="ecuacion">{resultado['ecuacion']}</div>
        <p>{interpretacion_anual(resultado)}</p>
        <div class="grid-kpi">
          <div class="kpi"><span>Observaciones</span><strong>{int(resultado['central'].nobs)}</strong></div>
          <div class="kpi"><span>Pendiente central</span><strong>{resultado['central'].params['brecha_desempleo']:+.3f}</strong></div>
          <div class="kpi"><span>p-valor HAC</span><strong>{resultado['central'].pvalues['brecha_desempleo']:.3f}</strong></div>
          <div class="kpi"><span>R²</span><strong>{resultado['central'].rsquared:.3f}</strong></div>
        </div>
        {fig1}
        {fig2}
        <h3>Comparación de especificaciones</h3>
        {tabla_html(comp, ['modelo','dependiente','n','r2_ajustado','aic','bic','nota'])}
        <h3>Coeficientes y errores HAC</h3>
        {tabla_html(coef, ['modelo','termino','coeficiente','error_hac','p_valor'])}
        <p class="nota">AIC/BIC solo son comparables de forma directa entre modelos que usan la misma variable dependiente. En los modelos sin constante, el R² de statsmodels es no centrado.</p>
      </section>
    """


def contenido_informe_mensual(resultado: dict) -> str:
    """Genera el contenido HTML del informe mensual."""
    fig1 = pio.to_html(
        figura_mensual_contexto(resultado["data"]),
        full_html=False,
        include_plotlyjs=False,
        config={"responsive": True, "displaylogo": False},
    )
    fig2 = pio.to_html(
        figura_aceleracion(resultado["data"], resultado["central"], mensual=True),
        full_html=False,
        include_plotlyjs=False,
        config={"responsive": True, "displaylogo": False},
    )
    coef = resultado["coeficientes"]
    comp = resultado["comparacion"]
    mejor = resultado["modelos"][resultado["mejor_nivel"]]
    return f"""
      <section class="bloque">
        <h2>Informe con datos mensuales</h2>
        <p class="bajada">Enero de 2011 a junio de 2026. IPC oficial no desestacionalizado; ENE alineada al mes central; actividad = variación interanual del promedio móvil de tres meses del IMACEC original.</p>
        <div class="ecuacion">{resultado['ecuacion']}</div>
        <p>{interpretacion_mensual(resultado)}</p>
        <div class="grid-kpi">
          <div class="kpi"><span>Observaciones comunes</span><strong>{len(resultado['data'])}</strong></div>
          <div class="kpi"><span>Pendiente Δ12 central</span><strong>{resultado['central'].params['brecha_desempleo']:+.3f}</strong></div>
          <div class="kpi"><span>p-valor HAC(12)</span><strong>{resultado['central'].pvalues['brecha_desempleo']:.3f}</strong></div>
          <div class="kpi"><span>Mejor BIC en niveles</span><strong>{resultado['mejor_nivel']}</strong></div>
        </div>
        {fig1}
        {fig2}
        <h3>Comparación de especificaciones mensuales</h3>
        {tabla_html(comp, ['modelo','dependiente','n','r2_ajustado','aic','bic'])}
        <h3>Coeficientes y errores HAC(12)</h3>
        {tabla_html(coef, ['modelo','termino','coeficiente','error_hac','p_valor'])}
        <p class="nota">El modelo elegido por BIC entre M1–M6 es {resultado['mejor_nivel']} (BIC={mejor.bic:.3f}). El uso de inflación a 12 meses genera fuerte persistencia; por eso el coeficiente de inflación rezagada no debe interpretarse como una elasticidad estructural.</p>
      </section>
    """


# -----------------------------------------------------------------------------
# Plantilla HTML y escritura de los tres informes.
# -----------------------------------------------------------------------------
CSS = """
:root{font-family:Inter,Segoe UI,Arial,sans-serif;color:#172033;background:#f4f6f8}
body{margin:0;background:#f4f6f8}.contenedor{max-width:1220px;margin:0 auto;padding:28px}
.cabecera{background:#fff;border-radius:14px;padding:24px 28px;box-shadow:0 1px 4px #0002;margin-bottom:18px}
h1{font-size:28px;margin:0 0 8px}.cabecera p,.bajada,.nota{color:#5c6678}.bloque{background:#fff;border-radius:14px;padding:24px 28px;box-shadow:0 1px 4px #0002}
h2{margin-top:0}.ecuacion{font-family:Cambria,Georgia,serif;font-size:22px;background:#eef3f8;border-left:4px solid #345b7e;padding:14px 16px;margin:14px 0 18px}
.grid-kpi{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:16px 0 24px}.kpi{border:1px solid #dbe2ea;border-radius:10px;padding:12px;background:#fbfcfd}.kpi span{display:block;color:#667085;font-size:12px}.kpi strong{display:block;font-size:18px;margin-top:4px;word-break:break-word}
.tabla{border-collapse:collapse;width:100%;font-size:13px;margin:10px 0 22px}.tabla th,.tabla td{border-bottom:1px solid #e3e7ec;text-align:left;padding:8px 9px}.tabla th{background:#f1f4f7;position:sticky;top:0}.tabla tr:hover td{background:#fafbfd}
.tabs{display:flex;gap:8px;margin:0 0 14px}.tab-button{border:0;border-radius:9px;padding:10px 16px;background:#dfe6ee;color:#24364b;font-weight:600;cursor:pointer}.tab-button.active{background:#244d73;color:white}.tab-panel{display:none}.tab-panel.active{display:block}
@media(max-width:800px){.grid-kpi{grid-template-columns:1fr 1fr}.contenedor{padding:12px}.bloque,.cabecera{padding:18px}}
"""


def html_documento(titulo: str, cuerpo: str, *, tabs: bool = False) -> str:
    """Crea un HTML autocontenido con Plotly embebido."""
    tab_script = """
<script>
// Activa una pestaña y fuerza el redimensionamiento de los gráficos Plotly ocultos.
document.querySelectorAll('.tab-button').forEach(btn=>btn.addEventListener('click',()=>{
  document.querySelectorAll('.tab-button').forEach(x=>x.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(x=>x.classList.remove('active'));
  btn.classList.add('active'); document.getElementById(btn.dataset.tab).classList.add('active');
  setTimeout(()=>window.dispatchEvent(new Event('resize')),60);
}));
</script>
""" if tabs else ""
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{titulo}</title><style>{CSS}</style><script>{get_plotlyjs()}</script></head>
<body><main class="contenedor"><header class="cabecera"><h1>{titulo}</h1><p>Chile · Curva de Phillips · NAIRU referencial fija en {NAIRU:.2f}% · IPC oficial no desestacionalizado</p></header>{cuerpo}</main>{tab_script}</body></html>"""


def generar_informes(anual: dict, mensual: dict, out_dir: Path) -> dict[str, Path]:
    """Escribe los informes anual, mensual y combinado con pestañas."""
    out_dir.mkdir(parents=True, exist_ok=True)
    anual_body = contenido_informe_anual(anual, include_plotly=False)
    mensual_body = contenido_informe_mensual(mensual)

    rutas = {
        "anual": out_dir / "informe_phillips_anual.html",
        "mensual": out_dir / "informe_phillips_mensual.html",
        "dual": out_dir / "informe_phillips_dual.html",
    }
    rutas["anual"].write_text(html_documento("Curva de Phillips · análisis anual", anual_body), encoding="utf-8")
    rutas["mensual"].write_text(html_documento("Curva de Phillips · análisis mensual", mensual_body), encoding="utf-8")

    dual_body = f"""
      <div class="tabs">
        <button class="tab-button active" data-tab="panel-anual">Datos anuales</button>
        <button class="tab-button" data-tab="panel-mensual">Datos mensuales</button>
      </div>
      <div id="panel-anual" class="tab-panel active">{anual_body}</div>
      <div id="panel-mensual" class="tab-panel">{mensual_body}</div>
    """
    rutas["dual"].write_text(html_documento("Inflación y desempleo en Chile · análisis anual y mensual", dual_body, tabs=True), encoding="utf-8")
    return rutas


# -----------------------------------------------------------------------------
# Exportación de resultados tabulares y resumen JSON reproducible.
# -----------------------------------------------------------------------------
def exportar_resultados(anual: dict, mensual: dict, out_dir: Path) -> None:
    """Guarda tablas de modelos, coeficientes y un resumen de resultados clave."""
    out_dir.mkdir(parents=True, exist_ok=True)
    anual["comparacion"].to_csv(out_dir / "modelos_anuales.csv", index=False, encoding="utf-8-sig")
    anual["coeficientes"].to_csv(out_dir / "coeficientes_anuales.csv", index=False, encoding="utf-8-sig")
    mensual["comparacion"].to_csv(out_dir / "modelos_mensuales.csv", index=False, encoding="utf-8-sig")
    mensual["coeficientes"].to_csv(out_dir / "coeficientes_mensuales.csv", index=False, encoding="utf-8-sig")

    resumen = {
        "nairu_pct": NAIRU,
        "meta_inflacion_pct": META_INFLACION,
        "anual": {
            "periodo": [int(anual["data"]["anio"].min()), int(anual["data"]["anio"].max())],
            "n": int(anual["central"].nobs),
            "ecuacion_central": anual["ecuacion"],
            "beta_gap": float(anual["central"].params["brecha_desempleo"]),
            "p_hac": float(anual["central"].pvalues["brecha_desempleo"]),
        },
        "mensual": {
            "periodo": [mensual["data"]["mes"].iloc[0], mensual["data"]["mes"].iloc[-1]],
            "n_comun": int(len(mensual["data"])),
            "ecuacion_central": mensual["ecuacion"],
            "beta_gap": float(mensual["central"].params["brecha_desempleo"]),
            "p_hac": float(mensual["central"].pvalues["brecha_desempleo"]),
            "mejor_modelo_niveles_bic": mensual["mejor_nivel"],
        },
    }
    (out_dir / "resumen_modelos.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# -----------------------------------------------------------------------------
# Punto de entrada de línea de comandos.
# -----------------------------------------------------------------------------
def main() -> int:
    """Ejecuta ambos análisis y genera todos los informes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anual", type=Path, default=None, help="Ruta opcional a datos_anualizados.xlsx/csv")
    parser.add_argument("--resultados", type=Path, default=RESULTS_DIR, help="Directorio de resultados tabulares")
    parser.add_argument("--informes", type=Path, default=REPORTS_DIR, help="Directorio de informes HTML")
    args = parser.parse_args()

    anual_df = cargar_anual(args.anual)
    anual = analizar_anual(anual_df)
    mensual_df = preparar_mensual()
    mensual = analizar_mensual(mensual_df)

    exportar_resultados(anual, mensual, args.resultados)
    rutas = generar_informes(anual, mensual, args.informes)

    print("Análisis anual:", anual["ecuacion"])
    print("Análisis mensual:", mensual["ecuacion"])
    print("Mejor modelo mensual en niveles por BIC:", mensual["mejor_nivel"])
    for nombre, ruta in rutas.items():
        print(f"{nombre}: {ruta}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())