from math import log2
from collections import Counter

from core.base import Metrica


class CommitEntropy(Metrica):
    nombre = "Entropía de Commits"
    descripcion = (
        "Mide la dispersión de los cambios en los commits usando la entropía de Shannon. "
        "Cuantifica la variabilidad en la cantidad de archivos modificados por commit."
    )
    dimension = ["Proceso"]
    interpretacion = (
        "Entropía baja: commits específicos y cohesivos que afectan pocos archivos. "
        "Entropía alta: commits dispersos que tocan muchos archivos distintos, "
        "lo que puede reflejar menor cohesión en los cambios."
    )

    def __init__(self, extractor):
        self._extractor = extractor

    def calcular(self, owner: str = None, repo: str = None, limite: int = None) -> dict:
        cache = self._extractor.load_cache("commit_entropy") if not limite else None
        last_sha = cache.get("last_sha") if cache else None
        cached_counts = cache.get("file_counts", []) if cache else []

        newest_sha = None
        new_counts = []
        for commit in self._extractor.iter_commits(limite=limite, since_sha=last_sha):
            if newest_sha is None:
                newest_sha = commit.hexsha
            new_counts.append(len(commit.stats.files))

        file_counts = new_counts + cached_counts

        if newest_sha and not limite:
            self._extractor.save_cache("commit_entropy", {
                "last_sha": newest_sha,
                "file_counts": file_counts,
            })

        if not file_counts:
            return {"entropy": 0.0}
        total = len(file_counts)
        freq = Counter(file_counts)
        entropy = -sum((c / total) * log2(c / total) for c in freq.values())
        return {"entropy": round(entropy, 4)}