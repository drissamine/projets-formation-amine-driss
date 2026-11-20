# Script de déploiement tout-en-un (Windows / PowerShell).
# Démarre Kafka, attend qu'il soit prêt, crée les topics et installe les dépendances Python.
#
# Usage : pwsh scripts/setup.ps1
$ErrorActionPreference = "Stop"

# Se placer à la racine du projet (parent de scripts/)
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
Write-Host "==> Racine du projet : $root" -ForegroundColor Cyan

# --- 1. Vérification des prérequis -----------------------------------------
Write-Host "`n==> Vérification des prérequis..." -ForegroundColor Cyan
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker introuvable. Installe Docker Desktop puis relance."
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python introuvable. Installe Python 3.9+ puis relance."
}
docker info *> $null
if ($LASTEXITCODE -ne 0) { throw "Le démon Docker ne répond pas. Démarre Docker Desktop." }
Write-Host "   Docker et Python OK."

# Avertissement JAVA_HOME / HADOOP_HOME (requis par Spark, pas par Kafka)
foreach ($v in @("JAVA_HOME", "HADOOP_HOME")) {
    $val = [Environment]::GetEnvironmentVariable($v)
    if ([string]::IsNullOrEmpty($val)) {
        Write-Host "   [info] $v non défini — requis pour exécuter Spark (voir README / .env)." -ForegroundColor Yellow
    } else {
        Write-Host "   $v = $val"
    }
}

# --- 2. Démarrage de l'infrastructure --------------------------------------
Write-Host "`n==> Démarrage de Kafka + Kafka UI (docker compose up -d)..." -ForegroundColor Cyan
docker compose up -d
if ($LASTEXITCODE -ne 0) { throw "Échec de docker compose up." }

# --- 3. Attente que Kafka soit prêt ----------------------------------------
Write-Host "`n==> Attente que Kafka soit prêt..." -ForegroundColor Cyan
$ready = $false
for ($i = 1; $i -le 30; $i++) {
    docker exec kafka /opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092 *> $null
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    Start-Sleep -Seconds 2
    Write-Host "   ... ($i/30)"
}
if (-not $ready) { throw "Kafka n'est pas devenu disponible à temps." }
Write-Host "   Kafka est prêt."

# --- 4. Création des topics -------------------------------------------------
Write-Host "`n==> Création des topics..." -ForegroundColor Cyan
& "$PSScriptRoot/create_topic.ps1"

# --- 5. Dépendances Python -------------------------------------------------
Write-Host "`n==> Installation des dépendances Python..." -ForegroundColor Cyan
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
Write-Host "   Dépendances installées."

# --- Fin -------------------------------------------------------------------
Write-Host "`n==================================================" -ForegroundColor Green
Write-Host " Déploiement terminé." -ForegroundColor Green
Write-Host " Kafka UI : http://localhost:8080" -ForegroundColor Green
Write-Host ""
Write-Host " Étapes suivantes :" -ForegroundColor Green
Write-Host "   python -m src.producer.producer --rate 50"
Write-Host "   python -m src.consumer.streaming_app --once --from-beginning"
Write-Host "==================================================" -ForegroundColor Green
