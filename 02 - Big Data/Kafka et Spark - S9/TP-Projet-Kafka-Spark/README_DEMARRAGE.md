# Guide de demarrage Kafka et ZooKeeper

## Probleme resolu
L'erreur `NodeExistsException` sur `/brokers/ids/0` etait causee par :
- Des sessions ZooKeeper orphelines suite a un arret brutal
- Un conflit de port 8080 (AdminServer ZooKeeper)

## Solution appliquee
1. ✅ Nettoyage des donnees ZooKeeper et Kafka
2. ✅ Desactivation de l'AdminServer ZooKeeper (port 8080)
3. ✅ Creation d'un script de demarrage fiable

## Comment demarrer les services

### Methode 1 : Utiliser le script batch (Recommande)

1. Ouvrir l'Explorateur de fichiers
2. Naviguer vers : `D:\M2\S9\TP-Projet-Kafka-Spark`
3. Double-cliquer sur : `start_kafka_fixed.bat`

Ce script va :
- Arreter les processus Java existants
- Nettoyer les donnees ZooKeeper
- Demarrer ZooKeeper (dans une fenetre)
- Attendre 5 secondes
- Demarrer Kafka (dans une fenetre)
- Creer le topic `streaming-events`

### Methode 2 : Manuellement (Si la methode 1 echoue)

**Etape 1 : Nettoyer les donnees**
```batch
rmdir /S /Q zookeeper-data
rmdir /S /Q zookeeper-logs
mkdir zookeeper-data
mkdir zookeeper-logs
```

**Etape 2 : Demarrer ZooKeeper**
```batch
cd D:\M2\S9\TP-Projet-Kafka-Spark\kafka
d:\M2\S9\kafka-install\kafka_2.13-3.8.1\bin\windows\zookeeper-server-start.bat config\zookeeper.properties
```

**Etape 3 : Attendre 10-15 secondes que ZooKeeper soit pret**

**Etape 4 : Demarrer Kafka (dans une NOUVELLE fenetre CMD)**
```batch
cd D:\M2\S9\TP-Projet-Kafka-Spark\kafka
d:\M2\S9\kafka-install\kafka_2.13-3.8.1\bin\windows\kafka-server-start.bat config\server.properties
```

**Etape 5 : Attendre 20-30 secondes que Kafka soit pret**

**Etape 6 : Creer le topic (dans une NOUVELLE fenetre CMD)**
```batch
d:\M2\S9\kafka-install\kafka_2.13-3.8.1\bin\windows\kafka-topics.bat --bootstrap-server localhost:9092 --create --topic streaming-events --partitions 3 --replication-factor 1
```

## Verification

Pour verifier que tout fonctionne :
```batch
d:\M2\S9\kafka-install\kafka_2.13-3.8.1\bin\windows\kafka-topics.bat --bootstrap-server localhost:9092 --list
```

Vous devriez voir : `streaming-events`

## Arret des services

Pour arreter proprement :
1. Fermer la fenetre Kafka (Ctrl+C ou croix)
2. Fermer la fenetre ZooKeeper (Ctrl+C ou croix)

Ou utiliser :
```batch
taskkill /F /IM java.exe
```

## Configuration modifiee

Le fichier `kafka/config/zookeeper.properties` a ete modifie :
```properties
# Desactive l'AdminServer pour eviter le conflit de port 8080
admin.enableServer=false
```

## Ports utilises

- ZooKeeper : 2181
- Kafka : 9092

## Fichiers crees

- `start_kafka_fixed.bat` : Script de demarrage automatique
- `start_services.py` : Script Python alternatif
