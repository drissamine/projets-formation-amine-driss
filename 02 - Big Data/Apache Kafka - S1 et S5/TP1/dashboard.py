from kafka import KafkaConsumer # pyright: ignore[reportMissingImports]
import json
from datetime import datetime, timezone
from collections import defaultdict
from rich.console import Console # pyright: ignore[reportMissingImports]
from rich.table import Table # pyright: ignore[reportMissingImports]
from rich.live import Live # pyright: ignore[reportMissingImports]
from rich.panel import Panel # pyright: ignore[reportMissingImports]
from rich.align import Align # pyright: ignore[reportMissingImports]
from rich.text import Text # pyright: ignore[reportMissingImports]
from rich.columns import Columns # pyright: ignore[reportMissingImports]
from rich import box # pyright: ignore[reportMissingImports]
import time

console = Console()

# Fonctions utilitaires
def update_stats(stats_dict, building, temperature):
    """Met à jour les statistiques d'un bâtiment"""
    if building not in stats_dict:
        stats_dict[building] = []
    stats_dict[building].append(temperature)
    # Limiter à 100 mesures par bâtiment pour éviter la surcharge
    if len(stats_dict[building]) > 100:
        stats_dict[building] = stats_dict[building][-50:]

def calculate_average(temperatures):
    """Calcule la moyenne des températures"""
    if not temperatures:
        return 0.0
    return round(sum(temperatures) / len(temperatures), 1)

def check_anomaly(temperature, sensor_id):
    """Vérifie si la température est anormale"""
    return temperature > 28.0

def get_temperature_color(temp):
    """Retourne la couleur en fonction de la température"""
    if temp >= 28:
        return "red"
    elif temp >= 26:
        return "yellow"
    elif temp >= 22:
        return "green"
    else:
        return "blue"

def get_status_emoji(status):
    """Retourne l'emoji correspondant au status"""
    if status == "ALERTE":
        return "🚨"
    elif status == "ATTENTION":
        return "⚠️"
    else:
        return "✅"

# Configuration du consumer
def create_consumer():
    """Crée un consumer Kafka"""
    try:
        consumer = KafkaConsumer(
            'iot-sensors',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
            auto_offset_reset='earliest'
        )
        return consumer
    except Exception as e:
        console.print(f"[bold red]❌ Erreur de connexion: {e}[/]", style="red")
        return None

# Variables globales
stats_by_building = defaultdict(list)
alerts = []
message_count = 0
connection_start_time = datetime.now(timezone.utc)

def create_header():
    """Crée l'en-tête moderne du dashboard"""
    # Titre principal avec style moderne
    title = Text("🏢 IoT TEMPERATURE DASHBOARD", style="bold white on blue")
    subtitle = Text("Système de monitoring en temps réel - Apache Kafka", style="italic cyan")
    
    # Panel de titre avec style moderne
    title_text = f"{title}\n{subtitle}"
    
    title_panel = Panel(
        title_text,
        border_style="blue",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    
    return title_panel

def create_stats_panel():
    """Crée le panel de statistiques avec design moderne"""
    # Panel de statistiques principal
    stats_table = Table(
        title="📊 STATISTIQUES PAR BÂTIMENT",
        show_header=True,
        header_style="bold white on blue",
        expand=True,
        box=box.ROUNDED,
        pad_edge=False
    )
    
    # Colonnes avec styles modernes
    stats_table.add_column("🏢 Bâtiment", style="bold cyan", no_wrap=True)
    stats_table.add_column("🌡️ Moyenne", style="bold green")
    stats_table.add_column("📉 Min", style="bold blue")
    stats_table.add_column("📈 Max", style="bold red")
    stats_table.add_column("📋 Échantillons", style="bold magenta")
    stats_table.add_column("🔍 Status", style="bold white")
    
    # Ajouter les statistiques pour chaque bâtiment
    for building_name, temperatures in stats_by_building.items():
        if temperatures:
            avg_temp = calculate_average(temperatures)
            min_temp = min(temperatures)
            max_temp = max(temperatures)
            count = len(temperatures)
            
            # Déterminer le status avec emoji
            if max_temp > 28:
                status = "ALERTE"
                status_style = "bold white on red"
            elif max_temp > 26:
                status = "ATTENTION"
                status_style = "bold white on yellow"
            else:
                status = "NORMAL"
                status_style = "bold white on green"
            
            # Couleurs pour les températures
            avg_color = get_temperature_color(avg_temp)
            min_color = get_temperature_color(min_temp)
            max_color = get_temperature_color(max_temp)
            
            status_emoji = get_status_emoji(status)
            
            stats_table.add_row(
                f"Bâtiment {building_name}",
                f"[{avg_color}]{avg_temp}°C[/]",
                f"[{min_color}]{min_temp}°C[/]",
                f"[{max_color}]{max_temp}°C[/]",
                f"[bold magenta]{count}[/]",
                f"[{status_style}]{status_emoji} {status}[/]"
            )
    
    # Panel avec style moderne
    stats_panel = Panel(
        stats_table,
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    
    return stats_panel

def create_alerts_panel():
    """Crée le panel d'alertes moderne"""
    recent_alerts = alerts[-8:] if alerts else []  # Limiter à 8 alertes
    
    if recent_alerts:
        alert_content = []
        for alert in reversed(recent_alerts):
            alert_content.append(f"[bold red]⚠️[/] {alert}")
        
        alert_text = "\n".join(alert_content)
        
        alert_panel = Panel(
            alert_text,
            title="🚨 ALERTES RÉCENTES",
            border_style="red",
            box=box.ROUNDED,
            padding=(1, 2)
        )
    else:
        alert_panel = Panel(
            "[bold green]✅ Aucune alerte active[/]\n[dim]Le système fonctionne normalement[/]",
            title="🚨 ALERTES RÉCENTES",
            border_style="green",
            box=box.ROUNDED,
            padding=(1, 2)
        )
    
    return alert_panel

def create_info_panel():
    """Crée le panel d'informations système"""
    current_time = datetime.now(timezone.utc)
    uptime = current_time - connection_start_time
    total_messages = sum(len(temps) for temps in stats_by_building.values())
    
    # Calcul des messages par seconde
    msg_per_sec = message_count / max(uptime.total_seconds(), 1) if uptime.total_seconds() > 0 else 0
    
    # Informations système avec icônes
    info_lines = [
        f"🕐 Mise à jour: [bold cyan]{current_time.strftime('%H:%M:%S')}[/]",
        f"⏱️ Uptime: [bold green]{str(uptime).split('.')[0]}[/]",
        f"📡 Topic: [bold blue]iot-sensors[/]",
        f"🏢 Bâtiments: [bold yellow]{len([b for b in stats_by_building.values() if b])}[/]",
        f"📊 Messages: [bold magenta]{total_messages:,}[/]",
        f"🔄 Messages/sec: [bold green]{msg_per_sec:.1f}[/]",
        f"📋 Liste: [bold white]{', '.join(stats_by_building.keys()) or 'Aucun'}[/]"
    ]
    
    info_text = "\n".join(info_lines)
    
    info_panel = Panel(
        info_text,
        title="ℹ️ INFORMATIONS SYSTÈME",
        border_style="blue",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    
    return info_panel

def create_live_stats():
    """Crée les statistiques en temps réel"""
    if not stats_by_building:
        return Panel(
            "[dim]En attente de données...[/]",
            title="📈 TEMPÉRATURES RÉCENTES",
            border_style="blue",
            box=box.ROUNDED
        )
    
    # Graphique simple en texte
    chart_lines = []
    for building_name, temperatures in stats_by_building.items():
        if temperatures:
            recent_temps = temperatures[-10:]  # 10 dernières mesures
            avg_recent = calculate_average(recent_temps)
            
            # Barres de progression ASCII
            bar_length = 15
            filled_length = int(bar_length * (avg_recent - 15) / (30 - 15))  # Normaliser entre 15-30°C
            filled_length = max(0, min(bar_length, filled_length))
            
            bar = "█" * filled_length + "░" * (bar_length - filled_length)
            temp_color = get_temperature_color(avg_recent)
            
            chart_lines.append(f"[bold cyan]{building_name}[/]: [{temp_color}]{bar}[/] {avg_recent}°C")
    
    chart_text = "\n".join(chart_lines)
    
    chart_panel = Panel(
        chart_text,
        title="📈 TEMPÉRATURES RÉCENTES",
        border_style="cyan",
        box=box.ROUNDED,
        padding=(1, 2)
    )
    
    return chart_panel

def create_dashboard():
    """Crée l'interface complète du dashboard avec layout amélioré"""
    
    # Créer le layout principal avec structure simplifiée
    dashboard = Table.grid(expand=True)
    dashboard.add_column()
    
    # 1. En-tête
    dashboard.add_row(create_header())
    dashboard.add_row("")
    
    # 2. Section principale - Statistiques (pleine largeur)
    dashboard.add_row(create_stats_panel())
    dashboard.add_row("")
    
    # 3. Section inférieure - Deux colonnes
    bottom_section = Table.grid()
    bottom_section.add_column()
    bottom_section.add_column()
    
    # Panel gauche - Alertes
    alerts_panel = create_alerts_panel()
    
    # Panel droite - Informations système
    info_panel = create_info_panel()
    
    bottom_section.add_row(alerts_panel, info_panel)
    dashboard.add_row(bottom_section)
    dashboard.add_row("")
    
    # 4. Section finale - Graphique temps réel et statut
    final_section = Table.grid()
    final_section.add_column()
    final_section.add_column()
    
    # Graphique temps réel
    live_stats_panel = create_live_stats()
    
    # Status du système
    status_text = "[bold green]●[/] Système opérationnel"
    if alerts:
        status_text = f"[bold yellow]●[/] {len(alerts)} alerte(s) active(s)"
    
    status_panel = Panel(
        status_text,
        title="🔍 STATUS",
        border_style="green",
        box=box.ROUNDED,
        padding=(1, 1)
    )
    
    final_section.add_row(live_stats_panel, status_panel)
    dashboard.add_row(final_section)
    
    return dashboard

def process_message(message):
    """Traite un message avec affichage moderne (sans spam console)"""
    global stats_by_building, alerts, message_count
    
    try:
        data = message.value
        if not data:
            return
            
        # Validation des données
        required_fields = ['sensor_id', 'temperature', 'building', 'timestamp']
        if not all(field in data for field in required_fields):
            return
            
        building = data['building']
        temperature = data['temperature']
        sensor_id = data['sensor_id']
        timestamp = data['timestamp']
        
        message_count += 1
        
        # Affichage moderne du message reçu (uniquement pour les alertes importantes)
        if check_anomaly(temperature, sensor_id):
            alert_msg = f"{sensor_id}: {temperature}°C ({timestamp})"
            alerts.append(alert_msg)
            console.print(f"[bold red]🚨 ALERTE: {alert_msg}[/]")
        
        # Mettre à jour les statistiques
        update_stats(stats_by_building, building, temperature)
        
        # Affichage périodique du statut (moins fréquent)
        if message_count % 50 == 0 and message_count > 0:
            uptime = datetime.now(timezone.utc) - connection_start_time
            msg_per_sec = message_count / max(uptime.total_seconds(), 1)
            console.print(f"[bold cyan]📊 {message_count:,} messages | {msg_per_sec:.1f} msg/sec[/]", style="green")
        
    except Exception as e:
        console.print(f"[bold red]❌ Erreur: {e}[/]", style="red")

def main():
    """Fonction principale du dashboard moderne avec affichage corrigé"""
    # Effacer la console et afficher l'écran de démarrage
    console.clear()
    
    # Écran de démarrage moderne
    startup_panel = Panel(
        "[bold blue]🚀 Démarrage du Dashboard IoT[/]\n\n"
        "[dim]Configuration de la connexion Kafka...[/]",
        title="🏢 IoT TEMPERATURE DASHBOARD",
        border_style="blue",
        box=box.ROUNDED,
        padding=(2, 4)
    )
    
    console.print(startup_panel)
    time.sleep(1)
    
    # Créer le consumer
    consumer = create_consumer()
    if not consumer:
        console.print("[bold red]❌ Impossible de se connecter à Kafka[/]", style="bold red")
        return
    
    try:
        # Démarrer l'interface Live
        with Live(create_dashboard(), refresh_per_second=2, screen=True, auto_refresh=True) as live:
            console.print("[bold green]✅ Dashboard actif![/] [dim]Interface en temps réel[/]", style="yellow")
            console.print("[dim]📨 Les messages s'affichent dans le dashboard[/]", style="dim")
            
            # Boucle principale de traitement
            for message in consumer:
                process_message(message)
                
                # Mettre à jour le dashboard
                live.update(create_dashboard())
                    
    except KeyboardInterrupt:
        console.print("\n[bold red]🛑 Arrêt demandé par l'utilisateur[/]")
    except Exception as e:
        console.print(f"[bold red]❌ Erreur critique: {e}[/]", style="bold red")
    finally:
        consumer.close()
        console.print("[bold blue]🔌 Connexion fermée proprement[/]", style="blue")

if __name__ == "__main__":
    main()
