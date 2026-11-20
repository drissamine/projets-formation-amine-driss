@echo off
set KAFKA_BIN=d:\M2\S9\kafka-install\kafka_2.13-3.8.1\bin\windows
set CONFIG_DIR=%~dp0kafka\config

echo Arret des processus Java existants...
taskkill /F /IM java.exe 2>nul
timeout /t 2 /nobreak >nul

echo Nettoyage des donnees ZooKeeper et Kafka...
rmdir /S /Q zookeeper-data 2>nul
rmdir /S /Q zookeeper-logs 2>nul
rmdir /S /Q kafka-logs 2>nul
mkdir zookeeper-data
mkdir zookeeper-logs
mkdir kafka-logs

echo.
echo ==========================================
echo Demarrage de ZooKeeper...
echo ==========================================
start "ZooKeeper" cmd /k "%KAFKA_BIN%\zookeeper-server-start.bat %CONFIG_DIR%\zookeeper.properties"

echo Attente du demarrage de ZooKeeper (10 secondes)...
timeout /t 10 /nobreak >nul

echo.
echo ==========================================
echo Demarrage de Kafka...
echo ==========================================
start "Kafka" cmd /k "%KAFKA_BIN%\kafka-server-start.bat %CONFIG_DIR%\server.properties"

echo.
echo Attente du demarrage de Kafka (20 secondes)...
timeout /t 20 /nobreak >nul

echo.
echo ==========================================
echo Creation du topic streaming-events...
echo ==========================================
%KAFKA_BIN%\kafka-topics.bat --bootstrap-server localhost:9092 --create --topic streaming-events --partitions 3 --replication-factor 1
if %errorlevel% == 0 (
    echo Topic streaming-events cree avec succes.
) else (
    echo Erreur lors de la creation du topic (il existe peut-etre deja).
)

echo.
echo ==========================================
echo Verification des topics...
echo ==========================================
%KAFKA_BIN%\kafka-topics.bat --bootstrap-server localhost:9092 --list

echo.
echo ==========================================
echo Services demarres :
echo - ZooKeeper : localhost:2181
echo - Kafka     : localhost:9092
echo - Topic     : streaming-events
echo ==========================================
pause
