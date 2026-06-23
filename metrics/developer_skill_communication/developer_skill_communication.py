"""
Developer Skill Communication - Versión 1: FIXED PARSING
Con el error de parsing corregido
"""

from datetime import datetime
from typing import Dict, List
import statistics
import json
from pathlib import Path
import sys
import subprocess


class DeveloperSkillCommunicationV1Fixed:
    """
    Calcula la habilidad de comunicación del desarrollador mediante análisis
    de mensajes de commit obtenidos desde Git metadata.

    VERSIÓN CORREGIDA: El parsing de git log ahora es correcto
    """

    def __init__(self, repo_path: str, verbose=True):
        """
        Args:
            repo_path: Ruta local del repositorio clonado
            verbose: Mostrar información de debug
        """
        self.repo_path = Path(repo_path).expanduser().resolve()
        self.verbose = verbose

        if not self.repo_path.exists():
            raise ValueError(f"Ruta no existe: {self.repo_path}")

        if not (self.repo_path / '.git').exists():
            raise ValueError(f"No es un repositorio Git: {self.repo_path}")

        self._print(f"✓ Repositorio encontrado: {self.repo_path}")

    def _print(self, msg):
        """Imprime si verbose está activo"""
        if self.verbose:
            print(msg)

    def _get_commits_via_git(self) -> List[Dict]:
        """
        Extrae commits del repositorio local usando git log.
        VERSIÓN ARREGLADA CON PARSING CORRECTO
        """
        self._print("\n📥 Extrayendo commits del repositorio...")

        # Usar un formato más simple y seguro
        # %H = hash, %an = autor, %ae = email, %aI = fecha ISO, %B = mensaje completo
        # Delimitador entre commits
        format_str = "%H%n%an%n%ae%n%aI%n%B%n==END_COMMIT=="

        try:
            self._print("  → Ejecutando: git log...")
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "log", f"--format={format_str}"],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                raise RuntimeError(f"Git error: {result.stderr}")

            self._print("  → Parseando commits...")
            commits = []

            # Separar por delimitador de fin de commit
            for commit_block in result.stdout.split("==END_COMMIT=="):
                commit_block = commit_block.strip()
                if not commit_block:
                    continue

                # Separar líneas
                lines = commit_block.split('\n')

                # Esperamos al menos 5 líneas: hash, author, email, date, + al menos 1 línea de mensaje
                if len(lines) < 5:
                    continue

                try:
                    commit_hash = lines[0].strip()
                    author = lines[1].strip()
                    email = lines[2].strip()
                    date = lines[3].strip()
                    message = '\n'.join(lines[4:]).strip()

                    # Validación: author no debe estar vacío
                    if not author or not commit_hash:
                        self._print(f"⚠️ Commit inválido (sin autor o hash): {commit_hash[:8] if commit_hash else 'unknown'}")
                        continue

                    # Contar líneas del mensaje
                    message_lines = len([l for l in message.split('\n') if l.strip()])

                    commits.append({
                        'hash': commit_hash,
                        'author': author,
                        'email': email,
                        'date': date,
                        'message': message,
                        'message_lines': message_lines,
                        'message_length': len(message)
                    })

                except Exception as e:
                    self._print(f"⚠️ Error parseando commit: {e}")
                    continue

            self._print(f"  ✓ Total commits extraídos: {len(commits)}")

            if len(commits) == 0:
                self._print("❌ No se encontraron commits válidos")

            return commits

        except Exception as e:
            self._print(f"❌ Error extrayendo commits: {str(e)}")
            raise

    def calcular(self) -> Dict:
        """
        Calcula estadísticas de habilidad de comunicación por desarrollador.
        """
        commits = self._get_commits_via_git()

        if not commits:
            self._print("⚠️ No se encontraron commits")
            return {
                "status": "no_commits",
                "total_commits": 0,
                "total_developers": 0,
                "developers": {}
            }

        self._print(f"\n📊 Procesando {len(commits)} commits...")

        # Agrupar por desarrollador
        developers: Dict[str, List[Dict]] = {}

        for commit in commits:
            author = commit['author']
            if author not in developers:
                developers[author] = []
            developers[author].append(commit)

        self._print(f"  ✓ Total desarrolladores: {len(developers)}")

        # Calcular estadísticas por desarrollador
        self._print("\n📈 Calculando estadísticas...")
        developer_stats = {}
        all_message_lines = []

        for author, author_commits in developers.items():
            message_lines = [c['message_lines'] for c in author_commits]
            message_lengths = [c['message_length'] for c in author_commits]

            all_message_lines.extend(message_lines)

            developer_stats[author] = {
                'total_commits': len(author_commits),
                'total_message_lines': sum(message_lines),
                'average_message_lines': statistics.mean(message_lines),
                'median_message_lines': statistics.median(message_lines),
                'min_message_lines': min(message_lines),
                'max_message_lines': max(message_lines),
                'total_message_chars': sum(message_lengths),
                'average_message_chars': statistics.mean(message_lengths),
                'first_commit': min([c['date'] for c in author_commits]),
                'last_commit': max([c['date'] for c in author_commits]),
            }

        self._print("  ✓ Estadísticas calculadas")

        # Estadísticas globales
        resultado = {
            "status": "success",
            "total_commits": len(commits),
            "total_developers": len(developers),
            "total_message_lines": sum(all_message_lines),
            "average_message_lines_per_commit": statistics.mean(all_message_lines),
            "median_message_lines_per_commit": statistics.median(all_message_lines),
            "developers": developer_stats,
            "top_communicators": sorted(
                [(author, stats['average_message_lines'])
                 for author, stats in developer_stats.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }

        return resultado

    def calcular_y_exportar(self, output_file: str = None) -> Dict:
        """
        Calcula la métrica y exporta resultados a JSON.
        """
        print("\n" + "="*70)
        print("DEVELOPER SKILL COMMUNICATION - Versión 1 (FIXED)")
        print("Métrica: Habilidad de comunicación mediante mensajes de commit")
        print("="*70)

        resultado = self.calcular()

        if resultado['status'] == 'success':
            print("\n" + "-"*70)
            print("📊 RESULTADOS GLOBALES")
            print("-"*70)
            print(f"Total commits:              {resultado['total_commits']:,}")
            print(f"Total desarrolladores:      {resultado['total_developers']}")
            print(f"Total líneas en mensajes:   {resultado['total_message_lines']:,}")
            print(f"Promedio líneas/commit:     {resultado['average_message_lines_per_commit']:.2f}")
            print(f"Mediana líneas/commit:      {resultado['median_message_lines_per_commit']:.2f}")

            print("\n" + "-"*70)
            print("🏆 TOP 10 COMUNICADORES (promedio líneas por commit)")
            print("-"*70)
            for i, (author, avg_lines) in enumerate(resultado['top_communicators'], 1):
                commits = resultado['developers'][author]['total_commits']
                print(f"{i:2d}. {author:40s} → {avg_lines:6.2f} líneas/commit ({commits:5d} commits)")

            print("\n" + "-"*70)
            print("📝 DETALLES DE TOP 3 DESARROLLADORES")
            print("-"*70)
            for i, (author, _) in enumerate(resultado['top_communicators'][:3]):
                stats = resultado['developers'][author]
                print(f"\n{i+1}. {author}")
                print(f"   Commits: {stats['total_commits']}")
                print(f"   Líneas totales: {stats['total_message_lines']}")
                print(f"   Promedio: {stats['average_message_lines']:.2f} líneas/commit")
                print(f"   Rango: {stats['min_message_lines']} - {stats['max_message_lines']} líneas")
                print(f"   Período: {stats['first_commit'][:10]} → {stats['last_commit'][:10]}")

        else:
            print("⚠️ No se encontraron commits en el repositorio")

        # Exportar a JSON si se especifica
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)
            print(f"\n✓ Resultados exportados a: {output_path}")

        print("\n" + "="*70 + "\n")

        return resultado


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python developer_skill_communication_v1_fixed.py <repo_path> [output_file]")
        print("\nEjemplos:")
        print("  python developer_skill_communication_v1_fixed.py /Users/luzlaura/projects/tesis/tldr")
        print("  python developer_skill_communication_v1_fixed.py /Users/luzlaura/projects/tesis/tldr resultados.json")
        sys.exit(1)

    repo_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        metric = DeveloperSkillCommunicationV1Fixed(repo_path, verbose=True)
        resultado = metric.calcular_y_exportar(output_file)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nConsejo: Verifica que la ruta es correcta:")
        print(f"  ls -la '{repo_path}'")
        sys.exit(1)