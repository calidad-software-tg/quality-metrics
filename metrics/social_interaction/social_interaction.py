"""
Métrica M19 - Social Interaction between Developers
(Interacción Social entre Desarrolladores)

Operacionaliza la interacción social como el conteo de eventos de comunicación
explícita entre desarrolladores registrados en GitHub, según la ficha del repo
(metrics/social_interaction):

    social_interaction_total = issue_comments + pr_comments + pr_reviews

Canales (objetos de GitHub distintos: su suma NO duplica eventos):
  - issue_comments : comentarios de conversación sobre ISSUES reales.
  - pr_comments    : comentarios de conversación sobre PRs + comentarios inline
                     de revisión sobre el diff de los PRs.
  - pr_reviews     : revisiones formales (APPROVE / CHANGES_REQUESTED / COMMENT)
                     sobre PRs.

Detalle de extracción (Model B):
  GitHub modela los PR como issues, por lo que el endpoint REST /issues/comments
  devuelve los comentarios de conversación TANTO de issues como de PRs. Para
  separarlos se usa el campo `html_url` de cada comentario:
      - contiene "/issues/"  -> comentario sobre un issue real -> issue_comments
      - contiene "/pull/"    -> comentario sobre un PR          -> pr_comments
  A eso se suman los comentarios inline (/pulls/comments), que siempre son de PR.
  Así los subtotales quedan fieles a sus nombres sin llamadas extra a la API.

Decisiones metodológicas (de la ficha):
  - Se excluyen bots del conteo (github-actions[bot], dependabot, tldr-bot, etc.).
  - No se cuentan commits sin comentario ni reacciones (interacciones pasivas).
  - Es un proxy: solo capta lo registrado en GitHub, no comunicación externa.

Referencia teórica: Foucault et al. (2015); catálogo ISL/JAIIO 2022 (orden 91).
"""

from collections import Counter

from core.base import Metrica



# Bots a excluir explícitamente. Las dos primeras señales (sufijo "[bot]" y el
# tipo que reporta la API) atrapan a la mayoría, pero los bots que usan una
# cuenta de usuario común (como tldr-bot en tldr-pages) NO terminan en "[bot]"
# ni reportan type == "Bot", así que hay que listarlos a mano aquí.
BOTS_CONOCIDOS = {
    "github-actions[bot]",
    "dependabot[bot]",
    "dependabot-preview[bot]",
    "renovate[bot]",
    "codecov[bot]",
    "stale[bot]",
    "mergify[bot]",
    "allcontributors[bot]",
    "tldr-bot",            # específico de tldr-pages (cuenta de usuario, no App)
}

# Tamaños de página para la paginación GraphQL de revisiones.
_PRS_POR_PAGINA = 100
_REVIEWS_POR_PR = 10

_QUERY_REVIEWS = """
query($owner: String!, $repo: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequests(first: %d, after: $cursor) {
      pageInfo { hasNextPage endCursor }
      nodes {
        reviews(first: %d) {
          nodes {
            state
            author { login __typename }
          }
        }
      }
    }
  }
}
""" % (_PRS_POR_PAGINA, _REVIEWS_POR_PR)


class SocialInteractionBetweenDevelopers(Metrica):
    nombre = "Social Interaction between Developers"
    descripcion = (
        "Cuantifica la interacción y comunicación entre desarrolladores a partir "
        "de los eventos registrados en GitHub: comentarios en issues, comentarios "
        "en pull requests y revisiones de pull requests. Excluye bots."
    )
    dimension = ["Proceso", "Persona"]
    interpretacion = (
        "Un valor más alto refleja una comunidad con comunicación más intensa entre "
        "contributors. Es un proxy de la interacción social real: no contempla "
        "comunicación fuera de GitHub (Slack, Discord, listas de correo, etc.)."
    )

    def __init__(self, extractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        """
        Calcula la interacción social total y su desglose por desarrollador.

        `limite` es un tope grosero para corridas de prueba: se aplica POR CANAL
        (primeros N comentarios de cada endpoint y primeros N PRs para reviews).
        Para el valor definitivo de la métrica usar limite=None (histórico completo).

        Nota de costo: pr_reviews requiere recorrer todos los PRs vía GraphQL, por
        lo que es el canal más caro en rate limit. GraphQL exige token de auth.
        """
        # Conversación: un solo endpoint (/issues/comments), separado por html_url.
        issue_comments, pr_conv, autores_issue, autores_pr_conv = \
            self._contar_conversacion(owner, repo, limite)

        # Comentarios inline de revisión (siempre pertenecen a un PR).
        pr_inline, autores_inline = self._contar_comentarios(
            owner, repo, "pulls/comments", limite
        )

        # Revisiones formales (GraphQL).
        pr_reviews, autores_review = self._contar_reviews(owner, repo, limite)

        pr_comments = pr_conv + pr_inline

        por_desarrollador = Counter()
        for parcial in (autores_issue, autores_pr_conv, autores_inline, autores_review):
            por_desarrollador.update(parcial)

        top_interactors = dict(
            sorted(por_desarrollador.items(), key=lambda kv: kv[1], reverse=True)
        )

        return {
            "issue_comments": issue_comments,
            "pr_comments": pr_comments,
            "pr_reviews": pr_reviews,
            "social_interaction_total": issue_comments + pr_comments + pr_reviews,
            "top_interactors": top_interactors,
        }

    # ------------------------------------------------------------------ #
    # Comentarios de conversación: /issues/comments separado por html_url
    # ------------------------------------------------------------------ #
    def _contar_conversacion(self, owner, repo, limite=None):
        t_issue = t_pr = 0
        aut_issue, aut_pr = Counter(), Counter()
        vistos = 0
        for pagina in self._extractor.iter_paginated(owner, repo, "issues/comments"):
            for c in pagina:
                user = c.get("user") or {}
                login = user.get("login")
                if not self._es_humano(login, tipo=user.get("type")):
                    continue
                if "/pull/" in (c.get("html_url") or ""):
                    t_pr += 1
                    if login: aut_pr[login] += 1
                else:
                    t_issue += 1
                    if login: aut_issue[login] += 1
            vistos += len(pagina)
            print(f"    [conversacion] comentarios vistos: {vistos}")
            if limite and vistos >= limite:
                break
        return t_issue, t_pr, aut_issue, aut_pr

    def _contar_comentarios(self, owner, repo, endpoint, limite=None):
        total = 0
        por_autor = Counter()
        vistos = 0
        for pagina in self._extractor.iter_paginated(owner, repo, endpoint):
            for c in pagina:
                user = c.get("user") or {}
                login = user.get("login")
                if not self._es_humano(login, tipo=user.get("type")):
                    continue
                total += 1
                if login: por_autor[login] += 1
            vistos += len(pagina)
            print(f"    [{endpoint}] comentarios vistos: {vistos}")
            if limite and vistos >= limite:
                break
        return total, por_autor

    # ------------------------------------------------------------------ #
    # Canal de revisiones formales (GraphQL, recorriendo PRs)
    # ------------------------------------------------------------------ #
    def _contar_reviews(self, owner: str, repo: str, limite: int = None):
        total = 0
        por_autor = Counter()
        cursor = None
        prs_procesados = 0

        while True:
            data = self._extractor.graphql(
                _QUERY_REVIEWS, {"owner": owner, "repo": repo, "cursor": cursor}
            )
            if "errors" in data:
                raise RuntimeError(f"GraphQL devolvió errores: {data['errors']}")

            repo_data = (data.get("data") or {}).get("repository") or {}
            prs = repo_data.get("pullRequests") or {}

            for pr in prs.get("nodes", []):
                reviews = (pr.get("reviews") or {}).get("nodes", [])
                for r in reviews:
                    if r.get("state") == "PENDING":
                        continue
                    autor = r.get("author") or {}
                    login = autor.get("login")
                    if not self._es_humano(login, typename=autor.get("__typename")):
                        continue
                    total += 1
                    if login:
                        por_autor[login] += 1

                prs_procesados += 1
                if limite and prs_procesados >= limite:
                    return total, por_autor

            # progreso: para ver que está vivo
            print(f"    [reviews] PRs procesados: {prs_procesados}, reviews contadas: {total}")

            page = prs.get("pageInfo") or {}
            if not page.get("hasNextPage"):
                break
            cursor = page.get("endCursor")

        return total, por_autor

    # ------------------------------------------------------------------ #
    # Detección de bots
    # ------------------------------------------------------------------ #
    @staticmethod
    def _es_humano(login: str, tipo: str = None, typename: str = None) -> bool:
        """
        Devuelve False si la interacción es de un bot (se excluye del conteo).
        Combina tres señales: lista explícita, sufijo '[bot]' y el tipo que
        reporta la API (REST: user.type == 'Bot'; GraphQL: __typename == 'Bot').
        Un autor nulo (usuario borrado) se cuenta como humano pero no se atribuye
        a nadie en top_interactors.
        """
        if login and (login in BOTS_CONOCIDOS or login.endswith("[bot]")):
            return False
        if tipo == "Bot" or typename == "Bot":
            return False
        return True