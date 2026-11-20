@echo off
chcp 65001 >nul
echo ==========================================
echo  KAFKA-SPARK PIPELINE - Lancement Complet
echo ==========================================
echo.

set KAFKA_BIN=d:\M2\S9\kafka-install\kafka_2.13-3.8.1\bin\windows
set CONFIG_DIR=%~dp0kafka\config

:: Nettoyer les anciennes données ZooKeeper/Kafka
echo [1/7] Nettoyage des donnees anciennes...
cd kafka
rmdir /s /q zookeeper-data 2>nul
rmdir /s /q zookeeper-logs 2>nul
rmdir /s /q kafka-logs 2>nul
mkdir zookeeper-data
mkdir zookeeper-logs
mkdir kafka-logs
cd ..
echo     OK - Nettoyage termine

:: Lancer ZooKeeper dans une nouvelle fenêtre
echo [2/7] Demarrage de ZooKeeper...
start "ZooKeeper" cmd /k "echo === ZOOKEEPER === & %KAFKA_BIN%\zookeeper-server-start.bat %CONFIG_DIR%\zookeeper.properties"
timeout /t 5 /nobreak >nul

:: Lancer Kafka dans une nouvelle fenêtre
echo [3/7] Demarrage de Kafka...
start "Kafka" cmd /k "echo === KAFKA === & timeout /t 5 /nobreak >nul & %KAFKA_BIN%\kafka-server-start.bat %CONFIG_DIR%\server.properties"

:: Attendre que Kafka soit prêt
echo [4/7] Attente du demarrage de Kafka (15 secondes)...
timeout /t 15 /nobreak >nul

:: Créer le topic
echo [5/7] Creation du topic 'streaming-events'...
%KAFKA_BIN%\kafka-topics.bat --create --topic streaming-events --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 2>nul
if %errorlevel% == 0 (
    echo     OK - Topic cree
) else (
    echo     OK - Topic existe deja
)

:: Lister les topics pour vérifier
echo     Topics disponibles:
%KAFKA_BIN%\kafka-topics.bat --list --bootstrap-server localhost:9092 2>nul | findstr streaming

:: Lancer les tests
echo.
echo ==========================================
echo [6/7] Execution des Tests
echo ==========================================
echo.

python -m pytest tests/ -v --tb=short

:: Afficher le résumé
echo.
echo ==========================================
echo [7/7] Resume
echo ==========================================
echo.
echo ✅ Pipeline pret !
echo.
echo Commandes:
echo   Spark:  python spark/consumer/spark_streaming_app.py
echo   Producer: python producer/kafka_producer.py --continuous --delay 0.5
echo   Arret: .\stop_all.bat
echo.
pause
