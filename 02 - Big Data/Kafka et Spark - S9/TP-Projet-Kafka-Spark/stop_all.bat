@echo off
echo ==========================================
echo  Arrêt du Pipeline Kafka-Spark
echo ==========================================
echo.

set KAFKA_BIN=d:\M2\S9\kafka-install\kafka_2.13-3.8.1\bin\windows

echo [1/2] Arrêt de Kafka...
%KAFKA_BIN%\kafka-server-stop.bat 2>nul
taskkill /FI "WINDOWTITLE eq Kafka*" /F >nul 2>&1
echo     ✓ Kafka arrêté

echo [2/2] Arrêt de ZooKeeper...
%KAFKA_BIN%\zookeeper-server-stop.bat 2>nul
taskkill /FI "WINDOWTITLE eq ZooKeeper*" /F >nul 2>&1
echo     ✓ ZooKeeper arrêté

echo.
echo ==========================================
echo  Tous les services sont arrêtés
echo ==========================================
pause
