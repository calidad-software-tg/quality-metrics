import subprocess
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.base import Metrica


class DeveloperOwnershipV2(Metrica):
    nombre = "Propiedad del Código por Desarrollador (local)"
    descripcion = (
        "Calcula el porcentaje de líneas de código atribuidas a cada autor "
        "usando git blame local sobre todos los archivos del repositorio."
    )
    dimension = ["Persona"]
    interpretacion = (
        "Un desarrollador con alta propiedad es el principal responsable de esa base de código. "
        "Concentración alta en un solo autor puede ser un riesgo si ese desarrollador abandona el proyecto."
    )

    def __init__(self, extractor):
        self._extractor = extractor

    def _blame_file(self, path: str) -> dict[str, int]:
        try:
            out = subprocess.run(
                ["git", "blame", "--line-porcelain", "HEAD", "--", path],
                cwd=self._extractor.repo_path(),
                capture_output=True, text=True, timeout=30
            ).stdout
            counts: dict[str, int] = defaultdict(int)
            for line in out.splitlines():
                if line.startswith("author ") and not line.startswith("author-"):
                    counts[line[7:]] += 1
            return dict(counts)
        except Exception:
            return {}

    def calcular(self, owner: str = None, repo: str = None, limite: int = None) -> dict:
        cache = self._extractor.load_cache("developer_ownership_v2") if not limite else None
        if cache:
            return cache.get("result", {})

        out = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "HEAD"],
            cwd=self._extractor.repo_path(),
            capture_output=True, text=True
        ).stdout
        files = [f for f in out.splitlines() if f]

        if limite:
            files = files[:limite]

        ownership: dict[str, int] = defaultdict(int)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(self._blame_file, f): f for f in files}
            for future in as_completed(futures):
                for author, lines in future.result().items():
                    ownership[author] += lines

        total = sum(ownership.values())
        if total == 0:
            return {}

        result = {
            a: round((l / total) * 100, 2)
            for a, l in sorted(ownership.items(), key=lambda x: -x[1])
        }

        if not limite:
            self._extractor.save_cache("developer_ownership_v2", {"result": result})

        return result
