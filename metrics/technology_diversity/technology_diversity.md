# C15 – Diversidad Tecnológica (Technology Diversity)

## 1. Descripción

La métrica **Technology Diversity** mide la cantidad de tecnologías o lenguajes de programación distintos utilizados por un desarrollador durante su actividad en un repositorio. Se utiliza como indicador de versatilidad técnica y capacidad para trabajar en diferentes tecnologías dentro de un proyecto de software.

Aunque Gyimesi et al. (2015) no definen explícitamente una métrica denominada *Technology Diversity*, su framework demuestra que es posible extraer automáticamente información sobre lenguajes de programación, desarrolladores y archivos modificados a partir de GitHub y sistemas de control de versiones.

La métrica se construye a partir de dos capacidades demostradas en el paper:

1. Detección automática de lenguajes de programación mediante GitHub Linguist.
2. Asociación entre desarrolladores y archivos modificados utilizando el historial de commits.

En el contexto de la encuesta, esta métrica se utiliza como proxy de la capacidad de aprendizaje técnico y adaptación a diferentes tecnologías.

---

## 2. Clasificación – Dimensiones 3P

| Dimensión | Clasificación |
| --------- | ------------- |
| Persona   | Sí            |
| Proceso   | No            |
| Producto  | No            |

### Constructo asociado

**Aprendizaje técnico / capacidad de adaptación tecnológica**

La diversidad tecnológica se interpreta como un indicador indirecto de exposición y experiencia en múltiples tecnologías.

---

## 3. Fundamentación en Gyimesi et al. (2015)

El paper proporciona la base metodológica para construir esta métrica mediante tres elementos fundamentales.

### Detección automática de tecnologías

Los autores muestran que GitHub permite obtener estadísticas automáticas sobre los lenguajes utilizados en los repositorios mediante GitHub Linguist.

Esta capacidad permite identificar objetivamente qué tecnologías están presentes en un proyecto y constituye la base para contabilizar tecnologías distintas.

### Asociación entre desarrolladores y archivos

Los autores indican:

> "From the version control system the number of modifications and fixes on a file can be easily determined; moreover, committer identity can be mapped to the changed files."

Esta afirmación demuestra que es posible asociar cada desarrollador con los archivos que modifica.

### Extracción de métricas objetivas

Gyimesi et al. proponen un framework de métricas extraídas automáticamente desde GitHub y sistemas de control de versiones, demostrando que propiedades observables del desarrollo pueden transformarse en métricas cuantificables.

Technology Diversity sigue este mismo enfoque metodológico.

---

## 4. Fórmula de cálculo

[
TechnologyDiversity =
count(distinct\ programming_languages)
]

Donde:

* `programming_languages` representa los lenguajes detectados en los archivos modificados por el desarrollador.
* `distinct` indica que cada lenguaje se cuenta una única vez.
* El resultado representa la cantidad de tecnologías diferentes utilizadas por un desarrollador.

### Ejemplo

Si un desarrollador modificó archivos:

```text
README.md
script.py
docker-compose.yml
build.sh
```

y GitHub Linguist identifica:

```text
Markdown
Python
YAML
Shell
```

entonces:

[
TechnologyDiversity = 4
]

---

## 5. Variables necesarias

| Variable           | Descripción                          |
| ------------------ | ------------------------------------ |
| developer_id       | Identificador del desarrollador      |
| commit_id          | Commit realizado                     |
| modified_files     | Archivos modificados                 |
| file_language      | Lenguaje detectado para cada archivo |
| distinct_languages | Conjunto único de lenguajes          |

---

## 6. Fuente de datos

Basado en la metodología propuesta por Gyimesi et al. (2015).

### GitHub API

Permite obtener:

* commits
* desarrolladores
* archivos modificados

### Git Metadata

Permite asociar:

* desarrollador → commit
* commit → archivo modificado

### GitHub Linguist

Permite detectar automáticamente:

* lenguaje principal de cada archivo
* clasificación tecnológica del repositorio

---

## 7. Implementación Python

```python
from collections import defaultdict

def technology_diversity(commits, file_languages):
    developer_languages = defaultdict(set)

    for commit in commits:
        developer = commit["author"]

        for file in commit["files"]:
            language = file_languages.get(file)

            if language:
                developer_languages[developer].add(language)

    return {
        developer: len(languages)
        for developer, languages in developer_languages.items()
    }
```

Resultado:

```python
{
    "developer_1": 4,
    "developer_2": 2,
    "developer_3": 7
}
```

---

## 8. Calculabilidad en tldr-pages/tldr

### Parcialmente calculable

La métrica puede implementarse técnicamente utilizando GitHub API y GitHub Linguist.

Sin embargo, presenta una limitación importante en tldr-pages:

* la mayor parte del repositorio está compuesta por archivos Markdown (`.md`);
* existe una baja diversidad real de tecnologías;
* gran parte de las contribuciones corresponden a documentación y no a código fuente.

Por este motivo, los valores obtenidos tenderán a ser bajos y reflejarán principalmente diversidad de formatos de documentación más que diversidad de lenguajes de programación.

La métrica es técnicamente calculable pero su capacidad discriminatoria dentro de este repositorio es limitada.

---

## 9. Interpretación

| Valor | Interpretación                  |
| ----- | ------------------------------- |
| 1     | Uso de una única tecnología     |
| 2-3   | Diversidad tecnológica baja     |
| 4-6   | Diversidad tecnológica moderada |
| > 6   | Diversidad tecnológica alta     |

Los rangos deben interpretarse considerando las características del proyecto analizado.

---

## 10. Relación con el ítem de encuesta

La métrica se relaciona con el constructo:

> "Capacidad de aprender nuevas habilidades técnicas"

La lógica subyacente es que un desarrollador que trabaja con múltiples tecnologías probablemente haya desarrollado conocimientos y habilidades en distintos dominios técnicos.

Sin embargo, la métrica no mide aprendizaje de forma directa. Únicamente observa la utilización de tecnologías diferentes dentro del historial de contribuciones.

Por este motivo debe considerarse una métrica proxy.

---

## 11. Observaciones

La métrica no fue definida explícitamente por Gyimesi et al. (2015). Su construcción se basa en capacidades demostradas por el framework presentado en el paper:

* detección automática de lenguajes;
* extracción de métricas desde GitHub;
* asociación entre desarrolladores y archivos modificados.

Technology Diversity constituye una extensión metodológicamente consistente del enfoque propuesto por los autores.

---

## 12. Referencia

Gyimesi, P., Gyimóthy, T., & Ferenc, R. (2015).

Framework para extracción automática de métricas de calidad de software a partir de repositorios GitHub y sistemas de control de versiones.
