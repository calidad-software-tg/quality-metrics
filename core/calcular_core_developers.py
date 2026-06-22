"""
Genera la lista candidata de core developers de tldr-pages/tldr y la exporta a CSV
para que Esteban la revise. Cada fila trae la evidencia (en qué fuente aparece +
cuántos PRs mergeó), así él solo marca quién es core y quién no.

Uso:
    python calcular_core_developers.py                 # histórico completo
    python calcular_core_developers.py --limite 500    # prueba rápida (PRs recientes)

Después de la revisión de Esteban, la lista validada se pasa a la métrica:
    UserReportedBugs(gh, core_developers=[...logins confirmados...])
"""
import argparse
import csv
import os

from core.github_extractor import GitHubExtractor
from core.core_developers import CoreDevelopersResolver
from config.settings import GITHUB_TOKEN, GITHUB_API_BASE

ORIGINAL_OWNER = "tldr-pages"
ORIGINAL_REPO = "tldr"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limite", type=int, default=None,
                        help="tope de PRs a recorrer (prueba); omitir para histórico completo")
    parser.add_argument("--salida", default="core_developers_candidatos.csv")
    args = parser.parse_args()

    gh = GitHubExtractor(GITHUB_TOKEN, GITHUB_API_BASE)
    resolver = CoreDevelopersResolver(gh)

    print(f"Calculando core developers de {ORIGINAL_OWNER}/{ORIGINAL_REPO} "
          f"(limite={args.limite})...")
    r = resolver.resolver(ORIGINAL_OWNER, ORIGINAL_REPO, limite=args.limite)

    print(f"\nFuentes: {r['fuentes']}")
    print(f"Total de candidatos: {r['total_candidatos']}\n")

    with open(args.salida, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["login", "in_maintainers_doc", "in_codeowners",
                         "prs_merged", "es_core_REVISAR"])
        for c in r["candidatos"]:
            writer.writerow([c["login"], c["in_maintainers_doc"],
                             c["in_codeowners"], c["prs_merged"], ""])

    print(f"CSV escrito en: {os.path.abspath(args.salida)}")
    print("La columna 'es_core_REVISAR' queda vacía para que Esteban la complete (sí/no).")

    # vista previa: top 15 por PRs mergeados
    print("\nTop 15 candidatos por PRs mergeados:")
    print(f"  {'login':<25} {'doc':<6} {'codeo':<6} {'PRs':>6}")
    for c in r["candidatos"][:15]:
        print(f"  {c['login']:<25} "
              f"{('sí' if c['in_maintainers_doc'] else '-'):<6} "
              f"{('sí' if c['in_codeowners'] else '-'):<6} "
              f"{c['prs_merged']:>6}")


if __name__ == "__main__":
    main()