# M05 – Cyclomatic Complexity (McCabe Complexity)

---

## 1. Descripción

Mide el número de caminos de ejecución independientes en una unidad de código (método o función). Es un predictor indirecto de calidad: a mayor complejidad ciclomática, mayor dificultad para comprender, testear y mantener el código. Fue propuesta originalmente por Thomas McCabe en 1976.

> ⚠️ **Aplicabilidad al repositorio analizado**
>
> tldr-pages es un repositorio de documentación pura (archivos `.md`). No contiene código fuente procesable por herramientas de análisis estático. **Esta métrica no es aplicable a tldr-pages.** Aplica a repositorios con lógica de programa real (Python, Java, C/C++, JavaScript, etc.).

---

## 2. Clasificación – Dimensiones 3P

| Dimensión | Clasificación Original ISL | Clasificación en Encuesta |
|-----------|---------------------------|---------------------------|
| **Producto** | Sí | Sí |
| **Persona** | No | Sí |
| **Proceso** | No | No |

**Clasificación original:** MCC es una métrica de Producto. Mide un atributo intrínseco del artefacto de software, independientemente de quién lo produjo.

**Clasificación en encuesta:** Al transformarse en el ítem *"La calidad percibida en el código desarrollado"* (C05), adquiere también la dimensión Persona, ya que la pregunta interpela al contributor sobre su propia producción.

Ítem de encuesta asociado: **C05 – La calidad percibida en el código desarrollado**.

---

## 3. Fórmula de cálculo

```
MCC = E − N + 2P
```

Donde:
- **E** = número de aristas en el grafo de flujo de control del método
- **N** = número de nodos en el grafo de flujo de control del método
- **P** = número de componentes conexos (para un único método, P = 1)

**Forma equivalente y práctica:**

```
MCC = número de decision points + 1
```

Un *decision point* es toda sentencia que introduce una bifurcación en el flujo de ejecución:

| Sentencia | Cuenta como decision point |
|-----------|---------------------------|
| `if` / `elif` | +1 |
| `for` | +1 |
| `while` | +1 |
| `except` / `catch` | +1 |
| `case` (en `match`) | +1 por rama |
| Operador `and` / `or` en condición | +1 cada uno |

### Implementación Python

Combina PyDriller (iteración sobre commits) con `lizard` (análisis estático multi-lenguaje). Por cada commit se iteran los archivos modificados, se extraen los métodos que cambiaron y se registra su MCC.

---

## 4. Variables necesarias y unidades

| Variable | Descripción | Unidad | Origen |
|----------|-------------|--------|--------|
| `D` | Número de decision points en el método | entero ≥ 0 | Análisis estático (`lizard`) |
| `MCC` | Complejidad ciclomática resultante | entero ≥ 1 | Calculado |

La métrica se calcula **por método**. Valor mínimo posible: 1 (método sin bifurcaciones).

---

## 5. Fuente de datos en el historial Git

MCC requiere acceso al **código fuente**, no solo a metadatos Git. La extracción combina PyDriller con `lizard`.

**Flujo de extracción por commit:**

```
git log (commits)
    └─► commit.modified_files
            └─► modified_file.changed_methods   ← funciones que cambiaron
                    └─► method.complexity        ← MCC antes y después
                            └─► registrar: (hash, autor, fecha, archivo, método, MCC)
```

Para análisis por autor: agrupar las funciones modificadas por autor en cada commit y promediar su MCC.

---

## 6. Granularidad temporal

| Granularidad | Descripción |
|--------------|-------------|
| **Por commit** | Una observación por commit que modifica archivos fuente. **Granularidad primaria.** |
| **Por autor** | Promedio de MCC de las funciones modificadas por cada contributor. |
| **Por release** | Una observación por versión etiquetada. |

---

## 7. Rangos de interpretación

Según Anderson (2004), citado en de Bassi et al. (2018):

| Rango MCC | Nivel | Riesgo |
|-----------|-------|--------|
| 1 – 10 | Baja | Bajo |
| 11 – 20 | Moderada | Moderado |
| 21 – 50 | Alta | Alto |
| > 50 | Muy alta | Muy alto |

---

## 8. Ejemplo de cálculo

```python
def clasificar_archivo(extension, tamanio):
    if extension == ".md":        # +1
        if tamanio > 1000:        # +1
            return "md_grande"
        else:
            return "md_chico"
    elif extension == ".py":      # +1
        return "script"
    else:
        return "otro"
```

**Decision points:** 3 → **MCC = 3 + 1 = 4** → complejidad baja.

---

## 9. Relación con el ítem de encuesta

> **C05 – La calidad percibida en el código desarrollado**

MCC operacionaliza este ítem en dos niveles: como métrica de **Producto**, el MCC promedio/máximo del repositorio mide objetivamente la complejidad estructural del código producido; como métrica de **Persona**, calculado por contributor permite evaluar el impacto individual de cada desarrollador en la complejidad del código.

---

## 10. Referencias

- McCabe, T. (1976). A Complexity Measure. *IEEE Transactions on Software Engineering*, SE-2(4), 308–320.
- de Bassi, P. R., Wanderley, G. M. P., Banali, P. H., & Paraiso, E. C. (2018). Measuring Developers' Contribution in Source Code using Quality Metrics. *2018 IEEE 22nd International Conference on Computer Supported Cooperative Work in Design (CSCWD)*, 39–44. https://doi.org/10.1109/CSCWD.2018.8465320
- Radon documentation: https://radon.readthedocs.io/en/latest/commandline.html
- Alonso, E. J., & Robiolo, G. (2022b, octubre). Determinación de la calidad de producto, persona y proceso en entornos de desarrollo con GitHub: un estudio sistemático de la literatura [ponencia]. Simposio Argentino de Ingeniería de Software (ASSE 2022), JAIIO 51, Universidad Abierta Interamericana, Buenos Aires, Argentina.