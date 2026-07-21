"""
Developer Communication / Communication Activity (consigna 58, Registro 30)
---------------------------------------------------------------------------
"La comunicación efectiva entre los desarrolladores de su equipo".

Mide la ACTIVIDAD COMUNICACIONAL DIRIGIDA Y TÉCNICA entre desarrolladores y su
sostenimiento en el tiempo (no el volumen bruto, que ya cubre social_interaction
en la consigna 9; ni el tamaño de commits, que cubre developer_skill_communication
en la consigna 10).

Novedad respecto de versiones previas: filtra comunicación TÉCNICA vs. cortesía.
El escaneo exploratorio de tldr-pages mostró mucho ruido social ("thanks",
"lgtm", "nice one", "merged", emojis...) que no es comunicación técnica. El
clasificador de abajo separa una de otra; la ficha de Registro 30 pide justamente
"diferenciación entre comunicación técnica y no técnica".

Grafo dirigido: arista A -> B si A responde/menciona a B en un hilo de B, contando
SOLO interacciones técnicas. Sobre él: densidad, reciprocidad, actividad temporal.
Además reporta ratio_tecnico (qué fracción de la comunicación dirigida es técnica).
"""

import re
from collections import Counter

from core.base import Metrica

# ============================================================================ #
#  CLASIFICADOR TÉCNICO vs. NO TÉCNICO  (AJUSTABLE)
#  Léxico derivado del escaneo real de comentarios de tldr-pages.
#  Mové términos entre listas para recalibrar; es la parte pensada para tocar.
# ============================================================================ #

# Señales ESTRUCTURALES: si aparecen, el comentario es técnico casi con certeza.
_RE_BACKTICK  = re.compile(r"`")
_RE_CODEBLOCK = re.compile(r"```")
_RE_FLAG      = re.compile(r"(?<!\w)--?[a-zA-Z]")                 # -x  o  --flag
_RE_PATH      = re.compile(r"[\w./-]+/[\w./-]+|\b\w+\.(md|py|sh|js|json|yml|yaml)\b")
_RE_REF       = re.compile(r"#\d+")                               # #123
_RE_URL       = re.compile(r"https?://")
_RE_MENCION   = re.compile(r"@[a-z0-9-]+")

# Cortesía / reconocimiento / estado: NO es comunicación técnica.
_CORTESIA_1 = {
    "thanks", "thank", "thx", "ty", "lgtm", "nice", "great", "awesome", "perfect",
    "cool", "done", "fixed", "merged", "merging", "landed", "cheers", "sure", "ok",
    "okay", "yep", "yeah", "agree", "agreed", "indeed", "np", "shipit", "updated",
    "welcome", "wow", "ack", "definitely", "absolutely", "oops", "gracias", "listo",
    "dale", "bienvenido",
    # "palabras-emoji" que GitHub renderiza como :emoji:
    "thumbsup", "thumbsdown", "heart", "sparkles", "eyes", "smile", "smiley",
    "tada", "hooray", "clap", "rocket", "fire", "raisedhands",
}
_CORTESIA_FRASE = (
    "thank you", "good catch", "good one", "good point", "good idea", "good pickup",
    "no problem", "no problemo", "no worries", "fair enough", "sounds good",
    "looks great", "looks good", "look great", "same here", "same as above",
    "same comment as above", "will fix", "will do", "nice one", "nice work",
    "nice catch", "you are welcome", "merry christmas", "good start",
)

# Palabras vacías: no cuentan como "contenido sustantivo".
_STOP = {
    "a", "an", "the", "this", "that", "it", "is", "are", "was", "were", "be", "to",
    "for", "of", "in", "on", "and", "or", "but", "i", "you", "we", "they", "he",
    "she", "my", "your", "its", "as", "at", "so", "if", "then", "me", "us", "them",
    "do", "did", "does", "can", "could", "would", "should", "will", "im", "ive",
    "id", "ill", "here", "there", "now", "just", "all", "any", "some", "one",
    "please", "lets", "let", "with", "from", "by", "about", "up", "out", "not",
    "no", "yes", "these", "those", "have", "has", "had", "get", "got", "too",
    "also", "very", "much", "more", "been", "being", "than", "when", "what",
}


def _normalizar(body: str) -> str:
    t = body.lower()
    t = _RE_MENCION.sub(" ", t)               # saca @menciones
    t = _RE_REF.sub(" ", t)                   # saca #123
    t = re.sub(r"[^\w\s]", " ", t)            # saca puntuación/emojis unicode
    return re.sub(r"\s+", " ", t).strip()


def es_tecnico(body: str) -> bool:
    """
    True  -> comunicación técnica (discusión sobre código, páginas, problemas...)
    False -> cortesía / reconocimiento / coordinación trivial.
    Heurística de dos capas (ver escaneo): estructura fuerte gana; si no,
    se decide por cuánto contenido sustantivo queda al sacar la cortesía.
    """
    if not body or not body.strip():
        return False

    # Capa 1: señal estructural -> técnico seguro.
    if (_RE_BACKTICK.search(body) or _RE_CODEBLOCK.search(body)
            or _RE_FLAG.search(body) or _RE_PATH.search(body)
            or _RE_URL.search(body)):
        return True

    norm = _normalizar(body)
    if not norm:
        return False

    # Sacar primero las FRASES de cortesía completas (si no, sus palabras
    # quedarían contadas como contenido: "good catch", "same as above"...).
    norm_sin = norm
    tiene_frase = False
    for f in _CORTESIA_FRASE:
        if f in norm_sin:
            tiene_frase = True
            norm_sin = norm_sin.replace(f, " ")
    tokens = norm_sin.split()

    tiene_cortesia = tiene_frase or any(tok in _CORTESIA_1 for tok in tokens)

    # Contenido sustantivo = tokens que no son cortesía, ni stopword, ni número.
    contenido = [
        tok for tok in tokens
        if tok not in _CORTESIA_1 and tok not in _STOP and not tok.isdigit()
    ]

    # Capa 2: si es cortesía y casi no queda contenido -> no técnico.
    if tiene_cortesia and len(contenido) <= 1:
        return False
    # Prosa con contenido real (aunque abra con "thanks") -> técnico.
    return len(contenido) >= 2

# ============================================================================ #

BOTS_CONOCIDOS = {
    "github-actions[bot]", "dependabot[bot]", "dependabot-preview[bot]",
    "renovate[bot]", "codecov[bot]", "stale[bot]", "mergify[bot]",
    "allcontributors[bot]", "tldr-bot",
}
_MENCION = re.compile(r"@([A-Za-z0-9](?:[A-Za-z0-9-]{0,38})?)")


def _is_bot(login: str) -> bool:
    if not login:
        return True
    l = login.lower()
    return l.endswith("[bot]") or l in BOTS_CONOCIDOS or l == "tldr-bot"


def _num_hilo(url: str):
    if not url:
        return None
    try:
        return int(url.rstrip("/").split("/")[-1])
    except (ValueError, IndexError):
        return None


def _meses_entre(a: str, b: str) -> int:
    ya, ma = int(a[:4]), int(a[5:7])
    yb, mb = int(b[:4]), int(b[5:7])
    return (yb - ya) * 12 + (mb - ma) + 1


class DeveloperCommunicationActivity(Metrica):

    nombre = "Developer Communication"
    descripcion = (
        "Mide la actividad comunicacional dirigida y TÉCNICA entre desarrolladores "
        "(quién coordina con quién, filtrando cortesía) y su sostenimiento temporal."
    )
    dimension = ["Proceso", "Persona"]
    interpretacion = (
        "Alta densidad/reciprocidad técnica indica coordinación distribuida y real; "
        "alta consistencia temporal, comunicación sostenida. ratio_tecnico muestra "
        "qué parte del diálogo es técnica vs. social. Fidelidad baja."
    )

    def __init__(self, extractor, solo_tecnicas: bool = True):
        # solo_tecnicas=True -> el grafo se construye con interacciones técnicas.
        self._extractor = extractor
        self._solo_tecnicas = solo_tecnicas

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        ext = self._extractor

        autor_hilo = {}
        for it in ext.get_paginated(owner, repo, "issues", {"state": "all"},
                                    max_items=limite):
            n = it.get("number")
            if n is not None:
                autor_hilo[n] = (it.get("user") or {}).get("login")

        comentarios = []
        for c in ext.get_paginated(owner, repo, "issues/comments", max_items=limite):
            comentarios.append((c, c.get("issue_url")))
        for c in ext.get_paginated(owner, repo, "pulls/comments", max_items=limite):
            comentarios.append((c, c.get("pull_request_url")))

        conocidos = {
            (c.get("user") or {}).get("login")
            for c, _ in comentarios
            if not _is_bot((c.get("user") or {}).get("login"))
        }
        conocidos |= {a for a in autor_hilo.values() if a and not _is_bot(a)}

        aristas = Counter()      # grafo de interacciones TÉCNICAS (o todas, según flag)
        meses = Counter()
        dirigidas_total = 0
        dirigidas_tecnicas = 0

        for c, url in comentarios:
            emisor = (c.get("user") or {}).get("login")
            if _is_bot(emisor):
                continue

            receptores = set()
            autor = autor_hilo.get(_num_hilo(url))
            if autor and not _is_bot(autor) and autor != emisor:
                receptores.add(autor)
            for m in _MENCION.findall(c.get("body") or ""):
                if m != emisor and not _is_bot(m) and m in conocidos:
                    receptores.add(m)
            if not receptores:
                continue

            tecnico = es_tecnico(c.get("body") or "")
            fecha = (c.get("created_at") or "")[:7]

            for receptor in receptores:
                dirigidas_total += 1
                if tecnico:
                    dirigidas_tecnicas += 1
                # el grafo/temporal usa técnicas si el flag está activo
                if tecnico or not self._solo_tecnicas:
                    aristas[(emisor, receptor)] += 1
                    if fecha:
                        meses[fecha] += 1

        pares = set(aristas)
        reciprocos = sum(1 for (a, b) in pares if (b, a) in pares)
        nodos = {x for par in pares for x in par}
        n = len(nodos)
        posibles = n * (n - 1) if n > 1 else 1

        if meses:
            claves = sorted(meses)
            span = _meses_entre(claves[0], claves[-1])
            activos = len(meses)
        else:
            span, activos = 0, 0

        return {
            "metrica": self.nombre,
            "consigna_id": 58,
            "base_grafo": "tecnicas" if self._solo_tecnicas else "todas",
            "interacciones_dirigidas_total": dirigidas_total,
            "interacciones_dirigidas_tecnicas": dirigidas_tecnicas,
            "ratio_tecnico": round(dirigidas_tecnicas / (dirigidas_total or 1), 4),
            "pares_coordinados": len(pares),
            "desarrolladores_involucrados": n,
            "densidad_coordinacion": round(len(pares) / posibles, 4),
            "reciprocidad": round(reciprocos / (len(pares) or 1), 4),
            "meses_activos": activos,
            "actividad_por_mes_activo": round(
                sum(meses.values()) / (activos or 1), 2),
            "consistencia_temporal": round(activos / (span or 1), 4),
            "fidelidad": "baja",
            "inferencia": "inferida",
        }


if __name__ == "__main__":
    import os
    from core.github_extractor import GitHubExtractor

    ext = GitHubExtractor(os.environ.get("GITHUB_TOKEN", ""), "https://api.github.com")
    print(DeveloperCommunicationActivity(ext).calcular("tldr-pages", "tldr", limite=500))