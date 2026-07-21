"""
Utilidad para estimar la lista de core developers de un repositorio, con evidencia
por persona, para que un humano (Esteban) la revise/pode antes de usarla.

No es una métrica: es un helper que alimenta el parámetro `core_developers` de
UserReportedBugs (M39). Resuelve el pendiente de la ficha ("confirmar la lista de
core con Esteban") generando una lista candidata fundamentada.

Señales usadas (todas a nivel de login de GitHub, confiables):
  - mergedBy de PRs mergeados: para mergear un PR hace falta acceso de escritura,
    así que quien mergeó es (o fue) del equipo core. Señal empírica más fuerte;
    además da un conteo (cuántos PRs mergeó) que ayuda a separar el núcleo activo
    de la cola larga de maintainers (p. ej. maintainers de idioma con 0 merges).
  - Docs de maintainers/gobernanza: MAINTAINERS.md y GOVERNANCE.md (el
    CONTRIBUTING.md de tldr-pages apunta a GOVERNANCE.md como doc de gobernanza).
  - CODEOWNERS: dueños de código declarados (se ignoran los equipos @org/team).

No usa la API de colaboradores/miembros de la org: para repos ajenos GitHub solo la
expone a quienes ya tienen acceso (o solo miembros públicos), así que sería
incompleta. Las señales de arriba son visibles para cualquiera.

Salida: dict con la lista de candidatos ordenada por PRs mergeados (desc) y la
evidencia de cada uno. La decisión final de quién es core la toma Esteban.
"""

import base64
import re

from collections import Counter


_HANDLE = r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?"

_DOCS_MAINTAINERS = ["MAINTAINERS.md", "GOVERNANCE.md"]
_DOCS_CODEOWNERS = [".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS"]

_QUERY_MERGERS = """
query($owner: String!, $repo: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequests(states: MERGED, first: 100, after: $cursor,
                 orderBy: {field: CREATED_AT, direction: DESC}) {
      pageInfo { hasNextPage endCursor }
      nodes { mergedBy { login } }
    }
  }
}
"""


class CoreDevelopersResolver:
    def __init__(self, github_extractor):
        self._extractor = github_extractor

    def resolver(self, owner: str, repo: str, limite: int = None) -> dict:
        """
        Estima los core developers combinando mergedBy + docs de maintainers
        (MAINTAINERS.md / GOVERNANCE.md) + CODEOWNERS.
        `limite` corta el recorrido de PRs (para pruebas; con orderBy DESC toma los
        más recientes). Para la lista definitiva usar limite=None.
        """
        # Se excluye el nombre de la org/owner para que no se cuele como persona
        # (p. ej. links del tipo github.com/tldr-pages/...).
        excluir = {owner.lower()}

        en_docs = self._handles_de_docs(owner, repo, _DOCS_MAINTAINERS) - excluir
        codeowners = self._handles_codeowners(owner, repo) - excluir
        mergers = self._pr_mergers(owner, repo, limite)  # Counter login -> #PRs

        logins = set(en_docs) | set(codeowners) | set(mergers)
        candidatos = [
            {
                "login": login,
                "in_maintainers_doc": login in en_docs,
                "in_codeowners": login in codeowners,
                "prs_merged": mergers.get(login, 0),
            }
            for login in logins
        ]
        candidatos.sort(key=lambda c: (-c["prs_merged"], c["login"]))

        return {
            "repo": f"{owner}/{repo}",
            "total_candidatos": len(candidatos),
            "fuentes": {
                "maintainers_doc": len(en_docs),
                "codeowners": len(codeowners),
                "pr_mergers": len(mergers),
            },
            "candidatos": candidatos,
        }

    # --- señal fuerte: quién mergeó PRs (= acceso de escritura) --------------
    def _pr_mergers(self, owner: str, repo: str, limite: int = None) -> Counter:
        mergers = Counter()
        cursor = None
        procesados = 0
        while True:
            data = self._extractor.graphql(
                _QUERY_MERGERS, {"owner": owner, "repo": repo, "cursor": cursor}
            )
            if "errors" in data:
                raise RuntimeError(f"GraphQL devolvió errores: {data['errors']}")
            prs = (((data.get("data") or {}).get("repository") or {})
                   .get("pullRequests") or {})
            for nodo in prs.get("nodes", []):
                mb = nodo.get("mergedBy") or {}
                login = (mb.get("login") or "")
                if login and not login.endswith("[bot]"):
                    mergers[login.lower()] += 1
                procesados += 1
                if limite and procesados >= limite:
                    return mergers
            page = prs.get("pageInfo") or {}
            if not page.get("hasNextPage"):
                break
            cursor = page.get("endCursor")
        return mergers

    # --- señales declarativas: archivos del repo -----------------------------
    def _handles_de_docs(self, owner: str, repo: str, paths: list) -> set:
        """Lee TODOS los docs que existan de `paths` y une los handles de GitHub."""
        handles = set()
        for path in paths:
            contenido = self._leer_archivo(owner, repo, path)
            if contenido is None:
                continue
            for m in re.findall(rf"github\.com/({_HANDLE})(?=[)\s\"'>/]|$)", contenido):
                handles.add(m.lower())
            for m in re.findall(rf"(?<![A-Za-z0-9_])@({_HANDLE})", contenido):
                handles.add(m.lower())
        return handles

    def _handles_codeowners(self, owner: str, repo: str) -> set:
        """CODEOWNERS: handles @usuario del primer archivo que exista, ignorando
        equipos @org/team."""
        contenido = None
        for path in _DOCS_CODEOWNERS:
            contenido = self._leer_archivo(owner, repo, path)
            if contenido is not None:
                break
        if contenido is None:
            return set()
        handles = set()
        for usuario, equipo in re.findall(rf"@({_HANDLE})(/[A-Za-z0-9-]+)?", contenido):
            if not equipo:  # con "/" es un equipo @org/team -> se ignora
                handles.add(usuario.lower())
        return handles

    def _leer_archivo(self, owner: str, repo: str, path: str):
        """Lee un archivo del repo y devuelve su texto, o None si no existe."""
        try:
            data = self._extractor.get_repo_contents(owner, repo, path)
            return base64.b64decode(data.get("content", "")).decode("utf-8", "ignore")
        except Exception:
            return None