"""
Average Problem Resolution Time - SEARCH API (FUNCIONA CORRECTAMENTE)
Tiempo Promedio de Resolución de Problemas

SOLUCIÓN CORRECTA: Usar GitHub Search API que soporta filtros de fecha
El endpoint /repos/issues devuelve en orden de creación, no de cierre
Search API permite: is:issue is:closed closed:YYYY-MM-DD..YYYY-MM-DD
"""

from datetime import datetime, timedelta
from typing import Dict, List
import statistics
import json
from pathlib import Path
import sys
import os

try:
    import requests
except ImportError:
    print("❌ Error: requests no está instalado")
    print("Instala con: pip install requests")
    sys.exit(1)


class AverageProblemResolutionTimeSearchAPI:
    """
    Calcula el tiempo promedio de resolución de issues usando GitHub Search API.

    VENTAJAS:
    - Soporta filtros de fecha (closed_at)
    - Sin límite de paginación normal
    - Obtiene TODOS los issues correctamente
    """

    def __init__(self, repo_owner: str, repo_name: str, github_token: str = None, verbose=True):
        """
        Args:
            repo_owner: Propietario del repositorio
            repo_name: Nombre del repositorio
            github_token: Token de GitHub
            verbose: Mostrar información de debug
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.verbose = verbose
        self.base_url = "https://api.github.com"

        # Obtener token
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        if not self.github_token:
            raise ValueError(
                "❌ Token de GitHub no proporcionado.\n"
                "Proporciona con: GITHUB_TOKEN=tu_token python script.py"
            )

        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        self._print(f"✓ GitHub token configurado")
        self._print(f"✓ Repositorio: {repo_owner}/{repo_name}")

    def _print(self, msg):
        """Imprime si verbose está activo"""
        if self.verbose:
            print(msg)

    def _count_issues_in_range(self, fecha_inicio: str, fecha_fin: str) -> int:
        """
        Cuenta cuántos issues hay en un rango.
        """

        url = f"{self.base_url}/search/issues"

        query = (
            f"repo:{self.repo_owner}/{self.repo_name} "
            f"is:issue is:closed "
            f"closed:{fecha_inicio}..{fecha_fin}"
        )

        response = requests.get(
            url,
            headers=self.headers,
            params={
                "q": query,
                "per_page": 1
            },
            timeout=10
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Error contando issues: {response.status_code}"
            )

        return response.json().get("total_count", 0)

    def _split_date_range(self, fecha_inicio: str, fecha_fin: str):
        """
        Divide un rango de fechas en dos mitades.
        """

        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

        mitad = inicio + (fin - inicio) / 2
        mitad = mitad.date()

        return (
            fecha_inicio,
            mitad.strftime("%Y-%m-%d"),
            (mitad + timedelta(days=1)).strftime("%Y-%m-%d"),
            fecha_fin
        )

    def _get_issues_recursive(
            self,
            fecha_inicio: str,
            fecha_fin: str,
            nivel: int = 0
    ) -> List[Dict]:
        """
        Descarga TODOS los issues.
        Si un rango supera 1000 resultados,
        lo divide automáticamente.
        """

        total = self._count_issues_in_range(
            fecha_inicio,
            fecha_fin
        )

        indent = "  " * nivel

        self._print(
            f"{indent}📊 {fecha_inicio} → {fecha_fin}: {total} issues"
        )

        if total <= 1000:
            return self._search_issues_batch(
                fecha_inicio,
                fecha_fin,
                f"Batch {fecha_inicio} → {fecha_fin}"
            )

        self._print(
            f"{indent}⚠️ Más de 1000 resultados, dividiendo..."
        )

        (
            inicio1,
            fin1,
            inicio2,
            fin2
        ) = self._split_date_range(
            fecha_inicio,
            fecha_fin
        )

        issues1 = self._get_issues_recursive(
            inicio1,
            fin1,
            nivel + 1
        )

        issues2 = self._get_issues_recursive(
            inicio2,
            fin2,
            nivel + 1
        )

        return issues1 + issues2

    def _search_issues_batch(self, fecha_inicio: str, fecha_fin: str, batch_name: str) -> List[Dict]:
        """
        Busca issues cerrados en un rango de fechas usando Search API.

        Search API es correcta porque filtra por closed_at directamente

        Args:
            fecha_inicio: Formato "2020-01-01"
            fecha_fin: Formato "2020-12-31"
            batch_name: Nombre descriptivo del batch
        """
        self._print(f"\n📥 {batch_name}")
        self._print(f"   Período: {fecha_inicio} a {fecha_fin}")

        url = f"{self.base_url}/search/issues"

        # Query para Search API
        # is:issue = solo issues (no PRs)
        # is:closed = solo cerrados
        # closed:YYYY-MM-DD..YYYY-MM-DD = rango de fecha de cierre
        query = (
            f"repo:{self.repo_owner}/{self.repo_name} "
            f"is:issue is:closed "
            f"closed:{fecha_inicio}..{fecha_fin}"
        )

        params = {
            'q': query,
            'per_page': 100,
            'page': 1,
            'sort': 'updated',
            'order': 'desc'
        }

        all_issues = []
        page = 1

        try:
            while True:
                params['page'] = page

                self._print(f"   → Página {page}...")
                response = requests.get(url, headers=self.headers, params=params, timeout=10)

                # Información de rate limit
                remaining = response.headers.get('X-RateLimit-Remaining', 'unknown')
                self._print(f"     (Rate limit: {remaining} requests remaining)")

                if response.status_code == 401:
                    raise RuntimeError("❌ Token de GitHub inválido")
                elif response.status_code == 403:
                    raise RuntimeError("❌ Límite de rate limit alcanzado (espera 1 hora)")
                elif response.status_code == 422:
                    raise RuntimeError("❌ Query inválida a Search API")
                elif response.status_code != 200:
                    raise RuntimeError(f"❌ Error GitHub API: {response.status_code} - {response.text}")

                data = response.json()

                # Obtener total en primera página
                if page == 1:
                    total = data.get('total_count', 0)
                    self._print(f"     Total issues en este rango: {total}")

                issues = data.get('items', [])

                if not issues:
                    self._print(f"     ✓ Fin de resultados")
                    break

                # Procesar issues
                for issue in issues:
                    all_issues.append({
                        'id': issue['id'],
                        'number': issue['number'],
                        'title': issue['title'],
                        'created_at': issue['created_at'],
                        'closed_at': issue['closed_at'],
                        'labels': [label['name'] for label in issue.get('labels', [])]
                    })

                self._print(f"     Recibidos: {len(issues)} issues")

                page += 1

                if page > 10:
                    break

        except requests.exceptions.RequestException as e:
            self._print(f"❌ Error de conexión: {e}")
            raise

        self._print(f"   ✓ Total en este batch: {len(all_issues)}")
        return all_issues

    def _get_all_closed_issues(self) -> List[Dict]:
        """
        Obtiene TODOS los issues cerrados.

        Evita automáticamente el límite
        de 1000 resultados de Search API.
        """

        self._print("\n" + "=" * 70)
        self._print("EXTRAYENDO ISSUES USANDO SEARCH API")
        self._print("DIVISIÓN AUTOMÁTICA DE FECHAS")
        self._print("=" * 70)

        all_issues = self._get_issues_recursive(
            "2010-01-01",
            "2099-12-31"
        )

        seen = set()
        unique_issues = []

        for issue in all_issues:
            if issue["number"] not in seen:
                seen.add(issue["number"])
                unique_issues.append(issue)

        self._print("\n" + "=" * 70)
        self._print(
            f"TOTAL ISSUES ÚNICOS: {len(unique_issues)}"
        )
        self._print("=" * 70)

        return unique_issues

    def calcular(self) -> Dict:
        """
        Calcula estadísticas de tiempo de resolución de issues.
        """
        issues = self._get_all_closed_issues()

        if not issues:
            self._print("⚠️ No se encontraron issues cerrados")
            return {
                "status": "no_issues",
                "total_issues": 0
            }

        self._print(f"\n📊 Procesando {len(issues)} issues...")

        # Calcular tiempos de resolución
        resolution_times = []

        for issue in issues:
            try:
                created = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
                closed = datetime.fromisoformat(issue['closed_at'].replace('Z', '+00:00'))

                # Tiempo en días
                days = (closed - created).total_seconds() / 86400
                resolution_times.append({
                    'issue_number': issue['number'],
                    'title': issue['title'],
                    'days': days,
                    'labels': issue['labels']
                })
            except Exception as e:
                self._print(f"⚠️ Error procesando issue #{issue['number']}: {e}")
                continue

        if not resolution_times:
            return {
                "status": "no_data",
                "total_issues": 0
            }

        self._print(f"  ✓ Issues procesados: {len(resolution_times)}")

        # Estadísticas básicas
        days_list = [rt['days'] for rt in resolution_times]
        media = statistics.mean(days_list)
        mediana = statistics.median(days_list)
        min_days = min(days_list)
        max_days = max(days_list)
        std_dev = statistics.stdev(days_list) if len(days_list) > 1 else 0

        # Contar issues en intervalos
        self._print("\n📈 Calculando intervalos...")

        intervals = {
            "1_dia": sum(1 for rt in resolution_times if rt['days'] <= 1),
            "3_dias": sum(1 for rt in resolution_times if rt['days'] <= 3),
            "7_dias": sum(1 for rt in resolution_times if rt['days'] <= 7),
            "30_dias": sum(1 for rt in resolution_times if rt['days'] <= 30),
            "100_dias": sum(1 for rt in resolution_times if rt['days'] <= 100),
            "365_dias": sum(1 for rt in resolution_times if rt['days'] <= 365),
        }

        # Top issues
        slowest = sorted(resolution_times, key=lambda x: x['days'], reverse=True)[:10]
        fastest = sorted(resolution_times, key=lambda x: x['days'])[:10]

        self._print("  ✓ Estadísticas calculadas")

        resultado = {
            "status": "success",
            "total_issues_cerrados": len(resolution_times),
            "extraction_method": "Search API con 2 batches por fecha (correcto)",
            "average_resolution_time": {
                "media_dias": round(media, 2),
                "mediana_dias": round(mediana, 2),
                "min_dias": round(min_days, 2),
                "max_dias": round(max_days, 2),
                "desv_estandar_dias": round(std_dev, 2)
            },
            "intervals": {
                key: {
                    "count": count,
                    "percentage": round(count / len(resolution_times) * 100, 1)
                }
                for key, count in intervals.items()
            },
            "cumulative_percentage": {
                "1_dia": round(intervals["1_dia"] / len(resolution_times) * 100, 1),
                "3_dias": round(intervals["3_dias"] / len(resolution_times) * 100, 1),
                "7_dias": round(intervals["7_dias"] / len(resolution_times) * 100, 1),
                "30_dias": round(intervals["30_dias"] / len(resolution_times) * 100, 1),
                "100_dias": round(intervals["100_dias"] / len(resolution_times) * 100, 1),
                "365_dias": round(intervals["365_dias"] / len(resolution_times) * 100, 1),
            },
            "slowest_issues": [
                {
                    "number": rt['issue_number'],
                    "title": rt['title'][:60],
                    "days": round(rt['days'], 1)
                }
                for rt in slowest
            ],
            "fastest_issues": [
                {
                    "number": rt['issue_number'],
                    "title": rt['title'][:60],
                    "days": round(rt['days'], 2)
                }
                for rt in fastest
            ]
        }

        return resultado

    def calcular_y_exportar(self, output_file: str = None) -> Dict:
        """
        Calcula la métrica y exporta resultados a JSON.
        """
        print("\n" + "="*70)
        print("AVERAGE PROBLEM RESOLUTION TIME - TODOS LOS ISSUES")
        print("Métrica C43: Tiempo Promedio de Resolución de Problemas")
        print("Método: Search API con 2 batches por fecha (CORRECTO)")
        print("="*70)

        resultado = self.calcular()

        if resultado['status'] == 'success':
            avg = resultado['average_resolution_time']
            intervals = resultado['intervals']
            cum_pct = resultado['cumulative_percentage']

            print("\n" + "-"*70)
            print("📊 ESTADÍSTICAS GENERALES")
            print("-"*70)
            print(f"Total issues cerrados:      {resultado['total_issues_cerrados']:,}")
            print(f"Método de extracción:       {resultado['extraction_method']}")
            print(f"Tiempo promedio (media):    {avg['media_dias']:>8.2f} días")
            print(f"Tiempo promedio (mediana):  {avg['mediana_dias']:>8.2f} días  ← MEJOR MÉTRICA")
            print(f"Mínimo:                     {avg['min_dias']:>8.2f} días")
            print(f"Máximo:                     {avg['max_dias']:>8.2f} días ({avg['max_dias']/365:.1f} años)")
            print(f"Desv. estándar:             {avg['desv_estandar_dias']:>8.2f} días")

            print("\n" + "-"*70)
            print("⏱️  DISTRIBUCIÓN POR INTERVALOS")
            print("-"*70)

            intervals_labels = {
                "1_dia": "≤ 1 día",
                "3_dias": "≤ 3 días",
                "7_dias": "≤ 7 días",
                "30_dias": "≤ 30 días",
                "100_dias": "≤ 100 días",
                "365_dias": "≤ 365 días"
            }

            for key, label in intervals_labels.items():
                count = intervals[key]['count']
                pct = cum_pct[key]
                bar = '█' * int(pct / 5)
                print(f"  {label:15s}: {count:5d} issues ({pct:5.1f}%) {bar}")

            print("\n" + "-"*70)
            print("🐢 TOP 10 ISSUES MÁS LENTOS")
            print("-"*70)
            for i, issue in enumerate(resultado['slowest_issues'][:10], 1):
                print(f"  {i:2d}. #{issue['number']:6d} - {issue['days']:8.1f} días - {issue['title']}")

            print("\n" + "-"*70)
            print("⚡ TOP 10 ISSUES MÁS RÁPIDOS")
            print("-"*70)
            for i, issue in enumerate(resultado['fastest_issues'][:10], 1):
                print(f"  {i:2d}. #{issue['number']:6d} - {issue['days']:8.2f} días - {issue['title']}")

            # Interpretación
            mediana = avg['mediana_dias']
            if mediana < 1:
                interpretation = "Excelente (muy rápido)"
            elif mediana < 3:
                interpretation = "Muy Bueno (respuesta ágil)"
            elif mediana < 7:
                interpretation = "Bueno (moderado)"
            elif mediana < 30:
                interpretation = "Aceptable"
            elif mediana < 90:
                interpretation = "Pobre"
            else:
                interpretation = "Muy Pobre"

            print("\n" + "-"*70)
            print("📈 INTERPRETACIÓN")
            print("-"*70)
            print(f"Mediana de {mediana:.2f} días = {interpretation}")
            if mediana <= 7:
                print("✅ El equipo resuelve issues rápidamente")
            elif mediana <= 30:
                print("ℹ️  Resolución moderada, típica de proyectos OSS")
            else:
                print("⚠️  Resolución lenta, revisar backlog")

        else:
            print("⚠️ No se encontraron issues cerrados")

        # Exportar a JSON
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)
            print(f"\n✓ Resultados exportados a: {output_path}")

        print("\n" + "="*70 + "\n")

        return resultado


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python average_problem_resolution_time_searchapi.py <owner> <repo> [output_file]")
        print("\nEjemplos:")
        print("  GITHUB_TOKEN=tu_token python average_problem_resolution_time_searchapi.py tldr-pages tldr")
        print("  GITHUB_TOKEN=tu_token python average_problem_resolution_time_searchapi.py tldr-pages tldr resultados.json")
        sys.exit(1)

    owner = sys.argv[1]
    repo = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else None

    try:
        metric = AverageProblemResolutionTimeSearchAPI(owner, repo, verbose=True)
        resultado = metric.calcular_y_exportar(output_file)
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)