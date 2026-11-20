@echo off
set ROOT_DIR=D:\M2\S9\TP-Projet-Kafka-Spark
set KAFKA_HOME=d:\M2\S9\kafka-install\kafka_2.13-3.8.1
set KAFKA_BIN=%KAFKA_HOME%\bin\windows
set CONFIG_DIR=%ROOT_DIR%\kafka\config

echo ============================================================
echo Demarrage du Pipeline Kafka-Spark (Version Bat)
echo ============================================================

echo [1/4] Arret des processus Java existants...
taskkill /F /IM java.exe /T 2>nul
timeout /t 5 /nobreak >nul

echo [2/4] Nettoyage des dossiers...
rmdir /S /Q "%ROOT_DIR%\zookeeper-data" 2>nul
rmdir /S /Q "%ROOT_DIR%\zookeeper-logs" 2>nul
rmdir /S /Q "%ROOT_DIR%\kafka-logs" 2>nul
rmdir /S /Q "%ROOT_DIR%\checkpoints" 2>nul
mkdir "%ROOT_DIR%\zookeeper-data"
mkdir "%ROOT_DIR%\zookeeper-logs"
mkdir "%ROOT_DIR%\kafka-logs"
mkdir "%ROOT_DIR%\checkpoints"
set TMP_LOGS=C:\tmp\kafka-logs
set TMP_ZK=C:\tmp\zookeeper
rmdir /S /Q "%TMP_LOGS%" 2>nul
rmdir /S /Q "%TMP_ZK%" 2>nul

echo [3/4] Demarrage de ZooKeeper...
start "ZooKeeper" cmd /c "%KAFKA_BIN%\zookeeper-server-start.bat %CONFIG_DIR%\zookeeper.properties > zookeeper_startup.log 2>&1"
echo     Attente de ZooKeeper (15s)...
timeout /t 15 /nobreak >nul

echo [4/4] Demarrage de Kafka...
start "Kafka" cmd /c "%KAFKA_BIN%\kafka-server-start.bat %CONFIG_DIR%\server.properties > kafka_startup.log 2>&1"
echo     Attente de Kafka (30s)...
timeout /t 30 /nobreak >nul

echo ============================================================
echo Verification et Creation du Topic...
echo ============================================================
"%KAFKA_BIN%\kafka-topics.bat" --bootstrap-server 127.0.0.1:9092 --create --topic streaming-events --partitions 3 --replication-factor 1
if %errorlevel% equ 0 (
    echo [OK] Topic 'streaming-events' cree avec succes.
) else (
    echo [NOTE] Le topic existe deja ou erreur de creation.
)

"%KAFKA_BIN%\kafka-topics.bat" --bootstrap-server 127.0.0.1:9092 --list

echo ============================================================
echo Pipeline pret.
echo ============================================================
pause
