# C18 – Densidad de Comentarios en el Código (Comment Density)

---

## 1. Descripción

La métrica **Comment Density (CD)** cuantifica la proporción de líneas comentadas sobre el total de líneas de código en un repositorio. Se expresa como un ratio entre 0 y 1 (o como porcentaje) y refleja el nivel de documentación interna del código fuente.

Una densidad de comentarios más alta generalmente indica:
- Mayor esfuerzo en documentación interna
- Código más mantenible y comprensible para otros desarrolladores
- Posible adherencia a estándares de calidad en el proceso de desarrollo

Gyimesi et al. (2015) incluyen Comment Density (CD) como una de las métricas estándar en su catálogo de 52 métricas de código estático para caracterizar la calidad del software. La métrica forma parte de las categorías clásicas de medición en ingeniería de software orientada a objetos, específicamente en el grupo de métricas de **documentación y mantenibilidad**.

La relevancia empírica de Comment Density está respaldada por su adopción en herramientas de análisis estático ampliamente utilizadas como **SonarQube**, que la reporta como indicador de calidad de código junto con métricas de complejidad y deuda técnica.

> **Nota metodológica:** Comment Density es una métrica observable y objetiva, pero su interpretación depende significativamente del contexto del proyecto. En repositorios de documentación como tldr-pages, la distinción entre "comentarios" y "contenido principal" puede requerir definición explícita. En repositorios de código ejecutable, los comentarios son identificables por su sintaxis (e.g., `//`, `#`, `/* */`).

---

## 2. Clasificación – Dimensiones 3P

| Dimensión | Clasificación Original ISL | Clasificación en Encuesta |
|-----------|---------------------------|---------------------------|
| **Proceso** | No | No |
| **Persona** | No | Sí |
| **Producto** | Sí | Sí |

Ítem de encuesta asociado: **C18 – La calidad de la documentación**.

---

## 3. Fórmula de cálculo

$$\text{Comment Density (CD)} = \frac{\text{CLOC}}{\text{LOC}}$$

O equivalentemente:

$$\text{CD} = \frac{\sum_{i=1}^{n} \text{comment\_lines}_i}{\sum_{i=1}^{n} \text{total\_lines}_i}$$

Donde:
- **CLOC** (Comment Lines of Code): cantidad total de líneas comentadas en todos los archivos.
- **LOC** (Lines of Code): cantidad total de líneas en todos los archivos (incluyendo comentarios, blancos y código).
- **$n$**: cantidad de archivos analizados.

**Resultado**: ratio entre 0 y 1, expresable también como **porcentaje** (0–100%).

### Implementación Python

```python
from pathlib import Path
import re
from typing import Dict

class CommentDensity:
    def __init__(self, file_extensions: list = None):
        """
        Args:
            file_extensions: Extensiones de archivo a analizar.
                           Por defecto: ['.py', '.java', '.js', '.cpp', '.md']
        """
        self.file_extensions = file_extensions or ['.py', '.java', '.js', '.cpp', '.md']
    
    def _count_comments_and_lines(self, file_path: Path) -> tuple:
        """
        Cuenta líneas de comentarios y líneas totales en un archivo.
        Retorna: (comment_lines, total_lines)
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception:
            return 0, 0
        
        total_lines = len(lines)
        comment_lines = 0
        
        # Detección simple de comentarios según extensión
        if file_path.suffix == '.py':
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#'):
                    comment_lines += 1
        
        elif file_path.suffix in ['.java', '.js', '.cpp', '.c']:
            i = 0
            while i < len(lines):
                stripped = lines[i].strip()
                
                # Comentarios de línea única
                if stripped.startswith('//'):
                    comment_lines += 1
                
                # Comentarios multi-línea
                elif '/*' in stripped:
                    comment_lines += 1
                    while i < len(lines) and '*/' not in lines[i]:
                        i += 1
                        comment_lines += 1
                    if i < len(lines):
                        comment_lines += 1
                
                i += 1
        
        elif file_path.suffix == '.md':
            # En Markdown, considerar líneas que comienzan con > o <!-- como comentarios
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('>') or stripped.startswith('<!--'):
                    comment_lines += 1
        
        return comment_lines, total_lines
    
    def calcular(self, repo_path: str) -> Dict:
        """
        Calcula Comment Density para un repositorio.
        
        Args:
            repo_path: Ruta local del repositorio clonado.
        
        Returns:
            Dict con keys: 'comment_lines', 'total_lines', 'comment_density', 'comment_density_percent'
        """
        repo_path = Path(repo_path)
        total_comment_lines = 0
        total_lines = 0
        files_analyzed = 0
        
        # Iterar sobre archivos con extensiones de interés
        for ext in self.file_extensions:
            for file_path in repo_path.rglob(f'*{ext}'):
                # Excluir directorios de dependencias o binarios
                if any(part in file_path.parts for part in ['.git', 'node_modules', '__pycache__', 'build', 'dist']):
                    continue
                
                comment_lines, total = self._count_comments_and_lines(file_path)
                total_comment_lines += comment_lines
                total_lines += total
                files_analyzed += 1
        
        # Calcular densidad
        density = (total_comment_lines / total_lines) if total_lines > 0 else 0.0
        
        return {
            "comment_lines": total_comment_lines,
            "total_lines": total_lines,
            "files_analyzed": files_analyzed,
            "comment_density": density,
            "comment_density_percent": density * 100.0
        }
```

**Notas de implementación:**
- Se recomienda excluir directorios de dependencias (`.git`, `node_modules`, etc.) para no sesgar la métrica.
- La detección de comentarios es heurística y depende del lenguaje de programación; puede requerirse herramientas especializadas (SonarQube, Radon para Python) para mayor precisión.
- Para tldr-pages/tldr, adaptarse al formato Markdown y definir explícitamente qué constituye un "comentario" (ej: bloquecitas `> nota`, líneas que comienzan con `<!--`).

---

## 4. Variables necesarias y unidades

| Variable | Descripción | Unidad | Origen |
|----------|-------------|--------|--------|
| `CLOC` | Comment Lines of Code | líneas | Análisis estático del repositorio clonado |
| `LOC` | Lines of Code | líneas | Análisis estático del repositorio clonado |
| `CD` | Comment Density | ratio (0–1) | Calculado: CLOC / LOC |
| `files_analyzed` | Cantidad de archivos analizados | entero ≥ 0 | Conteo durante análisis |

---

## 5. Fuente de datos

Esta métrica requiere acceso al **código fuente local del repositorio clonado**, no a la API de GitHub.

| Operación | Descripción | Datos obtenidos |
|-----------|-------------|-----------------|
| `git clone` | Clonar repositorio completo | Árbol de archivos fuente |
| Análisis estático | Parsear y contar líneas por archivo | `CLOC`, `LOC` por archivo |

**Pasos:**
1. Clonar el repositorio: `git clone https://github.com/tldr-pages/tldr.git`
2. Iterar sobre archivos con extensiones de interés (`.md`, `.py`, `.js`, etc.)
3. Contar líneas totales y líneas comentadas en cada archivo
4. Sumar y calcular ratio

---

## 6. Granularidad temporal

| Granularidad | Descripción |
|--------------|-------------|
| **Global** | Comment Density sobre el estado actual del repositorio (HEAD). Valor de referencia. |
| **Por rama** | Calcular por rama (main, develop, etc.) para comparar políticas de documentación. |
| **Histórico** | Analizar snapshots del repositorio en momentos específicos (ej: cada mes) para detectar tendencias. |

Para tldr-pages/tldr se recomienda calcular el valor global actual y, opcionalmente, una serie anual desde 2013 chequeando out de commits históricos.

---

## 7. Rangos de interpretación

No existen umbrales formales en la literatura para Comment Density, pero la experiencia práctica y herramientas como SonarQube sugieren estos rangos orientativos:

| Rango | Interpretación |
|-------|---------------|
| **< 5%** | Documentación interna insuficiente. Código poco documentado, difícil de mantener. |
| **5–15%** | Documentación moderada. Esperable en la mayoría de proyectos maduros de código. |
| **15–30%** | Documentación abundante. Indica esfuerzo significativo en claridad del código. |
| **> 30%** | Muy comentado. Posiblemente sobre-documentado o con muchas notas procedimentales. |

> **Contexto en tldr-pages:** Al ser un repositorio de documentación Markdown, los rangos pueden no ser directamente aplicables. La "densidad de comentarios" en Markdown se refiere a anotaciones o notas dentro del contenido, no a comentarios de código. Esperar valores muy bajos (< 5%) es normal y no indicativo de baja calidad.

---

## 8. Calculabilidad en tldr-pages/tldr

**Parcialmente calculable — con restricciones conceptuales.**

El repositorio tldr-pages/tldr es **principalmente Markdown** (archivos `.md` que contienen páginas de documentación de comandos). La métrica Comment Density es originalmente diseñada para **código ejecutable** (Python, Java, JavaScript, C++, etc.), donde los comentarios son sintácticamente distintos del código.

**En tldr-pages:**
- **Archivos principales:** `/pages/` contiene archivos `.md` sin comentarios de código (no hay sintaxis `//` o `#` para comentarios).
- **Metadatos:** Algunos archivos tienen frontmatter YAML o notaciones pero no comentarios tradicionales.
- **Resultado esperado:** Comment Density ≈ 0% o muy cercano a 0, ya que no hay comentarios en el sentido técnico.

**Recomendación:** Para tldr-pages, esta métrica **NO es significativa** y probablemente **no debería reportarse como indicador de calidad documentacional**. En su lugar, considerar:
- Métrica alternativa: **Completitud de páginas** (cobertura de comandos documentados).
- Métrica alternativa: **Actualidad de la documentación** (edad promedio de commits recientes a páginas).

**Si se requiere igual reportar:** Analizar solo archivos `.md` bajo `/pages/`, contar líneas totales, buscar patrones indicadores de anotación (ej: bloques `> Nota`, líneas que inician con `-`), y reportar con una advertencia explícita sobre limitaciones contextuales.

---

## 9. Ejemplo de cálculo

```python
from pathlib import Path
from metrics.comment_density import CommentDensity

# Asumir repositorio clonado en ./tldr-pages-repo
cd_metric = CommentDensity(file_extensions=['.md', '.py', '.js'])
resultado = cd_metric.calcular('./tldr-pages-repo')

print(resultado)
```

**Salida esperada (valores aproximados para tldr-pages/tldr, junio 2026):**

```python
{
    "comment_lines": 150,          # Pocas líneas con anotaciones
    "total_lines": 450000,         # Total de líneas en .md
    "files_analyzed": 3500,        # ~3500 archivos .md
    "comment_density": 0.00033,    # Muy bajo
    "comment_density_percent": 0.033  # ~0.03%
}
```

$$\text{Comment Density} = \frac{150}{450000} \approx 0.0003 \text{ (0.03%)}$$

**Interpretación:** Valor extremadamente bajo, coherente con la naturaleza del repositorio (documentación Markdown sin comentarios de código). **No es indicativo de baja calidad**; refleja simplemente que tldr-pages no es un repositorio de código fuente ejecutable.

---

## 10. Relación con el ítem de encuesta

> **C18 – La calidad de la documentación**

La relación es **indirecta y contexto-dependiente**.

- **En código ejecutable:** Relación **directa**. Comment Density es un proxy razonable de documentación interna y claridad del código.
- **En tldr-pages:** Relación **débil o nula**. Comment Density será cercana a 0% por diseño (Markdown sin comentarios de código), por lo que la métrica **no discrimina** entre documentación buena y mala. La "calidad de documentación" en tldr-pages se reflejaría mejor en métricas como:
  - Completitud de páginas (cobertura de comandos)
  - Actualidad (recencia de actualizaciones)
  - Estructura y claridad del contenido Markdown (requiere análisis más sofisticado)

**Recomendación:** Reportar Comment Density como métrica de referencia, pero con advertencia explícita sobre su falta de validez para tldr-pages. Considerar métricas alternativas para realmente evaluar "calidad de la documentación" en este contexto.

---

## 11. Referencias

- Gyimesi, P., Gyimesi, G., Tóth, Z., & Ferenc, R. (2015). Characterization of source code defects by data mining conducted on GitHub. *Proceedings of the International Conference on Computational Science and Its Applications (ICCSA 2015)*, Springer, 47–62. https://doi.org/10.1007/978-3-319-21413-9_4

- Alonso, E. J., & Robiolo, G. (2022). Determinación de la calidad de producto, persona y proceso en entornos de desarrollo con GitHub: un estudio sistemático de la literatura. *Simposio Argentino de Ingeniería de Software (ASSE 2022)*, JAIIO 51.

- SonarSource. (n.d.). *SonarQube Documentation: Code Metrics*. Retrieved from https://docs.sonarqube.org

- Chidamber, S. R., & Kemerer, C. F. (1994). A metrics suite for object oriented design. *IEEE Transactions on Software Engineering*, 20(6), 476–493.

---

## Notas adicionales

- **Precisión de la detección:** Esta implementación utiliza heurísticas simples para detectar comentarios. Para análisis más riguroso, se recomienda SonarQube o herramientas especializadas.
- **Exclusiones:** Se excluyen directorios comunes de dependencias y binarios para no sesgar resultados.
- **Escalabilidad:** Para repositorios muy grandes, procesar por lotes o filtrar por directorios específicos.
