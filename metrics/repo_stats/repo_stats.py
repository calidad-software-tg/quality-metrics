from core.base import Metrica

_QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    refs(refPrefix: "refs/heads/") { totalCount }
    collaborators { totalCount }
    object(expression: "HEAD:") {
      ... on Tree {
        entries {
          type
          object {
            ... on Blob { text }
          }
        }
      }
    }
  }
}
"""


class RepoStats(Metrica):
    nombre = "Estadísticas del Repositorio"
    descripcion = (
        "Calcula el número de ramas activas, colaboradores con acceso "
        "y líneas de código estimadas en los archivos raíz del repositorio."
    )
    dimension = ["Producto"]
    interpretacion = (
        "Más ramas activas sugieren desarrollo paralelo intenso. "
        "El conteo de colaboradores refleja el tamaño del equipo. "
        "Las líneas de código estiman la magnitud del proyecto."
    )

    def __init__(self, extractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        data = self._extractor.graphql(_QUERY, {"owner": owner, "name": repo})
        r = data["data"]["repository"]

        branches = r["refs"]["totalCount"]
        collaborators = r["collaborators"]["totalCount"]

        entries = r.get("object", {}).get("entries", [])
        lines = sum(
            e["object"]["text"].count("\n") + 1
            for e in entries
            if e["type"] == "blob" and e.get("object") and e["object"].get("text")
        )
        return {
            "branches": branches,
            "collaborators": collaborators,
            "estimated_lines_of_code": lines,
        }