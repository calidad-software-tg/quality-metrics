# C51 – Schedule Compliance 

---

## 1. Descripción

La métrica **Schedule Compliance / Schedule Variance** cuantifica el grado de desvío entre el avance planificado y el avance real de un proyecto de software en términos de tiempo, dentro de la dimensión de gestión de proyectos.

> "Las métricas de nivel de gestión de proyectos más utilizadas son la varianza del esfuerzo, la productividad, COCOMO, la variación de programación, el índice de rendimiento de la programación (SPI), earned Análisis de Valor (EVA)..." [21]

No tiene formula explicita en el paper, la fórmula que sigue proviene del estándar de referencia que el paper cita indirectamente (PMBOK / Earned Value Management).

---

## 2. Clasificación – Dimensiones 3P

| Dimensión | Clasificación Original ISL | Clasificación en Encuesta |
|-----------|---------------------------|---------------------------|
| **Proceso** | Sí | Sí |
| **Persona** | No | No |
| **Producto** | No | No |

---

## 3. Fórmula de cálculo

La fórmula estándar de Earned Value Management (EVM), a la que remite el nombre "Schedule Variance", es:

$$SV = EV - PV$$

Donde:
- **EV (Earned Value)**: valor ganado — costo presupuestado del trabajo realmente completado
- **PV (Planned Value)**: valor planificado — costo presupuestado del trabajo que debía completarse según el cronograma

Su índice asociado, **SPI (Schedule Performance Index)** — mencionado explícitamente en el paper —, se calcula como:

$$SPI = \frac{EV}{PV}$$

Interpretación:
- **SV > 0 / SPI > 1**: el proyecto está adelantado respecto al cronograma
- **SV = 0 / SPI = 1**: el proyecto está exactamente a tiempo
- **SV < 0 / SPI < 1**: el proyecto está atrasado respecto al cronograma

---

## 4. Variables necesarias y unidades

| Variable | Descripción | Unidad | Origen |
|---|---|---|---|
| `PV` | Valor planificado del trabajo programado a una fecha de corte | moneda (o esfuerzo) | Línea base del cronograma / plan del proyecto |
| `EV` | Valor del trabajo realmente completado a esa fecha | moneda (o esfuerzo) | Reporte de avance / seguimiento de tareas |
| `SV` | Diferencia EV − PV | moneda (o esfuerzo) | Calculado |
| `SPI` | Cociente EV / PV | ratio adimensional | Calculado |

---

## 5. Fuente de datos

En la práctica suele obtenerse de herramientas de gestión de proyectos (Jira, MS Project, Azure DevOps) que registran fechas planificadas vs. reales de tareas/hitos, o de reportes EVM si el proyecto lleva ese control.

---

## 6. Granularidad temporal

| Granularidad | Descripción |
|--------------|-------------|
| **Por hito/entregable** | Medición puntual en cada fecha de entrega comprometida. |
| **Acumulativa** | SV/SPI calculado sobre el total del proyecto hasta la fecha de corte actual. |
| **Por release/sprint** | En contextos ágiles, recalcular por iteración en lugar de por hito tradicional. |

---

## 7. Rangos de interpretación


| Rango SPI | Interpretación |
|---|---|
| **> 1.05** | Adelantado significativamente |
| **0.95 – 1.05** | Dentro de tolerancia (a tiempo) |
| **0.80 – 0.94** | Atraso moderado, requiere atención |
| **< 0.80** | Atraso crítico |

---

## 8. Relación con el ítem de encuesta

> **El cumplimiento de plazos de entrega**

La relación es **directa**: Schedule Compliance/Variance es la contraparte objetiva y cuantitativa de esa percepción. Se consideraron dos métricas canónicas justificadas (Schedule Compliance y Schedule Variance) porque ambas representan explícitamente el concepto de cumplimiento temporal — una como etiqueta general (¿se cumplió o no?) y la otra como el cálculo cuantitativo del desvío.

---

## 9. Referencias

- Colakoglu, F. N., Yazici, A., & Mishra, A. (2021). Software Product Quality Metrics: A Systematic Mapping Study. *IEEE Access*, 9, 44647–44675. https://doi.org/10.1109/ACCESS.2021.3054730
- Project Management Institute (PMI). (2017). *A Guide to the Project Management Body of Knowledge (PMBOK Guide)*. Newtown Square, PA, USA.