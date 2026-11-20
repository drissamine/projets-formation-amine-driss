#!/usr/bin/env python3
"""
Script pour générer un rapport visuel des tests du projet Kafka-Spark
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_tests_and_collect_results():
    """Exécute les tests et collecte les résultats"""
    print("🧪 Exécution des tests...")
    
    # Exécuter pytest avec sortie JSON
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", 
        "--tb=short",
        "--json-report",
        "--json-report-file=test_results.json"
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print("⚠️ Timeout lors de l'exécution des tests")
        return -1, "", "Timeout"
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution des tests: {e}")
        return -1, "", str(e)


def parse_test_output(stdout):
    """Parse la sortie des tests pour extraire les informations"""
    lines = stdout.split('\n')
    
    results = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'warnings': 0,
        'duration': 0,
        'tests': []
    }
    
    for line in lines:
        # Extraire le résumé final
        if 'passed' in line and 'failed' in line:
            parts = line.split()
            for i, part in enumerate(parts):
                if part == 'failed,':
                    results['failed'] = int(parts[i-1])
                elif part == 'passed,':
                    results['passed'] = int(parts[i-1])
                elif part == 'warnings':
                    results['warnings'] = int(parts[i-1])
        
        # Extraire la durée
        if 'in' in line and 's' in line:
            try:
                duration_str = line.split('in')[1].strip().split()[0]
                results['duration'] = float(duration_str.replace('s', ''))
            except:
                pass
        
        # Extraire les tests individuels
        if 'PASSED' in line or 'FAILED' in line:
            test_name = line.split('::')[-1].split()[0] if '::' in line else ''
            status = 'PASSED' if 'PASSED' in line else 'FAILED'
            if test_name:
                results['tests'].append({
                    'name': test_name,
                    'status': status
                })
    
    results['total'] = results['passed'] + results['failed']
    return results


def generate_html_report(results):
    """Génère un rapport HTML visuel"""
    
    success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de Tests - Kafka-Spark Pipeline</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-card .number {{
            font-size: 3em;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .stat-card .label {{
            font-size: 1.1em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-card.success .number {{
            color: #28a745;
        }}
        
        .stat-card.danger .number {{
            color: #dc3545;
        }}
        
        .stat-card.warning .number {{
            color: #ffc107;
        }}
        
        .stat-card.info .number {{
            color: #17a2b8;
        }}
        
        .progress-section {{
            padding: 40px;
        }}
        
        .progress-bar-container {{
            background: #e9ecef;
            border-radius: 50px;
            height: 50px;
            overflow: hidden;
            position: relative;
            margin: 20px 0;
        }}
        
        .progress-bar {{
            height: 100%;
            background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 1.2em;
            transition: width 1s ease;
        }}
        
        .details {{
            padding: 40px;
        }}
        
        .test-list {{
            display: grid;
            gap: 10px;
        }}
        
        .test-item {{
            display: flex;
            align-items: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #28a745;
        }}
        
        .test-item.failed {{
            border-left-color: #dc3545;
            background: #fff5f5;
        }}
        
        .test-item .icon {{
            font-size: 1.5em;
            margin-right: 15px;
        }}
        
        .test-item .name {{
            flex: 1;
            font-family: 'Courier New', monospace;
        }}
        
        .footer {{
            background: #343a40;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            margin: 5px;
        }}
        
        .badge.success {{
            background: #28a745;
            color: white;
        }}
        
        .badge.danger {{
            background: #dc3545;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Rapport de Tests</h1>
            <p>Kafka-Spark Streaming Pipeline</p>
            <p style="font-size: 0.9em; margin-top: 10px;">
                Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
            </p>
        </div>
        
        <div class="stats">
            <div class="stat-card info">
                <div class="label">Total Tests</div>
                <div class="number">{results['total']}</div>
            </div>
            
            <div class="stat-card success">
                <div class="label">✅ Réussis</div>
                <div class="number">{results['passed']}</div>
            </div>
            
            <div class="stat-card danger">
                <div class="label">❌ Échoués</div>
                <div class="number">{results['failed']}</div>
            </div>
            
            <div class="stat-card warning">
                <div class="label">⚠️ Warnings</div>
                <div class="number">{results['warnings']}</div>
            </div>
        </div>
        
        <div class="progress-section">
            <h2 style="margin-bottom: 20px;">Taux de Réussite</h2>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: {success_rate}%;">
                    {success_rate:.1f}%
                </div>
            </div>
            <p style="text-align: center; color: #666; margin-top: 10px;">
                Durée totale: {results['duration']:.2f} secondes
            </p>
        </div>
        
        <div class="details">
            <h2 style="margin-bottom: 20px;">Détails des Tests</h2>
            <div class="test-list">
"""
    
    # Ajouter les tests individuels
    for test in results['tests']:
        icon = '✅' if test['status'] == 'PASSED' else '❌'
        css_class = '' if test['status'] == 'PASSED' else 'failed'
        html += f"""
                <div class="test-item {css_class}">
                    <span class="icon">{icon}</span>
                    <span class="name">{test['name']}</span>
                    <span class="badge {'success' if test['status'] == 'PASSED' else 'danger'}">{test['status']}</span>
                </div>
"""
    
    html += """
            </div>
        </div>
        
        <div class="footer">
            <p>🚀 Projet réalisé dans le cadre du cours de Big Data et Streaming Analytics</p>
            <p style="margin-top: 10px; font-size: 0.9em;">
                Technologies: Apache Kafka 3.5+ | Apache Spark 3.4+ | Python 3.14
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


def main():
    """Fonction principale"""
    print("=" * 60)
    print("📊 Générateur de Rapport de Tests")
    print("   Kafka-Spark Streaming Pipeline")
    print("=" * 60)
    print()
    
    # Exécuter les tests
    returncode, stdout, stderr = run_tests_and_collect_results()
    
    if returncode == -1:
        print("❌ Impossible d'exécuter les tests")
        return
    
    # Parser les résultats
    print("📝 Analyse des résultats...")
    results = parse_test_output(stdout)
    
    # Afficher un résumé dans la console
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"Total:     {results['total']} tests")
    print(f"✅ Réussis: {results['passed']} tests")
    print(f"❌ Échoués: {results['failed']} tests")
    print(f"⚠️ Warnings: {results['warnings']}")
    print(f"⏱️ Durée:   {results['duration']:.2f}s")
    
    if results['total'] > 0:
        success_rate = results['passed'] / results['total'] * 100
        print(f"📈 Taux de réussite: {success_rate:.1f}%")
    
    print("=" * 60)
    
    # Générer le rapport HTML
    print("\n📄 Génération du rapport HTML...")
    html_content = generate_html_report(results)
    
    # Sauvegarder le rapport
    report_path = Path("test_report.html")
    report_path.write_text(html_content, encoding='utf-8')
    
    print(f"✅ Rapport généré: {report_path.absolute()}")
    print("\n💡 Ouvrez 'test_report.html' dans votre navigateur pour voir le rapport visuel")
    
    # Retourner le code de sortie approprié
    return 0 if results['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
