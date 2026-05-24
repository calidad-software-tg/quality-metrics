from core.base import Metrica


class DeveloperContribution(Metrica):
    nombre = "Contribución por Desarrollador"
    descripcion = (
        "Cuenta cuántos commits realizó cada autor en el repositorio. "
        "Permite analizar la distribución del trabajo entre colaboradores."
    )
    dimension = ["Persona"]
    interpretacion = (
        "Una distribución muy desigual puede indicar dependencia de pocos autores (bus factor alto). "
        "Una distribución uniforme refleja colaboración balanceada entre el equipo."
    )

    def __init__(self, extractor):
        self._extractor = extractor

    def calcular(self, owner: str = None, repo: str = None, limite: int = None) -> dict:
        cache = self._extractor.load_cache("developer_contribution") if not limite else None
        last_sha = cache.get("last_sha") if cache else None
        counts = dict(cache.get("counts", {})) if cache else {}

        newest_sha = None
        for commit in self._extractor.iter_commits(limite=limite, since_sha=last_sha):
            if newest_sha is None:
                newest_sha = commit.hexsha
            author = commit.author.name
            counts[author] = counts.get(author, 0) + 1

        if newest_sha and not limite:
            self._extractor.save_cache("developer_contribution", {
                "last_sha": newest_sha,
                "counts": counts,
            })

        return counts