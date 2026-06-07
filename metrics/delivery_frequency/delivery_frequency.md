# Frecuencia de Entregas Exitosas (Commit Frequency)

## 1. Descripción

La métrica **Commit Frequency** mide la frecuencia con la que se incorporan cambios al repositorio mediante commits realizados durante un período determinado. En el catálogo ISL no se identificó una métrica explícita denominada *Deployment Frequency*, *Release Frequency* o *Successful Delivery Frequency*. Por este motivo, se seleccionó **Commit Frequency** como la métrica más cercana disponible.

La hipótesis subyacente es que una mayor frecuencia de incorporación de cambios refleja un flujo continuo de trabajo y una capacidad sostenida de entrega. Sin embargo, debe destacarse que un commit individual no equivale necesariamente a una entrega exitosa, por lo que la correspondencia con el constructo original es parcial.

En el contexto de esta investigación, la métrica se utiliza como un **proxy de frecuencia de entregas exitosas**.

---

## 2. Clasificación – Dimensiones 3P

| Dimensión | Clasificación |
| --------- | ------------- |
| Proceso   | Sí            |
| Producto  | Sí            |
| Persona   | No            |

Ítem de encuesta asociado:

**"Frecuencia de entregas exitosas"**

---

## 3. Fórmula de cálculo

[
CommitFrequency = \frac{TotalCommits}{Periodo}
]

Donde:

* `TotalCommits`: cantidad de commits realizados durante el período analizado.
* `Periodo`: unidad temporal elegida (día, semana, mes o año).

Resultado:

Cantidad de commits por unidad de tiempo.

---

## 4. Variables necesarias

| Variable         | Descripción                  | Unidad          |
| ---------------- | ---------------------------- | --------------- |
| commits          | Número total de commits      | Cantidad        |
| periodo          | Intervalo temporal analizado | Tiempo          |
| commit_frequency | Frecuencia resultante        | Commits/periodo |

---

## 5. Fuente de datos

GitHub REST API.

Endpoint principal:

```text
GET /repos/{owner}/{repo}/commits
```

Datos utilizados:

* SHA del commit
* fecha
* autor

---

## 6. Implementación

Ejemplo simplificado:

```python
commit_frequency = total_commits / period_length
```

Ejemplo mensual:

```python
commit_frequency = commits_mes / 30
```

---

## 7. Interpretación

Valores altos indican:

* incorporación frecuente de cambios;
* actividad sostenida de desarrollo;
* flujo continuo de contribuciones.

Valores bajos indican:

* menor ritmo de incorporación de cambios;
* períodos de mantenimiento o baja actividad.

No existen umbrales universales, ya que dependen del tamaño y naturaleza del proyecto.

---

## 8. Calculabilidad en tldr-pages/tldr

**Calculable.**

Todos los commits del repositorio son accesibles mediante la API de GitHub.

La extracción requiere:

1. Obtener el historial de commits.
2. Filtrar por período temporal.
3. Contabilizar commits.
4. Calcular la frecuencia correspondiente.

La complejidad de implementación es baja.

---

## 9. Observaciones

La correspondencia entre **Commit Frequency** y **Frecuencia de Entregas Exitosas** es parcial.

Un commit representa una incorporación de cambios al repositorio, pero no necesariamente una entrega exitosa al usuario final. En repositorios colaborativos como tldr-pages, una entrega podría estar representada más fielmente por un Pull Request aprobado y mergeado o por una release oficial.

Sin embargo, debido a la ausencia de una métrica explícita de *Delivery Frequency* en el catálogo utilizado, **Commit Frequency** se adopta como el proxy más cercano disponible.

Además, tldr-pages posee un número reducido de releases oficiales, por lo que la frecuencia de releases no resulta suficientemente representativa para el análisis temporal del proyecto.

---

## 10. Relación con el ítem de encuesta

La relación con el ítem:

> "Frecuencia de entregas exitosas"

es **parcial**.

La métrica captura la frecuencia con la que se integran cambios al repositorio, pero no permite verificar automáticamente si dichos cambios constituyen entregas exitosas, despliegues efectivos o releases formales.

Por esta razón debe interpretarse como una aproximación indirecta al constructo original.

---

## 11. Nivel de confianza

**Medio**

* Calculabilidad: Alta.
* Disponibilidad de datos: Alta.
* Correspondencia conceptual: Media.
* Fidelidad operacional: Media-baja.

---

## 12. Referencia

Catálogo ISL – Commit Frequency.
