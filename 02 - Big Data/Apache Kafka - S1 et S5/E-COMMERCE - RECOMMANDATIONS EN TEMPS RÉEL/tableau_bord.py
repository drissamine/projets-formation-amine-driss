from flask import Flask, render_template_string, jsonify
import threading
import time
from collections import defaultdict
from kafka import KafkaConsumer
import json

import moteur_recommandations
import test_ab
import config

app = Flask(__name__)

# Instance globale du moteur (partagée)
moteur_global = None
test_ab_global = None

# Données du dashboard
dashboard_data = {
    'total_users': 0,
    'total_events': 0,
    'recommendations_generated': 0,
    'recommendations_clicked': 0,
    'recommendations_converted': 0,
    'revenue_from_recommendations': 0.0,
    'efficiency_metrics': {
        'overall_ctr': 0.0,  # Click-through rate
        'overall_conversion_rate': 0.0,
        'average_order_value': 0.0,
        'recommendation_revenue_per_user': 0.0
    },
    'ab_metrics': {'categorie': {'total': 0, 'clics': 0, 'conversions': 0, 'revenue': 0.0, 'taux_clic': 0, 'taux_conversion': 0},
                  'recommandation': {'total': 0, 'clics': 0, 'conversions': 0, 'revenue': 0.0, 'taux_clic': 0, 'taux_conversion': 0}},
    'last_update': None
}

# Consumer pour les recommandations
recommendations_consumer = None

def collecter_recommandations():
    """Thread en arrière-plan pour collecter les recommandations depuis Kafka"""
    global dashboard_data

    try:
        consumer = KafkaConsumer(
            config.TOPIC_RECOMMANDATIONS,
            bootstrap_servers=config.KAFKA_SERVERS,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='earliest',
            group_id='dashboard-consumer',
            consumer_timeout_ms=1000
        )

        print("Consumer de recommandations démarré")

        while True:
            try:
                # Consommer les messages disponibles
                messages = consumer.poll(timeout_ms=1000)

                for topic_partition, records in messages.items():
                    for record in records:
                        rec = record.value
                        algo = rec.get('algorithm', 'categorie')

                        # Mettre à jour les compteurs
                        dashboard_data['recommendations_generated'] += 1
                        dashboard_data['ab_metrics'][algo]['total'] += 1

                        # Simuler des clics et conversions (pour la démo)
                        if dashboard_data['recommendations_generated'] % 3 == 0:
                            dashboard_data['ab_metrics'][algo]['clics'] += 1
                            dashboard_data['recommendations_clicked'] += 1

                            # Simuler des conversions (1 clic sur 4 devient achat)
                            if dashboard_data['recommendations_clicked'] % 4 == 0:
                                dashboard_data['ab_metrics'][algo]['conversions'] += 1
                                dashboard_data['recommendations_converted'] += 1
                                # Simuler un revenu moyen de 150€
                                revenue = 150.0
                                dashboard_data['ab_metrics'][algo]['revenue'] += revenue
                                dashboard_data['revenue_from_recommendations'] += revenue

                        dashboard_data['last_update'] = time.time()

            except Exception as e:
                print(f"Erreur consumer recommandations: {e}")
                time.sleep(1)

    except Exception as e:
        print(f"Erreur démarrage consumer recommandations: {e}")

def collecter_evenements():
    """Thread en arrière-plan pour compter les événements utilisateur"""
    global dashboard_data

    try:
        consumer = KafkaConsumer(
            config.TOPIC_EVENEMENTS,
            bootstrap_servers=config.KAFKA_SERVERS,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='earliest',
            group_id='dashboard-events-consumer',
            consumer_timeout_ms=1000
        )

        utilisateurs_uniques = set()

        print("Consumer d'événements démarré")

        while True:
            try:
                messages = consumer.poll(timeout_ms=1000)

                for topic_partition, records in messages.items():
                    for record in records:
                        event = record.value
                        user_id = event.get('user_id')

                        if user_id:
                            utilisateurs_uniques.add(user_id)

                        dashboard_data['total_events'] += 1
                        dashboard_data['total_users'] = len(utilisateurs_uniques)
                        dashboard_data['last_update'] = time.time()

            except Exception as e:
                print(f"Erreur consumer événements: {e}")
                time.sleep(1)

    except Exception as e:
        print(f"Erreur démarrage consumer événements: {e}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Tableau de Bord - Recommandations E-commerce</title>
    <meta charset="utf-8">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric { background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .metric h3 { margin: 0 0 10px 0; }
        .metric-value { font-size: 24px; font-weight: bold; color: #007bff; }
        .chart-container { width: 100%; height: 400px; margin: 20px 0; background: white; border-radius: 5px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .charts-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin: 20px 0; }
        .chart-full { grid-column: 1 / -1; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .status { color: green; }
        .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin: 20px 0; }
    </style>
    <script>
        let recommendationsChart, abComparisonChart, algorithmPieChart, efficiencyChart;
        let chartData = { timestamps: [], recommendations: [], users: [], events: [] };

        function initCharts() {
            // Graphique évolution recommandations
            const recCtx = document.getElementById('recommendationsChart').getContext('2d');
            recommendationsChart = new Chart(recCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Recommandations Générées',
                        data: [],
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        tension: 0.4,
                        fill: true
                    }, {
                        label: 'Utilisateurs Actifs',
                        data: [],
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Évolution des Recommandations et Utilisateurs'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

            // Graphique comparaison A/B
            const abCtx = document.getElementById('abComparisonChart').getContext('2d');
            abComparisonChart = new Chart(abCtx, {
                type: 'bar',
                data: {
                    labels: ['Catégorie', 'Recommandation'],
                    datasets: [{
                        label: 'Taux de Clic (%)',
                        data: [],
                        backgroundColor: 'rgba(0, 123, 255, 0.6)',
                        borderColor: 'rgba(0, 123, 255, 1)',
                        borderWidth: 1
                    }, {
                        label: 'Taux de Conversion (%)',
                        data: [],
                        backgroundColor: 'rgba(40, 167, 69, 0.6)',
                        borderColor: 'rgba(40, 167, 69, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Performance des Algorithmes A/B'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });

            // Graphique circulaire algorithmes
            const pieCtx = document.getElementById('algorithmPieChart').getContext('2d');
            algorithmPieChart = new Chart(pieCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Catégorie', 'Recommandation'],
                    datasets: [{
                        data: [],
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.6)',
                            'rgba(54, 162, 235, 0.6)'
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Répartition des Algorithmes'
                        },
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });

            // Graphique efficacité
            const effCtx = document.getElementById('efficiencyChart').getContext('2d');
            efficiencyChart = new Chart(effCtx, {
                type: 'radar',
                data: {
                    labels: ['CTR Global', 'Taux Conversion', 'Recommandations', 'Utilisations'],
                    datasets: [{
                        label: 'Performance',
                        data: [],
                        backgroundColor: 'rgba(153, 102, 255, 0.2)',
                        borderColor: 'rgba(153, 102, 255, 1)',
                        borderWidth: 2,
                        pointBackgroundColor: 'rgba(153, 102, 255, 1)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Efficacité Globale du Système'
                        }
                    },
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }

        function updateCharts(data) {
            const now = new Date().toLocaleTimeString();

            // Mise à jour graphique évolution
            chartData.timestamps.push(now);
            chartData.recommendations.push(data.recommendations_generated);
            chartData.users.push(data.total_users);

            // Garder seulement les 20 dernières valeurs
            if (chartData.timestamps.length > 20) {
                chartData.timestamps.shift();
                chartData.recommendations.shift();
                chartData.users.shift();
            }

            recommendationsChart.data.labels = chartData.timestamps;
            recommendationsChart.data.datasets[0].data = chartData.recommendations;
            recommendationsChart.data.datasets[1].data = chartData.users;
            recommendationsChart.update();

            // Mise à jour graphique A/B
            const clicRates = [];
            const conversionRates = [];

            for (const [algo, metrics] of Object.entries(data.ab_metrics)) {
                clicRates.push(metrics.taux_clic);
                conversionRates.push(metrics.taux_conversion);
            }

            abComparisonChart.data.datasets[0].data = clicRates;
            abComparisonChart.data.datasets[1].data = conversionRates;
            abComparisonChart.update();

            // Mise à jour graphique circulaire
            const totals = [];
            for (const [algo, metrics] of Object.entries(data.ab_metrics)) {
                totals.push(metrics.total);
            }
            algorithmPieChart.data.datasets[0].data = totals;
            algorithmPieChart.update();

            // Mise à jour graphique efficacité
            efficiencyChart.data.datasets[0].data = [
                data.efficiency_metrics.overall_ctr,
                data.efficiency_metrics.overall_conversion_rate,
                data.recommendations_generated > 0 ? 100 : 0,
                data.total_users > 0 ? 100 : 0
            ];
            efficiencyChart.update();
        }

        function refreshData() {
            fetch('/api/metrics')
                .then(response => response.json())
                .then(data => {
                    // Mise à jour métriques texte
                    document.getElementById('total-users').textContent = data.total_users;
                    document.getElementById('total-events').textContent = data.total_events;
                    document.getElementById('recommendations-generated').textContent = data.recommendations_generated;
                    document.getElementById('recommendations-clicked').textContent = data.recommendations_clicked;
                    document.getElementById('recommendations-converted').textContent = data.recommendations_converted;
                    document.getElementById('revenue-from-recommendations').textContent = data.revenue_from_recommendations.toFixed(2) + '€';
                    document.getElementById('overall-ctr').textContent = data.efficiency_metrics.overall_ctr.toFixed(2) + '%';
                    document.getElementById('overall-conversion-rate').textContent = data.efficiency_metrics.overall_conversion_rate.toFixed(2) + '%';

                    // Mise à jour table A/B
                    const tbody = document.getElementById('ab-results');
                    tbody.innerHTML = '';
                    for (const [algo, metrics] of Object.entries(data.ab_metrics)) {
                        tbody.innerHTML += `
                            <tr>
                                <td>${algo}</td>
                                <td>${metrics.total}</td>
                                <td>${metrics.taux_clic}%</td>
                                <td>${metrics.taux_conversion}%</td>
                            </tr>
                        `;
                    }

                    // Mise à jour graphiques
                    updateCharts(data);
                })
                .catch(error => console.error('Erreur mise à jour données:', error));
        }

        // Initialisation
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
            refreshData();
        });

        setInterval(refreshData, 2000); // Actualisation toutes les 2 secondes
    </script>
</head>
<body>
    <h1>🛍️ Tableau de Bord - Système de Recommandations E-commerce</h1>

    <div class="metric">
        <h3>📊 Métriques Globales</h3>
        <p>Utilisateurs actifs: <span class="metric-value" id="total-users">0</span></p>
        <p>Événements traités: <span class="metric-value" id="total-events">0</span></p>
        <p>Recommandations générées: <span class="metric-value" id="recommendations-generated">0</span></p>
    </div>

    <div class="metric">
        <h3>🎯 Efficacité des Recommandations</h3>
        <p>Recommandations cliquées: <span class="metric-value" id="recommendations-clicked">0</span></p>
        <p>Conversions depuis recommandations: <span class="metric-value" id="recommendations-converted">0</span></p>
        <p>Revenus générés: <span class="metric-value" id="revenue-from-recommendations">0.00€</span></p>
        <p>Taux de clic global: <span class="metric-value" id="overall-ctr">0.00%</span></p>
        <p>Taux de conversion: <span class="metric-value" id="overall-conversion-rate">0.00%</span></p>
    </div>

    <div class="metric">
        <h3>🧪 Test A/B - Performance des Algorithmes</h3>
        <table>
            <thead>
                <tr>
                    <th>Algorithme</th>
                    <th>Total Recommandations</th>
                    <th>Taux de Clic</th>
                    <th>Taux de Conversion</th>
                </tr>
            </thead>
            <tbody id="ab-results">
                <!-- Données chargées dynamiquement -->
            </tbody>
        </table>
    </div>

    <div class="metric">
        <h3>🔄 État du Système</h3>
        <p class="status">✅ Service de suivi: Actif</p>
        <p class="status">✅ Moteur de recommandations: Actif</p>
        <p class="status">✅ Kafka: Connecté</p>
    </div>

    <div class="metric">
        <h3>📈 Graphiques Temps réel</h3>
        <div class="charts-grid">
            <div class="chart-container">
                <canvas id="recommendationsChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="abComparisonChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="algorithmPieChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="efficiencyChart"></canvas>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/metrics')
def get_metrics():
    # Calculer les taux pour les métriques A/B
    ab_metrics = dashboard_data['ab_metrics'].copy()
    for algo in ab_metrics:
        total = ab_metrics[algo]['total']
        if total > 0:
            ab_metrics[algo]['taux_clic'] = round(ab_metrics[algo]['clics'] / total * 100, 2)
            ab_metrics[algo]['taux_conversion'] = round(ab_metrics[algo]['conversions'] / total * 100, 2)
        else:
            ab_metrics[algo]['taux_clic'] = 0
            ab_metrics[algo]['taux_conversion'] = 0

    # Calculer les métriques d'efficacité globale
    efficiency_metrics = dashboard_data['efficiency_metrics'].copy()
    if dashboard_data['recommendations_generated'] > 0:
        efficiency_metrics['overall_ctr'] = round(
            dashboard_data['recommendations_clicked'] / dashboard_data['recommendations_generated'] * 100, 2
        )
        efficiency_metrics['overall_conversion_rate'] = round(
            dashboard_data['recommendations_converted'] / dashboard_data['recommendations_generated'] * 100, 2
        )
        if dashboard_data['recommendations_converted'] > 0:
            efficiency_metrics['average_order_value'] = round(
                dashboard_data['revenue_from_recommendations'] / dashboard_data['recommendations_converted'], 2
            )
        efficiency_metrics['recommendation_revenue_per_user'] = round(
            dashboard_data['revenue_from_recommendations'] / max(dashboard_data['total_users'], 1), 2
        )

    return jsonify({
        'total_users': dashboard_data['total_users'],
        'total_events': dashboard_data['total_events'],
        'recommendations_generated': dashboard_data['recommendations_generated'],
        'recommendations_clicked': dashboard_data['recommendations_clicked'],
        'recommendations_converted': dashboard_data['recommendations_converted'],
        'revenue_from_recommendations': dashboard_data['revenue_from_recommendations'],
        'efficiency_metrics': efficiency_metrics,
        'ab_metrics': ab_metrics
    })

def demarrer_dashboard(moteur_instance=None, test_ab_instance=None):
    """Démarre le dashboard avec les instances partagées"""
    global moteur_global, test_ab_global
    moteur_global = moteur_instance
    test_ab_global = test_ab_instance

    print(f"Dashboard démarré sur http://localhost:{config.PORT_DASHBOARD}")
    app.run(host='0.0.0.0', port=config.PORT_DASHBOARD, debug=False)

if __name__ == "__main__":
    # Démarrer les threads de collecte de données
    thread_recommandations = threading.Thread(target=collecter_recommandations, daemon=True)
    thread_evenements = threading.Thread(target=collecter_evenements, daemon=True)

    thread_recommandations.start()
    thread_evenements.start()

    # Attendre un peu que les consumers se connectent
    time.sleep(2)

    # Démarrer le dashboard
    demarrer_dashboard()
