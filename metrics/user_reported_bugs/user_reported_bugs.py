"""
Métrica M39 - Number of Bugs Detected by Users (Bugs Reportados por Usuarios)

Cuenta los issues de tipo bug reportados por usuarios EXTERNOS (no-core), según la
ficha (metrics/user_reported_bugs):

    n_user_bugs = count( issues_bug  &  reporter NOT IN core_developers )

Operacionalización para tldr-pages (decisiones de la ficha y de calidad técnica):

  CORE DEVELOPERS
    Origen confiable = MAINTAINERS.md (handles) + lista configurable (la que
    confirme Esteban). NO se usan los "commits directos" del git log: en tldr todo
    entra por PR con squash merge, y el squash atribuye el commit al AUTOR del PR
    (habitualmente externo), no al maintainer. Usar committers como core marcaría
    como core a los externos -> deflactaría la métrica. Por eso core = maintainers.
    `core_developers` es parámetro: si se pasa, es autoritativo; si no, se parsea
    MAINTAINERS.md. (git_extractor se acepta por compatibilidad pero no se usa.)

  IDENTIFICACIÓN DE BUGS
    tldr-pages no etiqueta bugs de forma consistente, así que:
      - by_label  : issues con alguna label que contenga una keyword de bug.
      - by_keyword: issues cuyo título o body contenga una keyword de bug.
    identification_method = "label" si hay bugs por label; si no, "keyword".
    Keywords por defecto (las del ejemplo de la ficha, sin "fix"/"not working"
    por ruidosas): wrong, incorrect, outdated, deprecated, broken, error.

  REPORTER EXTERNO
    Un issue es "de usuario" si su autor NO está en el set de core developers.
    Autor nulo (cuenta borrada) se trata como externo (no es core).

Limitaciones (ficha): tldr es documentación, no software ejecutable; "bug" aquí es
una página incorrecta/desactualizada. La métrica es sensible a la definición de
core: cuanto más amplia, menos "usuarios externos". Pendiente: validar la lista de
core con Esteban.

Referencia teórica: Vasilescu et al. (2015) - n_user_bugs / calidad externa.
"""

import base64
import re

from core.base import Metrica


KEYWORDS_BUG_DEFAULT = ["wrong", "incorrect", "outdated", "deprecated", "broken", "error"]
LABEL_KEYWORDS_DEFAULT = ["bug", "error", "incorrect", "outdated", "wrong"]

_ASOCIACIONES_CORE = {"OWNER", "MEMBER", "COLLABORATOR"}

_QUERY_ISSUES = """
query($owner: String!, $repo: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    issues(first: 100, after: $cursor) {
      pageInfo { hasNextPage endCursor }
      nodes {
        author { login }
        title
        body
        labels(first: 30) { nodes { name } }
      }
    }
  }
}
"""


class UserReportedBugs(Metrica):
    nombre = "Number of Bugs Detected by Users"
    descripcion = (
        "Cantidad de issues identificados como bugs (por label o por keyword en "
        "título/body) reportados por usuarios externos al equipo core del proyecto. "
        "Proxy de la calidad externa percibida por el usuario final."
    )
    dimension = ["Proceso", "Persona", "Producto"]
    interpretacion = (
        "Más bugs reportados por usuarios externos sugiere más inconsistencias "
        "detectadas por la comunidad. En tldr un 'bug' es una página incorrecta o "
        "desactualizada, no un fallo de código, lo que matiza la interpretación."
    )

    def __init__(self, github_extractor, git_extractor=None,
                 core_developers=None, keywords=None, bug_label_keywords=None,
                 metodo="keyword"):
        if metodo not in ("keyword", "label", "auto"):
            raise ValueError("metodo debe ser 'keyword', 'label' o 'auto'")
        self._extractor = github_extractor
        self._git = git_extractor  # aceptado por compatibilidad; no se usa (ver módulo)
        self._core_param = (
            {u.lower() for u in core_developers} if core_developers is not None else None
        )
        self._keywords = [k.lower() for k in (keywords or KEYWORDS_BUG_DEFAULT)]
        self._label_keywords = [k.lower() for k in (bug_label_keywords or LABEL_KEYWORDS_DEFAULT)]
        # Método de identificación de bugs:
        #   "keyword" (default, fiel a la ficha para tldr: keyword es lo viable)
        #   "label"   (fuerza label)
        #   "auto"    (label si hay algún bug por label; si no, keyword)
        self._metodo = metodo

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        core = self._obtener_core_developers(owner, repo)

        total_issues = 0
        bug_by_label = 0
        bug_by_keyword = 0
        user_bug_by_label = 0
        user_bug_by_keyword = 0

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
                total_issues += 1

                autor = nodo.get("author") or {}
                login = (autor.get("login") or "").lower()
                es_externo = login not in core  # login vacío (cuenta borrada) -> externo

                es_bug_label = self._es_bug_por_label(nodo)
                es_bug_keyword = self._es_bug_por_keyword(nodo)

                if es_bug_label:
                    bug_by_label += 1
                    if es_externo:
                        user_bug_by_label += 1
                if es_bug_keyword:
                    bug_by_keyword += 1
                    if es_externo:
                        user_bug_by_keyword += 1

                procesados += 1
                if limite and procesados >= limite:
                    return self._resultado(
                        core, total_issues, bug_by_label, bug_by_keyword,
                        user_bug_by_label, user_bug_by_keyword,
                    )

            page = issues.get("pageInfo") or {}
            if not page.get("hasNextPage"):
                break
            cursor = page.get("endCursor")

        return self._resultado(
            core, total_issues, bug_by_label, bug_by_keyword,
            user_bug_by_label, user_bug_by_keyword,
        )

    def _resultado(self, core, total_issues, bug_by_label, bug_by_keyword,
                   user_bug_by_label, user_bug_by_keyword) -> dict:
        # Elegir método según configuración.
        if self._metodo == "label":
            metodo = "label"
        elif self._metodo == "keyword":
            metodo = "keyword"
        else:  # auto: label si hay bugs por label, si no keyword
            metodo = "label" if bug_by_label > 0 else "keyword"

        user_bugs = user_bug_by_label if metodo == "label" else user_bug_by_keyword
        return {
            "core_developers_count": len(core),
            "total_issues": total_issues,
            "bug_issues_by_label": bug_by_label,
            "bug_issues_by_keyword": bug_by_keyword,
            "user_bug_issues": user_bugs,
            "n_user_bugs": user_bugs,
            "identification_method": metodo,
            "keywords_used": self._keywords,
        }

    def _es_bug_por_label(self, nodo: dict) -> bool:
        labels = ((nodo.get("labels") or {}).get("nodes")) or []
        for lab in labels:
            nombre = (lab.get("name") or "").lower()
            if any(k in nombre for k in self._label_keywords):
                return True
        return False

    def _es_bug_por_keyword(self, nodo: dict) -> bool:
        texto = ((nodo.get("title") or "") + " " + (nodo.get("body") or "")).lower()
        return any(k in texto for k in self._keywords)

    def _obtener_core_developers(self, owner: str, repo: str) -> set:
        """Lista de core devs: parámetro autoritativo si se pasó; si no, parseo de
        MAINTAINERS.md. Devuelve logins en minúscula."""
        if self._core_param is not None:
            return self._core_param

        try:
            data = self._extractor.get_repo_contents(owner, repo, "MAINTAINERS.md")
            contenido = base64.b64decode(data.get("content", "")).decode("utf-8", "ignore")
        except Exception:
            return set()  # sin MAINTAINERS.md accesible; quedará vacío (se ve en el count)

        handles = set()
        # Links a perfiles: github.com/<handle> (no seguido de otra ruta -> evita repos/orgs)
        for m in re.findall(r"github\.com/([A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?)(?=[)\s\"'>/]|$)", contenido):
            handles.add(m.lower())
        # Menciones @handle
        for m in re.findall(r"(?<![A-Za-z0-9_])@([A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?)", contenido):
            handles.add(m.lower())
        return handles