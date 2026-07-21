"""
Métrica M42 - Number of Active Development Branches (Ramas Activas)

Cantidad de ramas del repositorio principal con actividad reciente, según la ficha
(metrics/active_branches):

    Active Branches = count( ramas con último commit >= now - threshold_days )

Definición: una rama es "activa" si tuvo al menos 1 commit en los últimos
`threshold_days` días (umbral estándar 90; configurable). Se reportan también las
variantes a 90 y 30 días y el total sin filtro (consistente con Jarczyk et al. 2014).

Decisión de extracción (importante para tldr-pages):
  La ficha recomienda Git local, pero el clon local del equipo es el FORK
  (calidad-software-tg/tldr), que no contiene las ramas reales de tldr-pages/tldr.
  Como la consigna pide "el repositorio principal" y se mide comunidad sobre
  tldr-pages/tldr, se usa la API de GitHub (GraphQL) contra el repo original:
  refs(refPrefix:"refs/heads/") trae todas las ramas con la fecha de su último
  commit en una sola query. Las ramas de los forks no aparecen (son repos
  separados), así que quedan excluidas naturalmente.

Nota de contexto (ficha): tldr-pages usa contribución vía forks, por lo que el
número de ramas activas en el repo principal es inherentemente bajo (1-3). Eso NO
indica baja calidad: es una característica del modelo de desarrollo y debe
documentarse en el análisis.

Referencia teórica: Jarczyk et al. (2014) - branches_count / calidad OSS.
"""

from datetime import datetime, timezone

from core.base import Metrica


_QUERY_BRANCHES = """
query($owner: String!, $repo: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    refs(refPrefix: "refs/heads/", first: 100, after: $cursor) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name
        target {
          ... on Commit { committedDate }
        }
      }
    }
  }
}
"""


class NumberOfActiveBranches(Metrica):
    nombre = "Number of Active Development Branches"
    descripcion = (
        "Cantidad de ramas del repositorio principal con al menos un commit en los "
        "últimos N días (activas), más el total de ramas sin filtro. Excluye las "
        "ramas de los forks (no pertenecen al repo principal)."
    )
    dimension = ["Proceso", "Producto"]
    interpretacion = (
        "Refleja el uso del workflow de branching en el repo principal. En proyectos "
        "con contribución vía forks (como tldr-pages) el valor es bajo por diseño, no "
        "por baja calidad: el trabajo ocurre en forks externos, no en ramas internas."
    )

    def __init__(self, github_extractor, threshold_days: int = 90):
        self._extractor = github_extractor
        self._threshold_days = threshold_days

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        """
        Cuenta ramas activas del repo principal. `threshold_days` (del constructor)
        define el umbral del flag `active`; se reportan además las variantes 90d/30d
        y el total. `limite` no aplica (las ramas del repo principal son pocas).
        """
        ahora = datetime.now(timezone.utc)
        ramas = []  # (nombre, datetime del último commit)

        cursor = None
        while True:
            data = self._extractor.graphql(
                _QUERY_BRANCHES, {"owner": owner, "repo": repo, "cursor": cursor}
            )
            if "errors" in data:
                raise RuntimeError(f"GraphQL devolvió errores: {data['errors']}")
            repo_data = (data.get("data") or {}).get("repository")
            if repo_data is None:
                raise RuntimeError(
                    f"No se encontró el repositorio {owner}/{repo} "
                    "(¿nombre incorrecto o sin permisos?)."
                )

            refs = repo_data.get("refs") or {}
            for nodo in refs.get("nodes", []):
                fecha = (nodo.get("target") or {}).get("committedDate")
                if not fecha:
                    continue  # ref que no apunta a un commit (no debería pasar en heads)
                dt = datetime.fromisoformat(fecha.replace("Z", "+00:00"))
                ramas.append((nodo["name"], dt))

            page = refs.get("pageInfo") or {}
            if not page.get("hasNextPage"):
                break
            cursor = page.get("endCursor")

        def activa(dt: datetime, dias: int) -> bool:
            return (ahora - dt).days <= dias

        detalles = sorted(
            [
                {
                    "name": nombre,
                    "last_commit": dt.date().isoformat(),
                    "active": activa(dt, self._threshold_days),
                }
                for nombre, dt in ramas
            ],
            key=lambda d: d["last_commit"],
            reverse=True,
        )

        return {
            "total_branches": len(ramas),
            "active_branches_90d": sum(1 for _, dt in ramas if activa(dt, 90)),
            "active_branches_30d": sum(1 for _, dt in ramas if activa(dt, 30)),
            "threshold_days": self._threshold_days,
            "extraction_date": (
                ahora.replace(microsecond=0).isoformat().replace("+00:00", "Z")
            ),
            "branch_details": detalles,
        }