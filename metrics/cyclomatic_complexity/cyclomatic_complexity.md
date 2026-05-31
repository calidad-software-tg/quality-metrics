# C05 – Cyclomatic Complexity (McCabe Complexity)

## 1. Descripción

Mide el número de caminos de ejecución independientes en una unidad de código (método o función). Es un predictor indirecto de calidad: a mayor complejidad ciclomática, mayor dificultad para comprender, testear y mantener el código. Fue propuesta originalmente por Thomas McCabe en 1976.

> ⚠️ **Aplicabilidad al repositorio analizado**
>
> tldr-pages es un repositorio de documentación pura (archivos `.md`). No contiene código fuente procesable por herramientas de análisis estático. **Esta métrica no es aplicable a tldr-pages.** Aplica a repositorios con lógica de programa real (Python, Java, C/C++, JavaScript, etc.).

---

## 2. Clasificación por dimensiones (3P)

| Dimensión | Clasificación Original | Clasificación en Encuesta |
|-----------|------------------------|------------------------------------|
| **Producto** |  Sí |  Sí |
| **Persona** |  No |  Sí |
| **Proceso** |  No |  No |

**Clasificación original:** MCC es una métrica de Producto. Mide un atributo intrínseco del artefacto de software, independientemente de quién lo produjo.

**Clasificación en encuesta:** Al transformarse en el ítem *"La calidad percibida en el código desarrollado"* (C05), la métrica adquiere también la dimensión Persona, ya que la pregunta interpela al contributor sobre su propia producción. El MCC calculado sobre los commits de un autor específico permite evaluar el impacto individual de ese contributor en la complejidad del código.

---

## 3. Fórmula de cálculo

```
MCC = E − N + 2P
```

Donde:
- **E** = número de aristas (edges) en el grafo de flujo de control del método
- **N** = número de nodos en el grafo de flujo de control del método
- **P** = número de componentes conexos (para un único método, P = 1)

**Forma equivalente y práctica** (más usada en herramientas):

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

> **Nota: deducción de la equivalencia** (McCabe, 1976)
>
> En el grafo de flujo de control, cada nodo secuencial tiene 1 arista de salida, mientras que cada *predicate node* (decision point) tiene 2 (rama verdadera y falsa). Sea **D** el número de decision points:
>
> ```
> E = N + D
> ```
>
> Sustituyendo en la fórmula original con P = 1:
>
> ```
> MCC = E − N + 2 = (N + D) − N + 2 = D + 2
> ```
>
> El resultado correcto es **D + 1** porque la fórmula de McCabe usa el grafo *augmentado*, donde se agrega una arista del nodo de salida al de entrada, reduciendo el resultado en 1. Así: **MCC = D + 1**.
>
> El **+1** corresponde al camino base: el recorrido directo sin activar ninguna bifurcación.
>
> *Fuente: McCabe (1976), op. cit.*

---

## 4. Variables necesarias y unidades

| Variable | Descripción | Unidad |
|----------|-------------|--------|
| `D` | Número de decision points en el método | entero ≥ 0 |
| `MCC` | Complejidad ciclomática resultante | entero ≥ 1 |

La métrica se calcula **por método**. El valor mínimo posible es 1 (método sin bifurcaciones).

---

## 5. Fuente de datos en el historial Git

MCC requiere acceso al **código fuente**, no solo a los metadatos Git. La extracción se realiza combinando PyDriller (iteración sobre commits) con `lizard` (análisis estático multi-lenguaje).

**Flujo de extracción por commit:**

```
git log (commits)
    └─► commit.modified_files
            └─► modified_file.changed_methods   ← funciones que cambiaron
                    └─► method.complexity        ← MCC antes y después
                            └─► registrar: (hash, autor, fecha, archivo, método, MCC)
```

**Para análisis por autor:** agrupar las funciones modificadas por autor en cada commit y promediar su MCC.

---

## 6. Granularidad temporal

| Nivel | Descripción |
|-------|-------------|
| **Por commit** | Una observación por commit que modifica archivos fuente |
| **Por autor** | Promedio de MCC de las funciones modificadas por cada contributor |
| **Por release/tag** | Una observación por versión etiquetada |

La granularidad primaria es **método × commit**, consistente con de Bassi et al. (2018).

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

**C05 – "La calidad percibida en el código desarrollado"**

MCC operacionaliza este ítem en dos niveles:

| Nivel | Cómo MCC operacionaliza C05 |
|-------|----------------------------|
| **Producto** | MCC promedio/máximo del repositorio mide objetivamente la complejidad estructural del código producido. |
| **Persona** | MCC calculado por contributor permite comparar la percepción subjetiva de calidad con la complejidad objetiva introducida por cada desarrollador. |

---

## 10. Referencias

- McCabe, T. (1976). *A Complexity Measure*. IEEE Transactions on Software Engineering, SE-2(4), 308–320.
- de Bassi, P. R., Wanderley, G. M. P., Banali, P. H., & Paraiso, E. C. (2018). Measuring Developers' Contribution in Source Code using Quality Metrics. *2018 IEEE 22nd International Conference on Computer Supported Cooperative Work in Design (CSCWD)*, 39–44. https://doi.org/10.1109/CSCWD.2018.8465320
- Radon documentation: https://radon.readthedocs.io/en/latest/commandline.html