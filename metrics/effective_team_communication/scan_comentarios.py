"""
Escaneo exploratorio de comentarios (paso previo a diferenciar comunicación
técnica vs. no técnica en la métrica 58).

VERSIÓN LIVIANA Y ROBUSTA:
  - baja solo una MUESTRA (suficiente para decidir el criterio),
  - timeout en cada request (no se cuelga como la versión anterior),
  - maneja rate limit sin trabarse,
  - cachea lo bajado en disco (re-correr es instantáneo).

Uso (desde la raíz del proyecto quality-metrics):
    python -m metrics.effective_team_communication.scan_comentarios

Toma el token de config/settings.py.
Salida en ./scan_out/: comentarios_features.csv, resumen.csv,
top_frases_cortas.csv, muestra_por_grupo.csv
"""

import re
import csv
import json
import time
import random
import unicodedata
from collections import Counter
from pathlib import Path

import requests
from config.settings import GITHUB_TOKEN, GITHUB_API_BASE

OWNER, REPO = "tldr-pages", "tldr"

# --- perillas -----------------------------------------------------------------
# Muestra por canal. 15 páginas x 100 = 1500 comentarios por canal (~1 min total).
# Para explorar el criterio con esto sobra. Subilo si querés más volumen.
PAGINAS_POR_CANAL = 15
TIMEOUT = 30           # segundos por request; corta cuelgues
# ------------------------------------------------------------------------------

OUT = Path(__file__).resolve().parent / "scan_out"
CACHE = OUT / "cache"

BOTS_CONOCIDOS = {
    "github-actions[bot]", "dependabot[bot]", "dependabot-preview[bot]",
    "renovate[bot]", "codecov[bot]", "stale[bot]", "mergify[bot]",
    "allcontributors[bot]", "tldr-bot",
}

RE_BACKTICK  = re.compile(r"`")
RE_CODEBLOCK = re.compile(r"```")
RE_FLAG      = re.compile(r"(?<!\w)--?[a-zA-Z]")
RE_PATH      = re.compile(r"[\w./-]+/[\w./-]+|\b\w+\.(md|py|sh|js|json|yml|yaml)\b")
RE_ISSUE_REF = re.compile(r"#\d+")
RE_URL       = re.compile(r"https?://")
RE_MENCION   = re.compile(r"@[A-Za-z0-9-]+")
TECH_KW = {
    "bug", "fix", "error", "fails", "failing", "broken", "syntax", "command",
    "flag", "option", "example", "page", "pages", "output", "argument", "typo",
    "conflict", "rebase", "merge", "test", "tests", "translation", "format",
    "linux", "macos", "windows", "osx", "android", "code", "escape", "placeholder",
}
COURTESY = {
    "thanks", "thank you", "thank u", "thx", "ty", "lgtm", "welcome",
    "great", "nice", "awesome", "perfect", "cool", "done", "merged", "np",
    "no problem", "cheers", "sure", "ok", "okay", "yes", "no", "agreed",
    "good catch", "good point", "fixed", "gracias", "listo", "dale", "bienvenido",
}


# --- descarga robusta ---------------------------------------------------------
def bajar_muestra(session, endpoint, max_paginas):
    url = f"{GITHUB_API_BASE}/repos/{OWNER}/{REPO}/{endpoint}"
    params = {"per_page": 100}
    out, pagina = [], 0
    while url and pagina < max_paginas:
        # hasta 4 intentos por página (502/503/504 y cortes de red son transitorios)
        r = None
        for intento in range(4):
            try:
                r = session.get(url, params=params, timeout=TIMEOUT)
            except requests.exceptions.RequestException as e:
                espera = 2 ** intento
                print(f"     error de red ({e}); reintento en {espera}s...")
                time.sleep(espera)
                continue

            # rate limit: esperar o abortar, sin colgarse
            if r.status_code == 403 and "rate limit" in r.text.lower():
                reset = r.headers.get("X-RateLimit-Reset")
                espera = max(0, int(reset) - int(time.time())) if reset else 60
                if espera > 120:
                    print(f"     rate limit alto ({espera}s); corto con lo que tengo.")
                    return out
                print(f"     rate limit; espero {espera}s...")
                time.sleep(espera + 1)
                continue

            # errores transitorios del servidor: reintentar con backoff
            if r.status_code in (502, 503, 504):
                espera = 2 ** intento
                print(f"     {r.status_code} transitorio; reintento en {espera}s...")
                time.sleep(espera)
                continue

            break  # respuesta OK (o error no transitorio)

        if r is None:
            print("     no se pudo tras varios intentos; corto con lo que tengo.")
            break
        if r.status_code in (502, 503, 504):
            print("     el servidor sigue fallando; corto con lo que tengo.")
            break
        r.raise_for_status()

        out.extend(r.json())
        pagina += 1
        print(f"     {len(out)} comentarios...", end="\r")
        url = r.links.get("next", {}).get("url")
        params = None
    print(f"     {len(out)} comentarios          ")
    return out


def _is_bot(login, tipo):
    if not login:
        return True
    l = login.lower()
    return tipo == "Bot" or l.endswith("[bot]") or l in BOTS_CONOCIDOS


def _norm(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^\w\s]", "", t.lower().strip())
    return re.sub(r"\s+", " ", t).strip()


def _bucket_long(wc):
    if wc <= 2:  return "1-2 palabras"
    if wc <= 5:  return "3-5 palabras"
    if wc <= 15: return "6-15 palabras"
    if wc <= 40: return "16-40 palabras"
    return "40+ palabras"


def _clasif(has_tech, cortesia_pura):
    if has_tech and not cortesia_pura: return "tecnico"
    if cortesia_pura and not has_tech: return "no_tecnico"
    return "ambiguo"


def analizar(c, canal):
    login = (c.get("user") or {}).get("login")
    tipo  = (c.get("user") or {}).get("type")
    body  = c.get("body") or ""
    norm  = _norm(body)
    wc    = len(norm.split()) if norm else 0

    has_backtick  = bool(RE_BACKTICK.search(body))
    has_codeblock = bool(RE_CODEBLOCK.search(body))
    has_flag      = bool(RE_FLAG.search(body))
    has_path      = bool(RE_PATH.search(body))
    kw_hits       = sum(1 for w in norm.split() if w in TECH_KW)
    has_tech = has_backtick or has_codeblock or has_flag or has_path or kw_hits >= 1
    cortesia_pura = (wc <= 4 and not has_tech
                     and (norm in COURTESY or any(p in norm for p in COURTESY)))

    return {
        "canal": canal, "autor": login or "", "es_bot": _is_bot(login, tipo),
        "fecha": (c.get("created_at") or "")[:10],
        "palabras": wc, "caracteres": len(body), "bucket_long": _bucket_long(wc),
        "backticks": int(has_backtick), "codeblock": int(has_codeblock),
        "flag_cli": int(has_flag), "ruta_archivo": int(has_path),
        "ref_issue": int(bool(RE_ISSUE_REF.search(body))),
        "url": int(bool(RE_URL.search(body))),
        "mencion": int(bool(RE_MENCION.search(body))),
        "kw_tecnicas": kw_hits, "senal_tecnica": int(has_tech),
        "cortesia_pura": int(cortesia_pura),
        "clasif_heuristica": _clasif(has_tech, cortesia_pura),
        "texto": re.sub(r"\s+", " ", body).strip()[:300], "_norm": norm,
    }


def main():
    OUT.mkdir(exist_ok=True); CACHE.mkdir(exist_ok=True)
    session = requests.Session()
    session.headers.update({"Authorization": f"token {GITHUB_TOKEN}",
                            "Accept": "application/vnd.github+json"})

    print(f"Muestreando comentarios de {OWNER}/{REPO} "
          f"(~{PAGINAS_POR_CANAL*100} por canal)...")
    filas = []
    for canal, endpoint in [("issue", "issues/comments"), ("pr", "pulls/comments")]:
        cache_file = CACHE / f"{canal}_{PAGINAS_POR_CANAL}.json"
        if cache_file.exists():
            crudos = json.loads(cache_file.read_text(encoding="utf-8"))
            print(f"  -> {endpoint}: {len(crudos)} desde cache")
        else:
            print(f"  -> {endpoint} (descargando)...")
            crudos = bajar_muestra(session, endpoint, PAGINAS_POR_CANAL)
            cache_file.write_text(json.dumps(crudos), encoding="utf-8")
        filas += [analizar(c, canal) for c in crudos]

    total = len(filas)
    humanos = [f for f in filas if not f["es_bot"]]
    print(f"Total: {total} | humanos: {len(humanos)} | bots: {total - len(humanos)}")
    if not humanos:
        print("No hubo comentarios humanos en la muestra."); return

    campos = [k for k in filas[0] if k != "_norm"]
    with open(OUT / "comentarios_features.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos); w.writeheader()
        for f in filas: w.writerow({k: f[k] for k in campos})

    resumen = [("total_comentarios", total), ("humanos", len(humanos)),
               ("bots", total - len(humanos))]
    for k, v in Counter(f["bucket_long"] for f in humanos).most_common():
        resumen.append((f"long::{k}", v))
    for k, v in Counter(f["clasif_heuristica"] for f in humanos).most_common():
        resumen.append((f"clasif::{k}", v))
    for col in ("senal_tecnica", "cortesia_pura", "backticks", "codeblock",
                "flag_cli", "mencion"):
        resumen.append((f"con_{col}", sum(f[col] for f in humanos)))
    with open(OUT / "resumen.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["indicador", "valor"]); w.writerows(resumen)

    cortas = Counter(f["_norm"] for f in humanos if 0 < f["palabras"] <= 6 and f["_norm"])
    with open(OUT / "top_frases_cortas.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["frase_normalizada", "veces"])
        for frase, n in cortas.most_common(150): w.writerow([frase, n])

    random.seed(42)
    with open(OUT / "muestra_por_grupo.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(["grupo", "palabras", "senal_tecnica", "texto"])
        for grupo in ("tecnico", "no_tecnico", "ambiguo"):
            pool = [f for f in humanos if f["clasif_heuristica"] == grupo]
            for f in random.sample(pool, min(40, len(pool))):
                w.writerow([grupo, f["palabras"], f["senal_tecnica"], f["texto"]])

    print(f"\nListo. CSVs en: {OUT.resolve()}")
    print("Mirá primero resumen.csv y top_frases_cortas.csv.")


if __name__ == "__main__":
    main()