from collections import Counter
from datetime import timezone

import matplotlib.pyplot as plt

from core.base import Metrica


class CommitFrequency(Metrica):
    nombre = "Frecuencia de Commits"
    descripcion = (
        "Cuenta la cantidad de commits por día en el repositorio. "
        "Permite observar la cadencia y regularidad del trabajo del equipo."
    )
    dimension = ["Proceso"]
    interpretacion = (
        "Una frecuencia regular indica un equipo con ritmo sostenido. "
        "Picos aislados pueden reflejar sprints intensos o acumulación de trabajo."
    )

    def __init__(self, extractor):
        self._extractor = extractor

    def calcular(self, owner: str = None, repo: str = None, limite: int = None) -> dict:
        cache = self._extractor.load_cache("commit_frequency") if not limite else None
        last_sha = cache.get("last_sha") if cache else None
        cached_dates = cache.get("dates", []) if cache else []

        newest_sha = None
        new_dates = []
        for commit in self._extractor.iter_commits(limite=limite, since_sha=last_sha):
            if newest_sha is None:
                newest_sha = commit.hexsha
            dt = commit.committed_datetime.astimezone(timezone.utc)
            new_dates.append(dt.strftime("%Y-%m-%d"))

        all_dates = new_dates + cached_dates

        if newest_sha and not limite:
            self._extractor.save_cache("commit_frequency", {
                "last_sha": newest_sha,
                "dates": all_dates,
            })

        return dict(Counter(all_dates))

    def graficar(self, frecuencia: dict, titulo: str = "Frecuencia de Commits por Día"):
        fechas, conteos = zip(*sorted(frecuencia.items()))
        plt.figure(figsize=(10, 6))
        plt.bar(fechas, conteos)
        plt.xlabel("Fecha")
        plt.ylabel("Número de Commits")
        plt.title(titulo)
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.show()