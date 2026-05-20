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

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        commits = self._extractor.get_commits(owner, repo, limite=limite)
        file_counts = [
            len(self._extractor.get_commit_files(c["url"]))
            for c in commits
        ]
        if not file_counts:
            return {"entropy": 0.0}

        total = len(file_counts)
        freq = Counter(file_counts)
        entropy = -sum((c / total) * log2(c / total) for c in freq.values())
        return {"entropy": round(entropy, 4)}