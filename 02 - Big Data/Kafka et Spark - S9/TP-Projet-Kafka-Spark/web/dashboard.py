#!/usr/bin/env python3
"""
Web Dashboard for Kafka-Spark Streaming Pipeline

Real-time web dashboard for monitoring and visualizing streaming analytics results.
Built with Flask, Plotly, and SQLite for data persistence.
"""

import json
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import plotly.graph_objs as go
import plotly.utils
from pathlib import Path
import sys
import os

# Add parent directory to path to allow imports from project root
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

# Import our monitoring and output handlers
from monitoring.metrics import PipelineMetrics
from spark.output.sqlite_output import SQLiteOutputHandler

# Configure Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for API endpoints

# Configuration
DATABASE_PATH = "./results/streaming_results.db"
REFRESH_INTERVAL = 30  # seconds
MAX_DATA_POINTS = 100

class DashboardDataCollector:
    """Collects data for the dashboard from various sources"""
    
    def __init__(self):
        self.metrics = PipelineMetrics()
        self.sqlite_handler = SQLiteOutputHandler()
        self.data_cache = {
            'video_popularity': [],
            'user_engagement': [],
            'genre_analysis': [],
            'anomalies': [],
            'system_metrics': {},
            'pipeline_stats': {}
        }
        self.running = False
        self.thread = None
    
    def start(self):
        """Start background data collection"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._collection_loop, daemon=True)
            self.thread.start()
            print("Dashboard data collector started")
    
    def stop(self):
        """Stop background data collection"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("Dashboard data collector stopped")
    
    def _collection_loop(self):
        """Background loop for collecting data"""
        while self.running:
            try:
                # Collect pipeline metrics
                self._collect_pipeline_metrics()
                
                # Collect database data
                self._collect_database_data()
                
                # Sleep for refresh interval
                time.sleep(REFRESH_INTERVAL)
                
            except Exception as e:
                print(f"Error in data collection: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _collect_pipeline_metrics(self):
        """Collect pipeline performance metrics"""
        try:
            # Get throughput and latency
            throughput = self.metrics.get_throughput()
            latency = self.metrics.get_latency_stats()
            system_stats = self.metrics.get_system_stats()
            
            self.data_cache['pipeline_stats'] = {
                'throughput': throughput,
                'latency': latency,
                'system': system_stats,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error collecting pipeline metrics: {e}")
    
    def _collect_database_data(self):
        """Collect data from SQLite database"""
        try:
            # Get latest video popularity
            video_popularity = self.sqlite_handler.get_latest_video_popularity(limit=10)
            self.data_cache['video_popularity'] = video_popularity
            
            # Get latest user engagement
            user_engagement = self.sqlite_handler.get_latest_user_engagement(limit=10)
            self.data_cache['user_engagement'] = user_engagement
            
            # Get latest genre analysis
            genre_analysis = self.sqlite_handler.get_latest_genre_analysis(limit=10)
            self.data_cache['genre_analysis'] = genre_analysis
            
            # Get latest anomalies
            anomalies = self.sqlite_handler.get_latest_anomalies(limit=20)
            self.data_cache['anomalies'] = anomalies
            
        except Exception as e:
            print(f"Error collecting database data: {e}")
    
    def get_data(self) -> Dict[str, Any]:
        """Get current cached data"""
        return self.data_cache.copy()

# Initialize dashboard components
data_collector = DashboardDataCollector()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def api_stats():
    """API endpoint for pipeline statistics"""
    data = data_collector.get_data()
    return jsonify(data.get('pipeline_stats', {}))

@app.route('/api/video-popularity')
def api_video_popularity():
    """API endpoint for video popularity data"""
    data = data_collector.get_data()
    return jsonify(data.get('video_popularity', []))

@app.route('/api/user-engagement')
def api_user_engagement():
    """API endpoint for user engagement data"""
    data = data_collector.get_data()
    return jsonify(data.get('user_engagement', []))

@app.route('/api/genre-analysis')
def api_genre_analysis():
    """API endpoint for genre analysis data"""
    data = data_collector.get_data()
    return jsonify(data.get('genre_analysis', []))

@app.route('/api/anomalies')
def api_anomalies():
    """API endpoint for anomaly data"""
    data = data_collector.get_data()
    return jsonify(data.get('anomalies', []))

@app.route('/api/charts/video-popularity')
def api_chart_video_popularity():
    """API endpoint for video popularity chart data"""
    try:
        # Get data from database
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get video popularity over time
        cursor.execute("""
            SELECT window_start, video_id, play_count, unique_users
            FROM video_popularity 
            ORDER BY window_start DESC 
            LIMIT 50
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        # Process data for chart
        videos = {}
        for row in rows:
            window_start, video_id, play_count, unique_users = row
            if video_id not in videos:
                videos[video_id] = {
                    'timestamps': [],
                    'play_counts': [],
                    'unique_users': []
                }
            
            videos[video_id]['timestamps'].append(window_start)
            videos[video_id]['play_counts'].append(play_count)
            videos[video_id]['unique_users'].append(unique_users)
        
        # Create plotly traces
        traces = []
        for video_id, data in videos.items():
            traces.append(go.Scatter(
                x=data['timestamps'],
                y=data['play_counts'],
                mode='lines+markers',
                name=f'{video_id} (plays)',
                line=dict(width=2),
                hovertemplate=f'Video: {video_id}<br>Plays: %{{y}}<br>Time: %{{x}}<extra></extra>'
            ))
        
        layout = go.Layout(
            title='Video Popularity Over Time',
            xaxis=dict(title='Time'),
            yaxis=dict(title='Play Count'),
            hovermode='closest',
            height=400
        )
        
        fig = go.Figure(data=traces, layout=layout)
        return jsonify(json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig)))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/genre-analysis')
def api_chart_genre_analysis():
    """API endpoint for genre analysis chart data"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get latest genre data
        cursor.execute("""
            SELECT genre, play_count, unique_users, avg_duration
            FROM genre_analysis 
            ORDER BY window_start DESC 
            LIMIT 20
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        genres = {}
        for row in rows:
            genre, play_count, unique_users, avg_duration = row
            if genre not in genres:
                genres[genre] = {
                    'play_counts': [],
                    'unique_users': [],
                    'avg_durations': []
                }
            
            genres[genre]['play_counts'].append(play_count)
            genres[genre]['unique_users'].append(unique_users)
            genres[genre]['avg_durations'].append(avg_duration)
        
        # Calculate averages
        genre_data = []
        for genre, data in genres.items():
            genre_data.append({
                'genre': genre,
                'avg_play_count': sum(data['play_counts']) / len(data['play_counts']),
                'avg_unique_users': sum(data['unique_users']) / len(data['unique_users']),
                'avg_duration': sum(data['avg_durations']) / len(data['avg_durations'])
            })
        
        # Create bar chart
        genres_list = [g['genre'] for g in genre_data]
        play_counts = [g['avg_play_count'] for g in genre_data]
        
        trace = go.Bar(
            x=genres_list,
            y=play_counts,
            marker=dict(color='lightblue'),
            hovertemplate='Genre: %{x}<br>Plays: %{y}<extra></extra>'
        )
        
        layout = go.Layout(
            title='Average Plays by Genre',
            xaxis=dict(title='Genre'),
            yaxis=dict(title='Average Play Count'),
            height=400
        )
        
        fig = go.Figure(data=[trace], layout=layout)
        return jsonify(json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig)))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/user-engagement')
def api_chart_user_engagement():
    """API endpoint for user engagement chart data"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get user engagement data
        cursor.execute("""
            SELECT user_id, session_duration, total_watch_time
            FROM user_engagement 
            ORDER BY window_start DESC 
            LIMIT 20
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        # Create scatter plot
        user_ids = [row[0] for row in rows]
        session_durations = [row[1] for row in rows]
        watch_times = [row[2] for row in rows]
        
        trace = go.Scatter(
            x=session_durations,
            y=watch_times,
            mode='markers',
            marker=dict(
                size=10,
                color=session_durations,
                colorscale='Viridis',
                showscale=True
            ),
            text=user_ids,
            hovertemplate='User: %{text}<br>Session: %{x} min<br>Watch Time: %{y} sec<extra></extra>'
        )
        
        layout = go.Layout(
            title='User Engagement: Session Duration vs Watch Time',
            xaxis=dict(title='Session Duration (minutes)'),
            yaxis=dict(title='Total Watch Time (seconds)'),
            height=400
        )
        
        fig = go.Figure(data=[trace], layout=layout)
        return jsonify(json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig)))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/anomalies-timeline')
def api_chart_anomalies_timeline():
    """API endpoint for anomalies timeline chart"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get anomalies over time
        cursor.execute("""
            SELECT alert_time, alert_type, COUNT(*) as count
            FROM anomalies 
            GROUP BY alert_time, alert_type
            ORDER BY alert_time DESC 
            LIMIT 50
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        # Process data
        timestamps = []
        alert_types = []
        counts = []
        
        for row in rows:
            timestamps.append(row[0])
            alert_types.append(row[1])
            counts.append(row[2])
        
        # Create timeline chart
        trace = go.Scatter(
            x=timestamps,
            y=counts,
            mode='lines+markers',
            line=dict(width=3),
            marker=dict(size=8),
            hovertemplate='Time: %{x}<br>Count: %{y}<br>Type: %{text}<extra></extra>',
            text=alert_types
        )
        
        layout = go.Layout(
            title='Anomalies Timeline',
            xaxis=dict(title='Time'),
            yaxis=dict(title='Anomaly Count'),
            height=400
        )
        
        fig = go.Figure(data=[trace], layout=layout)
        return jsonify(json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig)))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system-metrics')
def api_system_metrics():
    """API endpoint for system metrics"""
    try:
        system_stats = data_collector.metrics.get_system_stats()
        return jsonify(system_stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def api_health():
    """API endpoint for system health check"""
    try:
        # Check if database exists and is accessible
        db_exists = Path(DATABASE_PATH).exists()
        
        # Check if we have recent data
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM video_popularity")
        video_count = cursor.fetchone()[0]
        conn.close()
        
        health_status = {
            'database': 'healthy' if db_exists and video_count > 0 else 'unhealthy',
            'data_available': video_count > 0,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(health_status)
        
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'unhealthy'}), 500

def create_dashboard_templates():
    """Create HTML templates for the dashboard"""
    templates_dir = Path("templates")
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    # Main dashboard template
    dashboard_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Streaming Analytics Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        :root {
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --success-color: #27ae60;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --bg-color: #f8f9fa;
            --card-bg: #ffffff;
            --text-color: #333333;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
        }
        
        header {
            background-color: var(--primary-color);
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        header h1 {
            font-size: 1.5rem;
            font-weight: 600;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid var(--secondary-color);
        }
        
        .stat-card.success { border-left-color: var(--success-color); }
        .stat-card.warning { border-left-color: var(--warning-color); }
        .stat-card.danger { border-left-color: var(--danger-color); }
        
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .chart-card {
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .chart-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--primary-color);
        }
        
        .chart-container {
            width: 100%;
            height: 400px;
        }
        
        .table-card {
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        th {
            background-color: #f1f3f4;
            font-weight: 600;
            color: var(--primary-color);
        }
        
        .badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
            color: white;
        }
        
        .badge.success { background-color: var(--success-color); }
        .badge.warning { background-color: var(--warning-color); }
        .badge.danger { background-color: var(--danger-color); }
        
        .refresh-btn {
            background-color: var(--secondary-color);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: background-color 0.2s;
        }
        
        .refresh-btn:hover {
            background-color: #2980b9;
        }
        
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: var(--success-color);
            margin-right: 0.5rem;
        }
        
        .status-indicator.offline {
            background-color: var(--danger-color);
            box-shadow: 0 0 5px var(--danger-color);
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .charts-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>🚀 Streaming Analytics Dashboard</h1>
    </header>
    
    <div class="container">
        <!-- Status and Stats -->
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
            <div style="display: flex; align-items: center;">
                <span class="status-indicator" id="status-indicator"></span>
                <span id="status-text">System Online</span>
            </div>
            <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>
        </div>
        
        <!-- Key Metrics -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="total-events">-</div>
                <div class="stat-label">Total Events</div>
            </div>
            <div class="stat-card success">
                <div class="stat-value" id="throughput">-</div>
                <div class="stat-label">Throughput (events/sec)</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-value" id="avg-latency">-</div>
                <div class="stat-label">Avg Latency (seconds)</div>
            </div>
            <div class="stat-card danger">
                <div class="stat-value" id="anomaly-count">-</div>
                <div class="stat-label">Recent Anomalies</div>
            </div>
        </div>
        
        <!-- Charts -->
        <div class="charts-grid">
            <div class="chart-card">
                <div class="chart-title">📈 Video Popularity Over Time</div>
                <div id="chart-video-popularity" class="chart-container"></div>
            </div>
            <div class="chart-card">
                <div class="chart-title">🎬 Genre Analysis</div>
                <div id="chart-genre-analysis" class="chart-container"></div>
            </div>
            <div class="chart-card">
                <div class="chart-title">👥 User Engagement</div>
                <div id="chart-user-engagement" class="chart-container"></div>
            </div>
            <div class="chart-card">
                <div class="chart-title">⚠️ Anomalies Timeline</div>
                <div id="chart-anomalies" class="chart-container"></div>
            </div>
        </div>
        
        <!-- Recent Anomalies Table -->
        <div class="table-card">
            <h3 style="margin-bottom: 1rem; color: var(--primary-color);">🚨 Recent Anomalies</h3>
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Type</th>
                        <th>User ID</th>
                        <th>Video ID</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody id="anomalies-table-body">
                    <!-- Data will be populated by JavaScript -->
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Dashboard JavaScript
        let refreshInterval;
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            startAutoRefresh();
            refreshData();
        });
        
        function startAutoRefresh() {
            refreshInterval = setInterval(refreshData, 30000); // Refresh every 30 seconds
        }
        
        function stopAutoRefresh() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
        }
        
        async function refreshData() {
            try {
                // Update status
                updateStatus(true);
                
                // Fetch and update stats
                const stats = await fetch('/api/stats').then(r => r.json());
                updateStats(stats);
                
                // Fetch and update charts
                await updateCharts();
                
                // Fetch and update anomalies table
                const anomalies = await fetch('/api/anomalies').then(r => r.json());
                updateAnomaliesTable(anomalies);
                
            } catch (error) {
                console.error('Error refreshing data:', error);
                updateStatus(false);
            }
        }
        
        function updateStatus(online) {
            const indicator = document.getElementById('status-indicator');
            const text = document.getElementById('status-text');
            
            if (online) {
                indicator.classList.remove('offline');
                text.textContent = 'System Online';
            } else {
                indicator.classList.add('offline');
                text.textContent = 'System Offline - Retrying...';
            }
        }
        
        function updateStats(stats) {
            if (stats.throughput) {
                document.getElementById('total-events').textContent = stats.throughput.total_events || '-';
                document.getElementById('throughput').textContent = stats.throughput.recent_throughput || '-';
            }
            
            if (stats.latency) {
                document.getElementById('avg-latency').textContent = stats.latency.avg_latency || '-';
            }
            
            // Update anomaly count (placeholder - would need separate API call)
            document.getElementById('anomaly-count').textContent = 'Calculating...';
        }
        
        async function updateCharts() {
            // Update video popularity chart
            try {
                const videoData = await fetch('/api/charts/video-popularity').then(r => r.json());
                Plotly.newPlot('chart-video-popularity', videoData.data, videoData.layout, {responsive: true});
            } catch (error) {
                console.error('Error updating video popularity chart:', error);
            }
            
            // Update genre analysis chart
            try {
                const genreData = await fetch('/api/charts/genre-analysis').then(r => r.json());
                Plotly.newPlot('chart-genre-analysis', genreData.data, genreData.layout, {responsive: true});
            } catch (error) {
                console.error('Error updating genre analysis chart:', error);
            }
            
            // Update user engagement chart
            try {
                const engagementData = await fetch('/api/charts/user-engagement').then(r => r.json());
                Plotly.newPlot('chart-user-engagement', engagementData.data, engagementData.layout, {responsive: true});
            } catch (error) {
                console.error('Error updating user engagement chart:', error);
            }
            
            // Update anomalies timeline chart
            try {
                const anomaliesData = await fetch('/api/charts/anomalies-timeline').then(r => r.json());
                Plotly.newPlot('chart-anomalies', anomaliesData.data, anomaliesData.layout, {responsive: true});
            } catch (error) {
                console.error('Error updating anomalies timeline chart:', error);
            }
        }
        
        function updateAnomaliesTable(anomalies) {
            const tbody = document.getElementById('anomalies-table-body');
            tbody.innerHTML = '';
            
            if (!anomalies || anomalies.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #666;">No recent anomalies</td></tr>';
                return;
            }
            
            anomalies.slice(0, 10).forEach(anomaly => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${anomaly.alert_time || '-'}</td>
                    <td><span class="badge danger">${anomaly.alert_type || '-'}</span></td>
                    <td>${anomaly.user_id || '-'}</td>
                    <td>${anomaly.video_id || '-'}</td>
                    <td>Current Time: ${anomaly.current_time || '-'}s</td>
                `;
                tbody.appendChild(row);
            });
        }
    </script>
</body>
</html>
    """
    
    with open(templates_dir / "dashboard.html", "w", encoding="utf-8") as f:
        f.write(dashboard_html)
    
    print(f"Dashboard templates created in {templates_dir}")

def main():
    """Main function to start the dashboard"""
    # Create templates directory and files
    create_dashboard_templates()
    
    # Start data collector
    data_collector.start()
    
    print("Starting web dashboard...")
    print("Dashboard will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    
    try:
        # Start Flask app
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nShutting down dashboard...")
        data_collector.stop()
        print("Dashboard stopped.")

if __name__ == '__main__':
    main()