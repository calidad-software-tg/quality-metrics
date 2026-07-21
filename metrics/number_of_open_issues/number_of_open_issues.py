"""
Métrica M28 - Number of Open Issues (Cantidad de Issues Abiertos)

Cuenta los issues en estado OPEN de un repositorio en un momento dado, según la
ficha (metrics/number_of_open_issues):

    Number of Open Issues = count(issues con estado = open)

Decisiones (de la ficha):
  - Se EXCLUYEN los pull requests. GitHub los mezcla con los issues en el endpoint
    general y en el campo REST `open_issues_count`, que por eso NO se usa. La query
    GraphQL issues(states: OPEN) cuenta solo issues reales, sin PRs.
  - Es un valor PUNTUAL (snapshot): cambia con el tiempo. Se registra la fecha de
    extracción junto al valor para reproducibilidad.
  - Los bots pueden abrir issues (github-actions[bot], dependabot[bot]). El conteo
    los INCLUYE (totalCount no discrimina autor); se deja constancia aquí para
    transparencia metodológica.

Referencias: Jarczyk et al. (2014, 2018); Gyimesi et al. (2015).
"""

from datetime import datetime, timezone

from core.base import Metrica


_QUERY_OPEN_ISSUES = """
query($owner: String!, $repo: String!) {
  repository(owner: $owner, name: $repo) {
    issues(states: OPEN) { totalCount }
  }
}
"""


class NumberOfOpenIssues(Metrica):
    nombre = "Number of Open Issues"
    descripcion = (
        "Cantidad total de issues en estado abierto en el repositorio al momento "
        "de la extracción, excluyendo pull requests. Representa el backlog de "
        "problemas, pedidos de funcionalidad y tareas pendientes de resolución."
    )
    dimension = ["Proceso", "Producto"]
    interpretacion = (
        "Es un snapshot del backlog. Un backlog alto puede indicar más reportes de "
        "los que el equipo resuelve en el corto plazo, no necesariamente baja "
        "calidad del producto. El valor es puntual: varía al abrirse y cerrarse issues."
    )

    def __init__(self, extractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        """
        Devuelve el conteo de issues abiertos (sin PRs) y la fecha de extracción.
        `limite` no aplica a esta métrica (es un único valor agregado); se acepta
        por compatibilidad con la interfaz Metrica.
        """
        data = self._extractor.graphql(
            _QUERY_OPEN_ISSUES, {"owner": owner, "repo": repo}
        )
        if "errors" in data:
            raise RuntimeError(f"GraphQL devolvió errores: {data['errors']}")

        repo_data = (data.get("data") or {}).get("repository")
        if repo_data is None:
            raise RuntimeError(
                f"No se encontró el repositorio {owner}/{repo} "
                "(¿nombre incorrecto o sin permisos?)."
            )

        open_issues = repo_data["issues"]["totalCount"]
        extraction_date = (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )

        return {
            "open_issues_count": open_issues,
            "extraction_date": extraction_date,
        }