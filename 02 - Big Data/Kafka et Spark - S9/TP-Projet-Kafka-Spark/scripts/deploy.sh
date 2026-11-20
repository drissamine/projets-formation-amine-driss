#!/bin/bash

# Deployment Script for Kafka-Spark Streaming Pipeline
# Usage: ./scripts/deploy.sh [environment]

set -e  # Exit on any error

# Configuration
ENVIRONMENT=${1:-development}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
KAFKA_HOME="/opt/kafka"
SPARK_HOME="/opt/spark"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Java
    if ! command -v java &> /dev/null; then
        error "Java is not installed or not in PATH"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    # Check Kafka
    if [ ! -d "$KAFKA_HOME" ]; then
        error "Kafka is not installed at $KAFKA_HOME"
        exit 1
    fi
    
    # Check Spark
    if [ ! -d "$SPARK_HOME" ]; then
        error "Spark is not installed at $SPARK_HOME"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Install Python dependencies
install_dependencies() {
    log "Installing Python dependencies..."
    
    # Install producer dependencies
    cd "$PROJECT_ROOT/producer"
    pip3 install -r requirements.txt
    
    # Install Spark consumer dependencies
    cd "$PROJECT_ROOT/spark/consumer"
    pip3 install -r requirements.txt
    
    # Install monitoring dependencies
    pip3 install psutil requests kafka-python
    
    success "Python dependencies installed"
}

# Setup environment variables
setup_environment() {
    log "Setting up environment variables..."
    
    # Create environment file
    cat > "$PROJECT_ROOT/.env" << EOF
# Environment Configuration
ENVIRONMENT=$ENVIRONMENT
KAFKA_HOME=$KAFKA_HOME
SPARK_HOME=$SPARK_HOME

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=streaming-events

# Spark Configuration
SPARK_CHECKPOINT_LOCATION=./checkpoints/spark-streaming
SPARK_OUTPUT_MODE=append

# Monitoring Configuration
MONITORING_INTERVAL=30
EOF
    
    # Source environment
    source "$PROJECT_ROOT/.env"
    
    # Set environment variables
    export SPARK_HOME="$SPARK_HOME"
    export PATH="$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin"
    export PYTHONPATH="$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-*.zip:$PYTHONPATH"
    
    success "Environment setup completed"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p "$PROJECT_ROOT/results/json"
    mkdir -p "$PROJECT_ROOT/results/csv"
    mkdir -p "$PROJECT_ROOT/checkpoints/spark-streaming"
    mkdir -p "$PROJECT_ROOT/backups"
    mkdir -p "$PROJECT_ROOT/logs"
    
    success "Directories created"
}

# Start Kafka cluster
start_kafka() {
    log "Starting Kafka cluster..."
    
    # Start ZooKeeper
    log "Starting ZooKeeper..."
    cd "$KAFKA_HOME"
    nohup bin/zookeeper-server-start.sh config/zookeeper.properties > "$PROJECT_ROOT/logs/zookeeper.log" 2>&1 &
    ZOOKEEPER_PID=$!
    echo $ZOOKEEPER_PID > "$PROJECT_ROOT/logs/zookeeper.pid"
    
    # Wait for ZooKeeper to start
    sleep 10
    
    # Start Kafka
    log "Starting Kafka..."
    nohup bin/kafka-server-start.sh config/server.properties > "$PROJECT_ROOT/logs/kafka.log" 2>&1 &
    KAFKA_PID=$!
    echo $KAFKA_PID > "$PROJECT_ROOT/logs/kafka.pid"
    
    # Wait for Kafka to start
    sleep 15
    
    # Create topic
    log "Creating Kafka topic..."
    bin/kafka-topics.sh --create --topic streaming-events --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
    
    success "Kafka cluster started"
}

# Start Spark cluster
start_spark() {
    log "Starting Spark cluster..."
    
    cd "$PROJECT_ROOT/spark/consumer"
    
    # Start Spark master and workers
    "$SPARK_HOME/sbin/start-master.sh"
    "$SPARK_HOME/sbin/start-worker.sh" spark://localhost:7077
    
    success "Spark cluster started"
}

# Start monitoring
start_monitoring() {
    log "Starting monitoring..."
    
    cd "$PROJECT_ROOT/monitoring"
    
    # Start monitoring in background
    nohup python3 metrics.py > "$PROJECT_ROOT/logs/monitoring.log" 2>&1 &
    MONITORING_PID=$!
    echo $MONITORING_PID > "$PROJECT_ROOT/logs/monitoring.pid"
    
    success "Monitoring started"
}

# Start the pipeline
start_pipeline() {
    log "Starting the pipeline..."
    
    # Start Spark consumer
    log "Starting Spark consumer..."
    cd "$PROJECT_ROOT/spark/consumer"
    nohup python3 spark_streaming_app.py > "$PROJECT_ROOT/logs/spark_consumer.log" 2>&1 &
    SPARK_CONSUMER_PID=$!
    echo $SPARK_CONSUMER_PID > "$PROJECT_ROOT/logs/spark_consumer.pid"
    
    # Wait for consumer to start
    sleep 10
    
    # Start Kafka producer
    log "Starting Kafka producer..."
    cd "$PROJECT_ROOT/producer"
    nohup python3 kafka_producer.py --continuous --delay 0.1 > "$PROJECT_ROOT/logs/kafka_producer.log" 2>&1 &
    KAFKA_PRODUCER_PID=$!
    echo $KAFKA_PRODUCER_PID > "$PROJECT_ROOT/logs/kafka_producer.pid"
    
    success "Pipeline started"
}

# Health check
health_check() {
    log "Performing health check..."
    
    # Check Kafka
    if ! curl -s http://localhost:2181/commands/stat > /dev/null 2>&1; then
        warning "ZooKeeper might not be running properly"
    fi
    
    # Check Spark
    if ! curl -s http://localhost:4040 > /dev/null 2>&1; then
        warning "Spark Web UI might not be accessible"
    fi
    
    # Check if processes are running
    if [ -f "$PROJECT_ROOT/logs/spark_consumer.pid" ]; then
        SPARK_PID=$(cat "$PROJECT_ROOT/logs/spark_consumer.pid")
        if ! kill -0 $SPARK_PID 2>/dev/null; then
            warning "Spark consumer might not be running"
        fi
    fi
    
    if [ -f "$PROJECT_ROOT/logs/kafka_producer.pid" ]; then
        KAFKA_PID=$(cat "$PROJECT_ROOT/logs/kafka_producer.pid")
        if ! kill -0 $KAFKA_PID 2>/dev/null; then
            warning "Kafka producer might not be running"
        fi
    fi
    
    success "Health check completed"
}

# Show status
show_status() {
    log "Pipeline Status:"
    echo "=================================="
    
    # Kafka status
    echo "Kafka:"
    if [ -f "$PROJECT_ROOT/logs/kafka.pid" ]; then
        KAFKA_PID=$(cat "$PROJECT_ROOT/logs/kafka.pid")
        if kill -0 $KAFKA_PID 2>/dev/null; then
            echo "  ✓ Kafka is running (PID: $KAFKA_PID)"
        else
            echo "  ✗ Kafka is not running"
        fi
    else
        echo "  ? Kafka status unknown"
    fi
    
    # Spark status
    echo "Spark:"
    if [ -f "$PROJECT_ROOT/logs/spark_consumer.pid" ]; then
        SPARK_PID=$(cat "$PROJECT_ROOT/logs/spark_consumer.pid")
        if kill -0 $SPARK_PID 2>/dev/null; then
            echo "  ✓ Spark consumer is running (PID: $SPARK_PID)"
        else
            echo "  ✗ Spark consumer is not running"
        fi
    else
        echo "  ? Spark status unknown"
    fi
    
    # Producer status
    echo "Producer:"
    if [ -f "$PROJECT_ROOT/logs/kafka_producer.pid" ]; then
        PRODUCER_PID=$(cat "$PROJECT_ROOT/logs/kafka_producer.pid")
        if kill -0 $PRODUCER_PID 2>/dev/null; then
            echo "  ✓ Kafka producer is running (PID: $PRODUCER_PID)"
        else
            echo "  ✗ Kafka producer is not running"
        fi
    else
        echo "  ? Producer status unknown"
    fi
    
    echo "=================================="
    echo ""
    echo "Useful URLs:"
    echo "  Spark Web UI: http://localhost:4040"
    echo "  Logs directory: $PROJECT_ROOT/logs/"
    echo "  Results directory: $PROJECT_ROOT/results/"
}

# Stop the pipeline
stop_pipeline() {
    log "Stopping the pipeline..."
    
    # Stop producer
    if [ -f "$PROJECT_ROOT/logs/kafka_producer.pid" ]; then
        PRODUCER_PID=$(cat "$PROJECT_ROOT/logs/kafka_producer.pid")
        log "Stopping Kafka producer (PID: $PRODUCER_PID)..."
        kill $PRODUCER_PID
        rm -f "$PROJECT_ROOT/logs/kafka_producer.pid"
    fi
    
    # Stop consumer
    if [ -f "$PROJECT_ROOT/logs/spark_consumer.pid" ]; then
        SPARK_PID=$(cat "$PROJECT_ROOT/logs/spark_consumer.pid")
        log "Stopping Spark consumer (PID: $SPARK_PID)..."
        kill $SPARK_PID
        rm -f "$PROJECT_ROOT/logs/spark_consumer.pid"
    fi
    
    success "Pipeline stopped"
}

# Stop all services
stop_all() {
    log "Stopping all services..."
    
    stop_pipeline
    
    # Stop Spark cluster
    log "Stopping Spark cluster..."
    "$SPARK_HOME/sbin/stop-all.sh"
    
    # Stop Kafka
    if [ -f "$PROJECT_ROOT/logs/kafka.pid" ]; then
        KAFKA_PID=$(cat "$PROJECT_ROOT/logs/kafka.pid")
        log "Stopping Kafka (PID: $KAFKA_PID)..."
        kill $KAFKA_PID
        rm -f "$PROJECT_ROOT/logs/kafka.pid"
    fi
    
    if [ -f "$PROJECT_ROOT/logs/zookeeper.pid" ]; then
        ZOOKEEPER_PID=$(cat "$PROJECT_ROOT/logs/zookeeper.pid")
        log "Stopping ZooKeeper (PID: $ZOOKEEPER_PID)..."
        kill $ZOOKEEPER_PID
        rm -f "$PROJECT_ROOT/logs/zookeeper.pid"
    fi
    
    # Stop monitoring
    if [ -f "$PROJECT_ROOT/logs/monitoring.pid" ]; then
        MONITORING_PID=$(cat "$PROJECT_ROOT/logs/monitoring.pid")
        log "Stopping monitoring (PID: $MONITORING_PID)..."
        kill $MONITORING_PID
        rm -f "$PROJECT_ROOT/logs/monitoring.pid"
    fi
    
    success "All services stopped"
}

# Cleanup
cleanup() {
    log "Performing cleanup..."
    
    # Clean old logs (older than 7 days)
    find "$PROJECT_ROOT/logs/" -name "*.log" -mtime +7 -delete
    
    # Clean old results (older than 30 days)
    find "$PROJECT_ROOT/results/" -type f -mtime +30 -delete
    
    # Clean old backups (older than 90 days)
    find "$PROJECT_ROOT/backups/" -type f -mtime +90 -delete
    
    success "Cleanup completed"
}

# Backup
backup() {
    log "Creating backup..."
    
    BACKUP_DIR="$PROJECT_ROOT/backups"
    BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    tar -czf "$BACKUP_FILE" \
        "$PROJECT_ROOT/results/" \
        "$PROJECT_ROOT/checkpoints/" \
        "$PROJECT_ROOT/logs/" \
        "$PROJECT_ROOT/.env"
    
    success "Backup created: $BACKUP_FILE"
}

# Main deployment function
deploy() {
    log "Starting deployment for environment: $ENVIRONMENT"
    
    check_prerequisites
    install_dependencies
    setup_environment
    create_directories
    start_kafka
    start_spark
    start_monitoring
    start_pipeline
    health_check
    show_status
    
    success "Deployment completed successfully!"
    log "Pipeline is now running. Use './scripts/deploy.sh status' to check status."
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "start")
        start_kafka
        start_spark
        start_monitoring
        start_pipeline
        show_status
        ;;
    "stop")
        stop_all
        ;;
    "restart")
        stop_all
        sleep 5
        deploy
        ;;
    "status")
        show_status
        ;;
    "health")
        health_check
        ;;
    "cleanup")
        cleanup
        ;;
    "backup")
        backup
        ;;
    "logs")
        if [ -n "$2" ]; then
            tail -f "$PROJECT_ROOT/logs/$2.log"
        else
            echo "Available log files:"
            ls "$PROJECT_ROOT/logs/"*.log 2>/dev/null || echo "No log files found"
        fi
        ;;
    "test")
        log "Running tests..."
        cd "$PROJECT_ROOT"
        python3 -m pytest tests/ -v
        ;;
    *)
        echo "Usage: $0 {deploy|start|stop|restart|status|health|cleanup|backup|logs [file]|test}"
        echo ""
        echo "Commands:"
        echo "  deploy    - Full deployment (default)"
        echo "  start     - Start all services"
        echo "  stop      - Stop all services"
        echo "  restart   - Restart all services"
        echo "  status    - Show pipeline status"
        echo "  health    - Perform health check"
        echo "  cleanup   - Clean old files"
        echo "  backup    - Create backup"
        echo "  logs [file] - Show logs (optionally specify file)"
        echo "  test      - Run tests"
        exit 1
        ;;
esac