from statistics import mean

from core.base import Metrica
from core.git_extractor import GitExtractor


class CentralizationOfWork(Metrica):
    nombre = "Centralización del Trabajo"
    descripcion = (
        "Coeficiente de Gini aplicado sobre la distribución de commits por autor. "
        "Cuantifica el grado de concentración del trabajo entre los colaboradores."
    )
    dimension = ["Proceso", "Persona"]
    interpretacion = (
        "G → 0: trabajo distribuido equitativamente. "
        "G → 1: todo el trabajo concentrado en un único desarrollador. "
        "Valores altos (> 0.80) correlacionan positivamente con tasas de cierre "
        "de issues a largo plazo (Jarczyk et al., 2018)."
    )

    def __init__(self, extractor: GitExtractor):
        self._extractor = extractor

    def calcular(self, owner: str = None, repo: str = None, limite: int = None) -> dict:
        cache = self._extractor.load_cache("centralization_of_work") if not limite else None
        last_sha = cache.get("last_sha") if cache else None
        counts = dict(cache.get("commits_per_contributor", {})) if cache else {}

        newest_sha = None
        for commit in self._extractor.iter_commits(limite=limite, since_sha=last_sha):
            if newest_sha is None:
                newest_sha = commit.hexsha
            author = commit.author.name or "unknown"
            counts[author] = counts.get(author, 0) + 1

        if newest_sha and not limite:
            self._extractor.save_cache("centralization_of_work", {
                "last_sha": newest_sha,
                "commits_per_contributor": counts,
            })

        if not counts:
            return {"n_contributors": 0, "commits_per_contributor": {}, "gini_commits": 0.0}

        y = sorted(counts.values())
        n = len(y)
        y_mean = mean(y)
        gini = sum((2 * i - n - 1) * yi for i, yi in enumerate(y, start=1)) / (n ** 2 * y_mean)

        return {
            "n_contributors": n,
            "commits_per_contributor": counts,
            "gini_commits": round(gini, 4),
        }