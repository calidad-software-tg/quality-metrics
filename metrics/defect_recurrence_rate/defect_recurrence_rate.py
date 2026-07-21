"""
Métrica M32 - Defect Recurrence Rate (Tasa de Defectos Recurrentes)

Proporción de defectos que reaparecen tras ser corregidos, medida como el ratio
entre issues reabiertos y issues cerrados, según la ficha
(metrics/defect_recurrence_rate):

    defect_recurrence_rate = reopened_issues / total_closed_issues * 100

Definiciones (de la ficha):
  - total_closed_issues : issues que fueron cerrados AL MENOS UNA VEZ en el
                          historial (su estado actual puede ser open o closed).
  - reopened_issues     : issues que tienen al menos un evento `reopened`
                          (subconjunto de los cerrados al menos una vez).
  - Se EXCLUYEN los pull requests.
  - Resultado: porcentaje en [0, 100].

Implementación (GraphQL, alternativa recomendada por la ficha):
  En lugar de pedir los eventos de cada issue cerrado por separado (REST: una
  llamada por issue -> miles de llamadas, de ahí la recomendación de caché de la
  ficha), se pagina la conexión `issues` (que ya excluye PRs) y, por cada issue,
  se pide el totalCount de sus eventos CLOSED_EVENT y REOPENED_EVENT vía
  timelineItems. Así:
      - CLOSED_EVENT  >= 1  -> el issue fue cerrado al menos una vez (denominador)
      - REOPENED_EVENT >= 1 -> el issue fue reabierto al menos una vez (numerador)
  Esto reduce el costo a ~(cantidad_de_issues / 100) requests y hace innecesaria
  la caché. Además captura "cerrado al menos una vez" aunque el issue esté hoy
  abierto, fiel a la definición conceptual de la ficha.

Sesgos conocidos (ficha, sección 11):
  - Un reopened puede deberse a razones administrativas, no a un defecto real.
  - Un defecto recurrente podría reportarse como issue nuevo en vez de reabrir.
  - En repos de documentación como tldr-pages, "defecto" vs "mejora" es difuso.
  Pendiente de validación: filtrar por label `bug` para mayor precisión (requiere
  conocer las labels reales del repo). Acá se mide sobre TODOS los issues.

Referencia teórica: Colakoglu et al. (2021) - Reliability / ISO 25010.
"""

from core.base import Metrica


_QUERY_ISSUES = """
query($owner: String!, $repo: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    issues(first: 100, after: $cursor) {
      pageInfo { hasNextPage endCursor }
      nodes {
        closed: timelineItems(itemTypes: [CLOSED_EVENT]) { totalCount }
        reopened: timelineItems(itemTypes: [REOPENED_EVENT]) { totalCount }
      }
    }
  }
}
"""


class DefectRecurrenceRate(Metrica):
    nombre = "Defect Recurrence Rate"
    descripcion = (
        "Proporción de issues que fueron cerrados y luego reabiertos al menos una "
        "vez, sobre el total de issues cerrados al menos una vez. Proxy de la "
        "recurrencia de defectos (regresiones). Excluye pull requests."
    )
    dimension = ["Proceso", "Producto"]
    interpretacion = (
        "Una tasa baja indica que las correcciones son estables y efectivas. Una "
        "tasa alta puede señalar correcciones incompletas, regresiones frecuentes o "
        "falta de tests de regresión. Es un proxy: no todo reopened es un defecto."
    )

    def __init__(self, extractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        """
        Recorre los issues del repo (sin PRs) contando cuántos fueron cerrados al
        menos una vez y cuántos reabiertos al menos una vez.

        `limite` corta tras procesar esa cantidad de issues (muestra para pruebas;
        el orden por defecto de GitHub no garantiza representatividad). Para el
        valor definitivo usar limite=None.
        """
        total_closed = 0
        reopened = 0
        cursor = None
        procesados = 0

        while True:
            data = self._extractor.graphql(
                _QUERY_ISSUES, {"owner": owner, "repo": repo, "cursor": cursor}
            )
            if "errors" in data:
                raise RuntimeError(f"GraphQL devolvió errores: {data['errors']}")

            repo_data = (data.get("data") or {}).get("repository")
            if repo_data is None:
                raise RuntimeError(
                    f"No se encontró el repositorio {owner}/{repo} "
                    "(¿nombre incorrecto o sin permisos?)."
                )

            issues = repo_data.get("issues") or {}
            for nodo in issues.get("nodes", []):
                cerrado = (nodo.get("closed") or {}).get("totalCount", 0)
                reabierto = (nodo.get("reopened") or {}).get("totalCount", 0)
                if cerrado >= 1:
                    total_closed += 1
                if reabierto >= 1:
                    reopened += 1

                procesados += 1
                if limite and procesados >= limite:
                    return self._resultado(total_closed, reopened)

            page = issues.get("pageInfo") or {}
            if not page.get("hasNextPage"):
                break
            cursor = page.get("endCursor")

        return self._resultado(total_closed, reopened)

    @staticmethod
    def _resultado(total_closed: int, reopened: int) -> dict:
        rate = round(reopened / total_closed * 100, 2) if total_closed else 0.0
        return {
            "total_closed_issues": total_closed,
            "reopened_issues": reopened,
            "defect_recurrence_rate": rate,
        }