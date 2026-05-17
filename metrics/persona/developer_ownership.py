from collections import defaultdict

from core.base import Metrica

_BLAME_QUERY = """
query($owner: String!, $name: String!, $path: String!) {
  repository(owner: $owner, name: $name) {
    object(expression: "HEAD") {
      ... on Commit {
        blame(path: $path) {
          ranges {
            startingLine
            endingLine
            commit {
              author {
                user { login }
              }
            }
          }
        }
      }
    }
  }
}
"""


class DeveloperOwnership(Metrica):
    nombre = "Propiedad del Código por Desarrollador"
    descripcion = (
        "Calcula el porcentaje de líneas de código atribuidas a cada autor "
        "usando git blame sobre todos los archivos del repositorio (API GraphQL)."
    )
    dimension = "Persona"
    interpretacion = (
        "Un desarrollador con alta propiedad es el principal responsable de esa base de código. "
        "Concentración alta en un solo autor puede ser un riesgo si ese desarrollador abandona el proyecto."
    )

    def __init__(self, extractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        tree = self._extractor.get_repo_tree(owner, repo)
        archivos = [item["path"] for item in tree if item["type"] == "blob"]
        if limite:
            archivos = archivos[:limite]

        propiedad: dict[str, int] = defaultdict(int)
        total_lineas = 0

        for path in archivos:
            data = self._extractor.graphql(_BLAME_QUERY, {"owner": owner, "name": repo, "path": path})
            ranges = (
                data.get("data", {})
                    .get("repository", {})
                    .get("object", {})
                    .get("blame", {})
                    .get("ranges", [])
            )
            for rango in ranges:
                usuario = rango["commit"]["author"].get("user")
                if usuario:
                    lineas = rango["endingLine"] - rango["startingLine"] + 1
                    propiedad[usuario["login"]] += lineas
                    total_lineas += lineas

        if total_lineas == 0:
            return {}
        return {autor: round((l / total_lineas) * 100, 2) for autor, l in propiedad.items()}