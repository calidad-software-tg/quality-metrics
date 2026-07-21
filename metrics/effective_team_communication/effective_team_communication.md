# Developer Communication / Communication Activity

## Consigna
**58 — "La comunicación efectiva entre los desarrolladores de su equipo"**
Registro 30 (Developer Communication / Communication Activity), Orden ISL 68.

## Métrica
- **Clasificación 3P:** Proceso / Persona.
- **Evidencia histórica:** Explícita — **Relación conceptual:** Directa.
- **Inferencia:** Inferida — **Fidelidad:** Baja.

## Qué mide (y cómo se diferencia de las métricas hermanas)
Mide la **actividad comunicacional dirigida y técnica** entre desarrolladores
—quién coordina con quién— y **su sostenimiento en el tiempo**, no el volumen
bruto de mensajes. Sigue la ficha de Registro 30, que enfatiza menciones,
coordinación técnica, **diferenciación entre comunicación técnica y no técnica** y
granularidad temporal.

| Métrica | Insumo | Qué responde |
|---|---|---|
| c.9 `social_interaction` | issue_comments + pr_comments + pr_reviews | **cuánto** se habla (volumen total + por dev, no dirigido) |
| c.10 `developer_skill_communication` | tamaño de mensajes de commit (git log) | **qué tan rico** documenta cada dev sus cambios |
| **c.58 (esta)** | **grafo dirigido de menciones/respuestas técnicas + tiempo** | **qué tan coordinado, técnico y sostenido** es el diálogo |

> No re-cuenta comentarios como la c.9: los transforma en un **grafo dirigido**
> (emisor → receptor), filtra la comunicación **técnica** de la cortesía, y agrega
> una **serie temporal**. Distinto objeto de medición.

## Construcción del grafo dirigido
Para cada comentario (de issue, de conversación de PR o inline de PR) se crean
aristas `emisor → receptor` cuando:
- **(a) respuesta:** el emisor comenta en un hilo abierto por otra persona, o
- **(b) mención:** el emisor menciona `@otro-desarrollador` en el cuerpo.

Sólo se cuentan menciones a **desarrolladores conocidos** del proyecto (que
participan en algún hilo), no cualquier `@string`. Se excluyen bots y
auto-interacciones. Con `solo_tecnicas=True` (por defecto), el grafo y la serie
temporal se construyen **solo con interacciones técnicas** (ver clasificador).

## Clasificador técnico vs. no técnico
La ficha pide diferenciar comunicación técnica de la no técnica. El criterio se
derivó de un **escaneo exploratorio real** de los comentarios de tldr-pages (ver
`scan_comentarios.py`), que mostró mucho ruido social (`thanks`, `lgtm`,
`nice one`, `merged`, emojis…). La función `es_tecnico(body)` decide en dos capas:

1. **Estructura (señal fuerte):** si el comentario tiene backtick, bloque de
   código, flag CLI (`--foo`), ruta de archivo o URL → **técnico**.
2. **Léxico:** si no hay estructura, se quitan las frases/palabras de cortesía
   (léxico obtenido del escaneo) y se mide el **contenido sustantivo** restante.
   Poco contenido + marcas de cortesía → **no técnico**; prosa con contenido real
   (aunque abra con "thanks") → **técnico**.

El léxico (`_CORTESIA_1`, `_CORTESIA_FRASE`, `_STOP`) está expuesto al inicio del
módulo y es **ajustable**: mover términos entre listas recalibra el criterio sin
tocar la lógica. Validado contra frases reales de la muestra (32/32 en el set de
prueba). Es una heurística, no un modelo: el gris son comentarios largos de charla
no técnica sin palabras clave (poco frecuentes).

## Indicadores
- **densidad_coordinacion** = pares que se comunican / pares posibles → cuán
  distribuida está la coordinación (vs. concentrada en pocos).
- **reciprocidad** = fracción de pares `A→B` que además tienen `B→A` → diálogo de
  ida y vuelta, no monólogo.
- **meses_activos** y **actividad_por_mes_activo** → ritmo de la comunicación.
- **consistencia_temporal** = meses con actividad / meses del período total →
  sostenida (≈1) vs. esporádica (≈0).
- **ratio_tecnico** = interacciones técnicas / interacciones dirigidas totales →
  qué parte del diálogo dirigido es técnica vs. social (señal de calidad).
- `interacciones_dirigidas_total`, `interacciones_dirigidas_tecnicas`,
  `pares_coordinados`, `desarrolladores_involucrados`, `base_grafo` como contexto.

## Fuente de datos
GitHub API (REST) sobre `tldr-pages/tldr`, vía `GitHubExtractor.get_paginated`:
`issues?state=all` (autoría de hilos), `issues/comments` y `pulls/comments`
(cuerpo, autor y fecha de cada comentario).

## Interpretación
Densidad y reciprocidad altas ⇒ equipo que se coordina de forma distribuida y
recíproca. Consistencia temporal alta ⇒ comunicación sostenida. `ratio_tecnico`
alto ⇒ el diálogo es mayormente técnico; bajo ⇒ predomina la cortesía/coordinación
social. Valores bajos de densidad ⇒ coordinación concentrada en pocos pares.

## Limitaciones y fidelidad
- **Fidelidad Baja / Inferida:** estructura, ritmo y clasificación técnica son
  proxy de efectividad; no se evalúa si la coordinación resolvió algo.
- **Clasificador heurístico:** basado en léxico observado, no en un modelo; casos
  límite (charla larga no técnica sin keywords) pueden colarse como técnicos.
- **Sesgo del dataset:** en tldr-pages predominan interacciones sobre
  correcciones/traducciones de páginas; las menciones pueden ser escasas, lo que
  en sí mismo es un hallazgo (baja coordinación dirigida).
- **`limite`** acota la descarga por canal para pruebas; usar `limite=None` para el
  valor definitivo (si no, faltan autores de hilo y se descartan interacciones).

## Relación con otras métricas
Complementa —sin duplicar— a `social_interaction` (volumen, c.9) y a
`developer_skill_communication` (mensajes de commit, c.10). Las tres pueden
compartir la extracción de comentarios, pero cada una calcula un objeto distinto.
El clasificador `es_tecnico` es reutilizable por otras métricas de comunicación.

## Archivos del módulo
- **`effective_team_communication.py`** — la métrica (`DeveloperCommunicationActivity`)
  y el clasificador `es_tecnico`.
- **`scan_comentarios.py`** — script exploratorio (no calcula la métrica) usado
  para derivar y validar el criterio técnico/no técnico. Ver abajo.
- **`effective_team_communication.md`** — este documento.

## Referencia
Ficha ISL Registro 30 (Developer Communication / Communication Activity), catálogo
JAIIO 2022. Constructo asociado: Developer Skill Communication (Salamea & Farré, 2019).

---

# Anexo — `scan_comentarios.py` (escaneo exploratorio)

## Propósito
Herramienta de **exploración previa**, no de cálculo. Sirvió para responder con
datos "¿qué tipos de comentarios hay en tldr-pages y cuánto es ruido no técnico?",
y así definir el léxico del clasificador `es_tecnico` en vez de inventarlo.

## Qué hace
1. Baja una **muestra** de comentarios de `issues/comments` y `pulls/comments`
   (por defecto ~1.500 por canal; ajustable con `PAGINAS_POR_CANAL`).
2. A cada comentario le marca señales observables: longitud, backticks, bloques de
   código, flags CLI, rutas, `#refs`, URLs, menciones, palabras técnicas, y si es
   cortesía pura. Con eso arma una clasificación heurística tentativa.
3. Exporta cuatro CSV para mirar en Excel y decidir el criterio.

## Robustez (por qué esta versión no se cuelga)
- **Timeout por request** (`TIMEOUT`): corta conexiones trabadas.
- **Reintentos con backoff** ante errores transitorios 502/503/504 y cortes de red.
- **Manejo de rate limit**: espera lo necesario o corta con lo que juntó.
- **Cache en disco** (`scan_out/cache/`): descarga una sola vez; re-correr es
  instantáneo (borrar la carpeta fuerza re-descarga).
- **Tope de páginas real**: no intenta bajar el histórico completo salvo que se
  pida explícitamente.

## Uso
Desde la raíz del proyecto `quality-metrics` (para resolver `config`/`core`):
```
python -m metrics.effective_team_communication.scan_comentarios
```
Toma el token de `config/settings.py`. Perillas al inicio del script:
`PAGINAS_POR_CANAL` (volumen de la muestra) y `TIMEOUT`.

## Salida (`scan_out/`)
- **`resumen.csv`** — foto rápida: totales, humanos vs bots, distribución por
  longitud, conteos por clase heurística y por señal.
- **`top_frases_cortas.csv`** — comentarios cortos más repetidos (revela las
  cortesías dominantes: `thanks`, `lgtm`, `nice one`…).
- **`muestra_por_grupo.csv`** — muestra aleatoria por grupo (técnico / no técnico /
  ambiguo) para validar a ojo.
- **`comentarios_features.csv`** — un registro por comentario con todas las señales,
  para pivotear en Excel.

## Hallazgos del escaneo (muestra de ~3.000 comentarios)
- Fuerte presencia de cortesía/estado (`thanks`, `lgtm`, `done`, `merged`, emojis).
- Las señales de *palabra suelta* (fix, page, example) generan falsos positivos
  técnicos porque aparecen dentro de frases de cortesía.
- Las señales **estructurales** (código, flags, rutas, URLs) son las confiables.
Estos hallazgos son los que definieron el clasificador de dos capas de la métrica.

## Aclaración metodológica
La muestra por defecto toma los comentarios **más antiguos** (la API pagina por
orden de creación). Sirve para *caracterizar tipos*; para estimar *proporciones*
representativas conviene una corrida mayor o muestreo aleatorio.