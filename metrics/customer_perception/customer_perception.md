# C44 – Customer Perception 

---

## 1. Descripción

La métrica **Customer Perception** es identificada en el estudio de Colakoglu, Yazici y Mishra (2021) — *"Software Product Quality Metrics: A Systematic Mapping Study"* — como una métrica de **nivel de sistema**, dentro del conjunto de métricas orientadas a capturar la calidad percibida del producto de software una vez entregado al usuario final.

El paper la menciona explícitamente en dos lugares:

1. Como parte del listado de métricas de nivel de sistema más utilizadas en los 70 artículos analizados:

   > "El nivel de sistema más utilizado, que consiste en un software más, las métricas del producto son las siguientes: Defectos y regresiones encontrados por el cliente, **Cálculo de la percepción del cliente**, MTTF (Tiempo medio de falla), MTTR (Tiempo medio de reparación), MTBF (Tiempo medio entre fallas), ROCOF (Tasa de ocurrencias de fallas) y POFOD (Probabilidad de falla en las demandas)."

2. Como ejemplo conceptual del atributo de calidad **Satisfacción** dentro del modelo **QinU (Calidad en Uso)** de ISO/IEC 25010:

   > "La satisfacción del producto del cliente y las tendencias de percepción son el ejemplo del atributo de calidad de satisfacción de QinU."

**Importante:** este paper es un *Mapeo Sistemático (SM)*, no un estudio empírico primario. Su objetivo es catalogar qué métricas se usan en la literatura, no detallar su implementación matemática. Por lo tanto, **el paper no reporta una fórmula de cálculo** para esta métrica; solo confirma su existencia, su nivel (sistema) y su vínculo con el atributo de calidad Satisfacción de QinU.

---

## 2. Clasificación – Dimensiones 3P

| Dimensión | Clasificación Original ISL | Clasificación en Encuesta |
|-----------|---------------------------|---------------------------|
| **Proceso** | No | No |
| **Persona** | No | No |
| **Producto** | Sí | Sí |
\
---

## 3. Fórmula de cálculo

**No disponible en el paper fuente.**

El artículo no provee una expresión matemática, rango de entrada/salida, ni procedimiento de cómputo para esta métrica. Solo se la nombra como parte de un listado de métricas de nivel de sistema recopiladas de la literatura (2009–2019).

A modo orientativo — y **no como dato extraído del paper**, sino como práctica común en la industria para "percepción del cliente" — este tipo de métrica suele operacionalizarse mediante:
- Encuestas de satisfacción post-entrega (escalas Likert).
- Net Promoter Score (NPS).
- Tasa de reviews/comentarios positivos vs. negativos sobre el producto.

Cualquiera de estas aproximaciones sería una interpretación externa al paper, no una fórmula validada por el estudio de Colakoglu et al. (2021).

---

## 4. Variables necesarias y unidades

No aplica — al no existir fórmula en el paper fuente, no hay variables definidas ni unidades asociadas.

---

## 5. Fuente de datos

No especificada en el paper. En el Informe Mundial de Calidad 2018-2019 citado en la introducción del artículo se menciona que "la satisfacción del usuario final es solo de alrededor del 40%", lo que sugiere que este tipo de dato suele obtenerse de encuestas de satisfacción de usuario final, pero el paper no vincula esta cifra directamente con la métrica "Cálculo de la percepción del cliente".

---

## 6. Granularidad temporal

No especificada en el paper.

---

## 7. Rangos de interpretación

No existen umbrales ni rangos formales reportados en el paper para esta métrica.

---

## 8. Ejemplo de cálculo

No disponible — el paper no incluye un caso de aplicación numérico para esta métrica.

---

## 9. Relación con el ítem de encuesta

> **[Completar según el ítem de encuesta correspondiente, ej.: "Satisfacción percibida del cliente/usuario final con el producto"]**

La relación es **directa y conceptual**: esta métrica es, según el propio paper, la contraparte cuantitativa del atributo de calidad **Satisfacción** de QinU (ISO 25010), que mide precisamente la percepción y las tendencias de satisfacción del cliente respecto al producto de software. A diferencia de M14 (Developer Quality), aquí no hay una fórmula objetiva basada en datos de repositorio; la métrica depende inherentemente de instrumentos de recolección subjetiva (encuestas, feedback) por su propia naturaleza.

---

## 10. Limitaciones identificadas

- El paper no ofrece fórmula, unidades, ni procedimiento de cálculo.
- No se identifica el estudio primario (S1–S70) específico del cual se extrajo esta métrica.
- Al ser una métrica de percepción, es intrínsecamente subjetiva y depende del instrumento de medición elegido (encuesta, NPS, análisis de sentimiento sobre reviews, etc.), lo cual el paper no discute.
- El propio artículo señala, en su sección de limitaciones (RQ3), que faltan métricas de calidad relacionadas con atributos "blandos" como cultura, actitud y punto de vista — una carencia que también podría aplicar a la falta de rigor operacional en métricas de percepción como esta.

---

## 11. Referencias

- Colakoglu, F. N., Yazici, A., & Mishra, A. (2021). Software Product Quality Metrics: A Systematic Mapping Study. *IEEE Access*, 9, 44647–44675. https://doi.org/10.1109/ACCESS.2021.3054730