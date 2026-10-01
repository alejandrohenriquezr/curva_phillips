"""Texto compartido por artículo, cuaderno e informe para evitar cifras divergentes."""
from .analisis_anual import NAIRU, NOTA_2026

REFERENCIAS = [
    ("Banco Central de Chile — IPoM diciembre 2024, Recuadro II.1 Holguras en el mercado laboral",
     "https://www.bcentral.cl/es/web/banco-central/contenido/-/details/informe-de-politica-monetaria-diciembre-2024"),
    ("FMI — Fiscal Policy Can Help Tame Inflation and Protect the Most Vulnerable, 2023",
     "https://www.imf.org/en/Blogs/Articles/2023/04/03/fiscal-policy-can-help-tame-inflation-and-protect-the-most-vulnerable"),
    ("FMI — To Reduce Inequality, Employ Young People, 2019",
     "https://www.imf.org/en/Blogs/Articles/2019/06/13/blog-to-reduce-inequality-employ-young-people"),
]


def numero(x, dec=3):
    return f"{x:.{dec}f}".replace(".", ",")


def secciones(r):
    h = r["modelos"]["historica_nairu_restringida"]
    s = r["modelos"]["sensibilidad_2026_nairu_restringida"]
    p = r["modelos"]["historica_persistencia_pib"]
    ci = h.conf_int().loc["brecha_desempleo"]
    dato = r["data"].iloc[-1]
    beta = h.params["brecha_desempleo"]
    evidencia = ("El intervalo contiene cero: esta muestra no permite distinguir con precisión la pendiente de cero al 5%."
                 if ci.iloc[0] <= 0 <= ci.iloc[1] else
                 "El intervalo excluye cero en esta especificación, sin establecer por ello causalidad ni estabilidad histórica.")
    ventanas = "; ".join(f"{row.ventana}: {numero(row.beta)} (n={row.n})" for row in r["estabilidad"].itertuples())
    inf = r["influencia"]
    return [
        ("title", "Inflación desempleo y bienestar en Chile"),
        ("subtitle", "Evidencia anual de 1997 a 2025 y corte interanual de julio de 2026"),
        ("h", "Qué propone la curva de Phillips"),
        ("p", "La curva de Phillips estudia cómo la holgura del mercado laboral se relaciona con la inflación. "
         "Cuando las empresas compiten por trabajadores escasos, los salarios y los costos pueden presionar los precios; "
         "con mayor desempleo, ese canal puede debilitarse. La relación también depende de las expectativas, la productividad "
         "y los costos externos. Por eso una nube de inflación y desempleo no basta para medir el efecto de una política."),
        ("p", "Una representación aumentada por expectativas es πₜ = πᵉₜ + α + b(uₜ − u*) + γzₜ + εₜ, "
         "con b < 0 como signo teórico habitual. Si se aproxima la inflación esperada por la inflación pasada, "
         "se obtiene Δπₜ = α + b(uₜ − u*) + γzₜ + εₜ. La especificación restringida fija α = 0 y omite zₜ: "
         "Δπₜ = b(uₜ − 8,25). Esta última impone inflación estable cuando el desempleo coincide con la referencia."),
        ("p", "El 8,25% es un supuesto fijo del ejercicio, no una NAIRU estimada para cada año ni una meta social de desempleo. "
         "El Banco Central analiza las holguras laborales con varios indicadores [1]. Un solo umbral no recoge cambios "
         "de participación, composición sectorial, productividad o calidad del empleo. La inflación rezagada es una "
         "aproximación de expectativas, no una medición de lo que esperaban hogares y empresas."),
        ("h", "Alcance de los datos y de la comparación"),
        ("p", "La tabla contiene 30 observaciones de desempleo, IPC y PIB. Se conservan exactamente los números del Excel "
         "y se ordenan por año para construir rezagos. El PIB se utiliza como la variación indicada por el usuario; "
         "no se convierte en brecha de producto ni se reemplaza por otra serie. La interpretación depende de esa definición "
         "y de la comparabilidad histórica de la tabla. No se ha realizado una conciliación con las fuentes estadísticas originales."),
        ("p", NOTA_2026 + " La estimación histórica utiliza 1998–2025, con 1997 como primer rezago. "
         "La extensión a 2026 se presenta como sensibilidad. La diferencia entre el IPC de julio de 2026 y el dato anual "
         "de 2025 mezcla cortes: no equivale a una aceleración entre dos años calendario ni entre dos cortes julio–julio homogéneos."),
        ("h", "La evidencia y su incertidumbre"),
        ("p", f"La ecuación histórica restringida es Δπₜ = {numero(beta)}(uₜ − 8,25), con n={int(h.nobs)}. "
         f"Su p-valor HAC es {numero(h.pvalues['brecha_desempleo'])} y el intervalo al 95% va de "
         f"{numero(ci.iloc[0])} a {numero(ci.iloc[1])}. {evidencia} Un punto porcentual adicional de desempleo "
         f"se asocia en esta ecuación con {numero(beta)} puntos de cambio en la inflación; no es un efecto causal estimado."),
        ("p", f"Al incluir el corte de 2026, la pendiente pasa a {numero(s.params['brecha_desempleo'])}, "
         f"con n={int(s.nobs)} y p HAC={numero(s.pvalues['brecha_desempleo'])}. Esa comparación permite conocer "
         "la sensibilidad numérica de la conclusión, pero no resuelve la diferencia de cobertura. Los errores HAC "
         "incluyen corrección de muestra y referencia t; con menos de treinta observaciones siguen siendo aproximados."),
        ("h", "Actividad persistencia y episodios"),
        ("p", f"En la ecuación πₜ = α + ρπₜ₋₁ + b(uₜ − 8,25) + γPIBₜ + εₜ, la muestra histórica entrega "
         f"ρ={numero(p.params['ipc_rezago_1'])}, b={numero(p.params['brecha_desempleo'])} y "
         f"γ={numero(p.params['pib_anual'])} (p del PIB={numero(p.pvalues['pib_anual'])}). "
         "El PIB puede recoger parte de las condiciones de demanda, pero su crecimiento no mide directamente la capacidad ociosa. "
         "Oferta, tipo de cambio y expectativas omitidas pueden mover simultáneamente actividad, empleo y precios. "
         "Agregar PIB no elimina la simultaneidad ni identifica un mecanismo causal."),
        ("p", f"Las pendientes restringidas por ventanas son {ventanas}. Al excluir una observación por vez, "
         f"la pendiente histórica varía entre {numero(inf.beta.min())} y {numero(inf.beta.max())}. "
         "Estas diferencias describen sensibilidad a la muestra, no prueban por sí solas quiebres estructurales. "
         "Los cortes se fijan de antemano y la ventana 2020–2023 se retira sólo como contraste de influencia; "
         "sus observaciones permanecen en la estimación principal. También se publican variantes de la referencia "
         "de desempleo entre 8,0% y 8,5% y de los rezagos HAC entre cero y dos."),
        ("h", "La dimensión social del ajuste"),
        ("p", "La inflación afecta el bienestar por el costo de la canasta, la evolución de los ingresos y las posiciones "
         "de ahorro y deuda. El FMI documenta estos canales y su heterogeneidad entre hogares [2]. Para Chile, esta tabla "
         "agregada no permite medir qué grupos pierden más ni calcular pobreza o salarios reales. La implicación es "
         "examinar la distribución de costos antes de trasladar un promedio macroeconómico a la experiencia de las familias."),
        ("p", "El desempleo reduce ingresos laborales y puede interrumpir trayectorias de experiencia y aprendizaje. "
         "La evidencia internacional del FMI vincula empleo juvenil y desigualdad [3]; no constituye una estimación "
         "para los jóvenes chilenos de esta muestra. Un análisis social más completo requeriría participación laboral, "
         "duración del desempleo, informalidad y desagregaciones por sexo, edad y territorio. Una tasa agregada similar "
         "puede coexistir con situaciones familiares muy distintas."),
        ("p", "La evaluación de políticas debe considerar conjuntamente estabilidad de precios y oportunidades de empleo. "
         "Como criterio económico, apoyos focalizados a hogares vulnerables pueden acompañar la estabilización; "
         "formación, intermediación laboral y servicios de cuidado pueden reducir barreras de acceso al trabajo. "
         "Esta base no identifica cuánto mejoraría cada medida ni autoriza a calcular cuántos empleos habría que "
         "sacrificar para reducir la inflación. Tampoco permite ordenar esas políticas por rentabilidad social."),
        ("h", "Cómo leer el corte de 2026"),
        ("p", f"La fila de 2026 informa desempleo de {numero(dato.desocupacion, 2)}%, IPC de "
         f"{numero(dato.ipc_anual, 1)}% y PIB de {numero(dato.pib_anual, 1)}%, bajo la convención julio–julio "
         "declarada para esta entrega. Es una observación útil para contextualizar el presente, pero no debe "
         "presentarse como cierre anual, pronóstico ni prueba de un nuevo régimen económico."),
        ("h", "Conclusión para el debate público"),
        ("p", "La curva de Phillips aporta una pregunta relevante sobre inflación y holgura laboral, pero exige "
         "explicitar expectativas, restricciones y diferencias de medición. Las estimaciones y sus intervalos "
         "deben leerse junto con las sensibilidades publicadas. La discusión social gana precisión cuando se "
         "reconocen los costos del desempleo y de la inflación sin convertir una asociación histórica en una "
         "receta automática de política económica."),
        ("h", "Referencias"),
        *[("p", f"[{i}] {title}. {url}") for i, (title, url) in enumerate(REFERENCIAS, 1)],
    ]
