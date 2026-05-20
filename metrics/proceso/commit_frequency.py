from collections import Counter

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

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        commits = self._extractor.get_commits(owner, repo, limite=limite)
        fechas = [c["commit"]["author"]["date"][:10] for c in commits]
        return dict(Counter(fechas))

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