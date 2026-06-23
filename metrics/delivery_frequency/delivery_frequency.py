"""
Commit Frequency - Frecuencia de Entregas Exitosas
Métrica C29: Frecuencia de entregas exitosas

Calcula la frecuencia de commits (incorporación de cambios) en el repositorio.
Proxy para "Frecuencia de entregas exitosas".
"""

from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict
import statistics
import json
from pathlib import Path
import sys
import subprocess
from dateutil import parser as date_parser


class CommitFrequency:
    """
    Calcula la frecuencia de commits en el repositorio.

    Representa la frecuencia con la que se incorporan cambios,
    usada como proxy para "frecuencia de entregas exitosas".
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

    def _get_commits_with_dates(self) -> List[Dict]:
        """
        Extrae commits con sus fechas.
        """
        self._print("\n📥 Extrayendo commits con fechas...")

        format_str = "%aI%n%an"  # ISO date y autor
        delimiter = "==END_COMMIT=="

        try:
            self._print("  → Ejecutando: git log...")
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "log", f"--format={format_str}{delimiter}"],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                raise RuntimeError(f"Git error: {result.stderr}")

            self._print("  → Parseando commits...")
            commits = []

            for commit_block in result.stdout.split(delimiter):
                commit_block = commit_block.strip()
                if not commit_block:
                    continue

                lines = commit_block.split('\n')
                if len(lines) >= 2:
                    try:
                        date_str = lines[0].strip()
                        author = lines[1].strip()

                        # Parsear fecha ISO
                        try:
                            # Intentar con dateutil
                            commit_date = date_parser.isoparse(date_str)
                        except:
                            # Fallback a datetime estándar
                            commit_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))

                        commits.append({
                            'date': commit_date,
                            'author': author,
                            'date_str': date_str
                        })
                    except Exception as e:
                        self._print(f"⚠️ Error parseando fecha: {date_str}")
                        continue

            self._print(f"  ✓ Total commits extraídos: {len(commits)}")
            return sorted(commits, key=lambda x: x['date'])

        except Exception as e:
            self._print(f"❌ Error extrayendo commits: {str(e)}")
            raise

    def calcular(self) -> Dict:
        """
        Calcula estadísticas de frecuencia de commits.
        """
        commits = self._get_commits_with_dates()

        if not commits:
            self._print("⚠️ No se encontraron commits")
            return {
                "status": "no_commits",
                "total_commits": 0,
                "date_range": None
            }

        self._print(f"\n📊 Procesando {len(commits)} commits...")

        # Fechas extremas
        first_date = commits[0]['date']
        last_date = commits[-1]['date']
        total_days = (last_date - first_date).days
        total_years = total_days / 365.25

        self._print(f"  ✓ Período: {first_date.date()} → {last_date.date()}")
        self._print(f"  ✓ Total días: {total_days}")

        # Frecuencia global
        commits_per_day = len(commits) / max(total_days, 1)
        commits_per_week = commits_per_day * 7
        commits_per_month = commits_per_day * 30
        commits_per_year = commits_per_day * 365

        # Commits por año
        self._print("\n📈 Calculando commits por período...")
        commits_by_year = defaultdict(int)
        commits_by_month = defaultdict(int)
        commits_by_week = defaultdict(int)
        commits_by_day_of_week = defaultdict(int)

        for commit in commits:
            dt = commit['date']
            year = dt.year
            month = f"{dt.year}-{dt.month:02d}"
            week = dt.isocalendar()[1]
            week_key = f"{dt.year}-W{week:02d}"
            day_of_week = dt.strftime('%A')

            commits_by_year[year] += 1
            commits_by_month[month] += 1
            commits_by_week[week_key] += 1
            commits_by_day_of_week[day_of_week] += 1

        # Últimos 12 meses
        last_12_months = defaultdict(int)
        cutoff_date = last_date - timedelta(days=365)

        for commit in commits:
            if commit['date'] >= cutoff_date:
                month = f"{commit['date'].year}-{commit['date'].month:02d}"
                last_12_months[month] += 1

        self._print("  ✓ Estadísticas calculadas")

        # Resultado
        resultado = {
            "status": "success",
            "total_commits": len(commits),
            "date_range": {
                "first_commit": first_date.isoformat(),
                "last_commit": last_date.isoformat(),
                "total_days": total_days,
                "total_years": round(total_years, 2)
            },
            "commit_frequency": {
                "commits_per_day": round(commits_per_day, 2),
                "commits_per_week": round(commits_per_week, 2),
                "commits_per_month": round(commits_per_month, 2),
                "commits_per_year": round(commits_per_year, 2)
            },
            "commits_by_year": dict(sorted(commits_by_year.items())),
            "commits_by_month": dict(sorted(commits_by_month.items())),
            "commits_by_week": dict(sorted(commits_by_week.items())),
            "commits_by_day_of_week": dict(commits_by_day_of_week),
            "last_12_months": dict(sorted(last_12_months.items())),
            "statistics": {
                "mean_commits_per_day": round(commits_per_day, 2),
                "median_commits_per_day": round(statistics.median(
                    [commits_by_day_of_week[day] for day in commits_by_day_of_week]
                ) if commits_by_day_of_week else 0, 2),
                "max_year": max(commits_by_year.items())[0] if commits_by_year else None,
                "max_commits_in_year": max(commits_by_year.values()) if commits_by_year else 0,
                "busiest_month": max(commits_by_month.items())[0] if commits_by_month else None,
                "busiest_day_of_week": max(commits_by_day_of_week.items())[0] if commits_by_day_of_week else None
            }
        }

        return resultado

    def calcular_y_exportar(self, output_file: str = None) -> Dict:
        """
        Calcula la métrica y exporta resultados a JSON.
        """
        print("\n" + "=" * 70)
        print("COMMIT FREQUENCY - Frecuencia de Entregas Exitosas")
        print("Métrica C29: Frecuencia con la que se incorporan cambios")
        print("=" * 70)

        resultado = self.calcular()

        if resultado['status'] == 'success':
            freq = resultado['commit_frequency']
            stats = resultado['statistics']
            date_range = resultado['date_range']

            print("\n" + "-" * 70)
            print("📊 INFORMACIÓN GENERAL")
            print("-" * 70)
            print(f"Total commits:              {resultado['total_commits']:,}")
            print(f"Período:                    {date_range['first_commit'][:10]} → {date_range['last_commit'][:10]}")
            print(f"Duración:                   {date_range['total_days']} días ({date_range['total_years']} años)")

            print("\n" + "-" * 70)
            print("📈 FRECUENCIA DE COMMITS")
            print("-" * 70)
            print(f"Promedio commits/día:       {freq['commits_per_day']:.2f}")
            print(f"Promedio commits/semana:    {freq['commits_per_week']:.2f}")
            print(f"Promedio commits/mes:       {freq['commits_per_month']:.2f}")
            print(f"Promedio commits/año:       {freq['commits_per_year']:.2f}")

            print("\n" + "-" * 70)
            print("🏆 ESTADÍSTICAS DESTACADAS")
            print("-" * 70)
            print(f"Año más activo:             {stats['max_year']} ({stats['max_commits_in_year']} commits)")
            print(f"Mes más activo:             {stats['busiest_month']}")
            print(f"Día de semana más activo:   {stats['busiest_day_of_week']}")

            print("\n" + "-" * 70)
            print("📅 TOP 5 AÑOS POR COMMITS")
            print("-" * 70)
            commits_by_year = sorted(
                resultado['commits_by_year'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            for year, count in commits_by_year:
                freq_year = count / 365
                print(f"  {year}: {count:5d} commits ({freq_year:.2f} commits/día)")

            print("\n" + "-" * 70)
            print("📅 ÚLTIMOS 12 MESES")
            print("-" * 70)
            last_12 = sorted(resultado['last_12_months'].items())
            for month, count in last_12:
                print(f"  {month}: {count:4d} commits")

            print("\n" + "-" * 70)
            print("📊 COMMITS POR DÍA DE LA SEMANA")
            print("-" * 70)
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                count = resultado['commits_by_day_of_week'].get(day, 0)
                percentage = (count / resultado['total_commits'] * 100) if resultado['total_commits'] > 0 else 0
                bar = '█' * int(percentage / 2)
                print(f"  {day:10s}: {count:5d} commits ({percentage:5.1f}%) {bar}")

        else:
            print("⚠️ No se encontraron commits en el repositorio")

        # Exportar a JSON
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)
            print(f"\n✓ Resultados exportados a: {output_path}")

        print("\n" + "=" * 70 + "\n")

        return resultado


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python commit_frequency.py <repo_path> [output_file]")
        print("\nEjemplos:")
        print("  python commit_frequency.py /Users/luzlaura/projects/tesis/tldr")
        print("  python commit_frequency.py /Users/luzlaura/projects/tesis/tldr resultados.json")
        sys.exit(1)

    repo_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        metric = CommitFrequency(repo_path, verbose=True)
        resultado = metric.calcular_y_exportar(output_file)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)