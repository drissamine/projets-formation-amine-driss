# Réponses aux questions théoriques du Projet DevOps

**Créé par DRISS Amine**

## Partie 4 : Analyse de sécurité des images Docker avec Trivy

**1. Combien de vulnérabilités HIGH et CRITICAL sont détectées ?**
(Cette réponse dépend du résultat de la commande Trivy sur votre poste local. Il faut exécuter la commande pour obtenir le nombre exact.)

**2. Proviennent-elles de l'image de base (Node/Alpine) ou des dépendances applicatives ?**
Généralement, pour une image `node:18-alpine`, les vulnérabilités proviennent souvent du système de base (Alpine) de certaines bibliothèques système intégrées, ou parfois des packages NPM. Le rapport Trivy spécifiera la source.

**3. Quelles actions simples pouvez-vous proposer pour réduire le nombre de vulnérabilités ?**

- **Mettre à jour l'image de base** : utiliser la version la plus récente d'Alpine ou de Node (ex: `node:20-alpine`).
- **Mise à jour des dépendances** NPM (`npm audit fix`).
- Utiliser un scanneur de sécurité CI/CD pour bloquer les builds avec des failles critiques.
- **Réduction de la surface d'attaque** en utilisant des images `distroless` à la place d'Alpine, ou un scanner plus restrictif.

---

## Partie 6 : Déploiement de l'application dans K8s

### A. Namespaces et Contexts

**4. Pourquoi est-il important d'utiliser un namespace dédié dans un cluster partagé ?**
Il permet d'isoler les ressources entre différentes applications, équipes ou environnements (dev/prod). Il évite aussi les conflits de noms (par ex., on peut avoir deux pods appelés "app" dans des namespaces différents).

**5. Que se passe-t-il si vous appliquez un fichier YAML sans préciser le namespace ?**
Les ressources seront déployées dans le namespace par défaut, actuellement défini dans votre contexte local (généralement `default`).

**6. Quelle est la différence entre un namespace et un cluster Kubernetes ?**
Un cluster Kubernetes est l'infrastructure physique ou virtuelle complète (ensemble des nœuds, maître et travailleurs). Un namespace est une séparation _logique_ virtuelle à l'intérieur de ce cluster physique.

### B. Création d'un Pod applicatif simple

**3. Quelle est la différence entre une image Docker, un conteneur et un Pod ?**

- Image Docker : Modèle inactif et en lecture seule contenant l'application.
- Conteneur : Instance d'une image Docker en cours d'exécution.
- Pod : Unité de base dans Kubernetes, il peut contenir un ou plusieurs conteneurs qui partagent le même réseau et stockage.

**4. Que se passe-t-il si vous supprimez manuellement ce Pod ?**
S'il s'agit d'un Pod simple (non géré par un Deployment ou ReplicaSet), il est définitivement supprimé et ne sera pas recréé.

**5. Pourquoi un Pod seul n'est-il pas suffisant pour une application en production ?**
Un pod seul n'a pas d'auto-guérison (pas redémarré en cas de crash du nœud), pas de scaling automatique et on ne peut le mettre à jour sans interruption de service.

### C. Exposition du Pod via un Service

**3. Pourquoi Kubernetes introduit-il la notion de Service ?**
Un Service permet d'exposer une application s'exécutant sur un ensemble de Pods avec une IP réseau unique et stable. Il agit comme un load-balancer interne.

**4. Que se passerait-il si l'adresse IP du Pod changeait ?**
Sans Service, l'application cliente devrait connaître les nouvelles IP à chaque fois qu'un Pod est recréé. Avec un Service, le client utilise l'IP fixe (ClusterIP) du Service, qui route le trafic vers la nouvelle IP du Pod de manière transparente.

**5. Quel est le rôle des labels et des selectors dans Kubernetes ?**
Les `labels` sont des mots-clés ajoutés aux Pods pour les identifier. Les `selectors` sont utilisés par les Services et Deployments pour sélectionner automatiquement les Pods portant des labels spécifiques.

### D. Externalisation de la configuration avec ConfigMap

**3. Pourquoi est-il recommandé de ne pas intégrer la configuration dans l'image Docker ?**
Pour séparer le code de sa configuration. Cela permet de déployer la même image sur de multiples environnements (dev, preprod, prod) en injectant simplement une `ConfigMap` différente, conformément au principe des "12 factors app".

**4. Que se passe-t-il si la ConfigMap est modifiée après le démarrage du Pod ?**
Si la configuration a été passée comme variable d'environnement, les changements ne seront pas appliqués tant que le Pod ne sera pas redémarré (car les vars d'env sont lues uniquement au démarrage).

**5. Dans quel cas faudrait-il redémarrer les Pods ?**
Il faut les redémarrer lors de modifications d'une ConfigMap ou Secret passés en variables d'environnement, afin que la nouvelle configuration soit chargée.

### E. Gestion des informations sensibles avec Secret

**2. Quelle est la différence entre une ConfigMap et un Secret ?**
Ils sont similaires, mais un `Secret` est conçu pour stocker des données confidentielles. Ses valeurs sont encodées en Base64 (au repos et en transfert) plutôt qu'en texte clair.

**3. Les Secrets sont-ils réellement sécurisés par défaut dans Kubernetes ?**
Pas complètement par défaut : ils sont simplement encodés en Base64. Pour une vraie sécurité, il faut activer le chiffrement au repos via etcd, ou utiliser des outils comme HashiCorp Vault ou AWS/Azure/GCP Secrets Manager.

**4. Pourquoi Kubernetes ne redémarre-t-il pas automatiquement les Pods après une modification du Secret ?**
Pour éviter des comportements imprévisibles et ne pas impacter les services sans prévenir l'administrateur. La mise à jour doit être réalisée explicitement (par ex, via un rolling-restart du Deployment).

### F. Déploiement du service Redis

**3. Pourquoi Redis ne doit-il pas être exposé vers l'extérieur ?**
Redis ne contient souvent aucune couche d'authentification robuste et est fait pour le stockage backend sécurisé. L'exposer créerait un risque de fuite de données et d'attaques d'ingénierie.

**4. Pourquoi l'application utilise-t-elle le nom du Service Redis et non son adresse IP ?**
Car l'adresse IP d'un pod ou même d'un service peut changer si elle est recréée. Le DNS de Kubernetes garantit que le nom de domaine `redis-service` pointera toujours vers l'IP en cours de validité.

**5. Que se passerait-il si Redis était déployé en tant que service externe ?**
Le service serait accessible par quiconque connaîtrait l'IP et le port public du cluster. Si aucune authentification forte n'est configurée, des pirates pourraient effacer, corrompre, ou voler la base de données.

### G. Déploiement final via un Deployment

**3. Quelle est la différence fondamentale entre un Pod et un Deployment ?**
Un `Pod` est une unité d'exécution statique de base. Un `Deployment` est un contrôleur de haut niveau : il gère les mises à jour progressives (rolling updates) et maintient un nombre défini de `Pods` en créant un `ReplicaSet`.

**4. Pourquoi Kubernetes est-il capable de recréer automatiquement des Pods ?**
Grâce au contrôleur logique `ReplicaSet` (créé par le Deployment). S'il observe que le nombre de pods opérationnels tombe en dessous de l'état désiré ("desired state"), il informe le scheduler de créer un nouveau Pod pour combler le manque.

**5. Quelle est la différence entre un redémarrage de conteneur et une recréation de Pod ?**
Si un processus plante, le kubelet redémarre le conteneur dans le même Pod existant (gardant la même IP de Pod). Si le Node entier crash, ou si le Pod est jeté, Kubernetes programme un tout nouveau Pod sur un Node sain (avec une nouvelle IP).

### Questions de synthèse de la Partie 6

- **Progression logique Pod -> Service -> Deployment :**
  - **Pod** : on exécute l'application. (Problème: il meurt et perd son IP).
  - **Service** : on donne une IP fixe pour contacter le Pod. (Problème: toujours un seul point d'échec de notre application).
  - **Deployment** : on crée de multiples réplicas et on met en place un mécanisme d'auto-guérison et de rolling-update transparent pour le Service.
- **Problèmes résolus par K8s vs Docker seul :** Orchestration multi-nœuds, auto-guérison, rolling updates, découverte de services, load-balancing interne, gestion du volume persistant, etc.
- **Ressource responsable de l'auto-guérison :** Le contrôleur `ReplicaSet` (qui est géré par la ressource `Deployment`).
- **Bonnes pratiques appliquées :** Utilisation de Namespaces, séparation Config/Code (ConfigMap/Secrets), sécurité locale réseau via ClusterIP et sondes d'observabilité (Liveness et Readiness).

---

## Partie 7 : Gestion de l'état et application scalables

**A. Scalabilité Automatique avec HPA**
**5. Le HPA scale-t-il immédiatement ? Pourquoi existe-t-il un délai de « stabilisation » (cooldown) ?**
Il ne scale pas instantanément pour lisser les pics temporaires (et éviter de créer/terminer sans cesse des pods pour des sauts très brefs). Le "cooldown" (souvent 5 minutes en scale-down) protège le cluster contre l'instabilité (effet yo-yo).

**6. Pourquoi un HPA basé uniquement sur le CPU peut-il être insuffisant pour une application gérant de gros transferts de fichiers ?**
Une application I/O bound (transferts) peut être engorgée au niveau réseau, ou du disque, ou de la mémoire sans vraiment mobiliser 100% de CPU. Dans ce cas, se baser uniquement sur le CPU ne traduirait en rien le fait que l'app est sous stress.

**B. Auto-healing (Auto-guérison) et Haute Disponibilité**
**3. Que devient l'adresse IP du Pod recréé ? Quel mécanisme assure la continuité d'accès ?**
Le Pod recréé obtient une nouvelle adresse IP. C'est le **Service** qui assure la continuité car il est un "proxy" qui met à jour dynamiquement sa liste d'endpoints (vers la nouvelle IP).

**4. Quelle ressource est techniquement responsable de maintenir le nombre de réplicas ?**
Le **ReplicaSet**.

**C. Mises à jour fluides (Rolling Update) et Rollback**
**4. Quel est le rôle crucial des Readiness Probes pendant que Kubernetes remplace les anciens Pods ?**
La Readiness Probe vérifie que le nouveau Pod est réellement prêt à recevoir du trafic avant qu'il ne soit intégré par le Service. Ainsi, le contrôleur ne terminera pas l'ancien Pod s'il voit que le nouveau Pod s'allume mais ne réussit pas sa sonde "readiness".

**5. Que signifient les paramètres maxSurge et maxUnavailable ?**

- `maxSurge` : nombre maximum de pods que l'on peut ajouter _au-delà_ du compte désiré pendant l'update.
- `maxUnavailable` : nombre maximum de pods pouvant être en état indisponible.

**D. Gestion de l'état : Déploiement de Redis avec StatefulSet**
**2. À quoi sert un Service « Headless » pour un StatefulSet ?**
Un "Headless Service" (ClusterIP: None) ne possède pas d'IP unique ni de load balancing. Ses enregistrements DNS pointent directement vers les adresses IP individuelles de tous les Pods (permettant la découverte peer-to-peer, essentiel pour créer un Cluster DB).

**4. Quel est le nom du Pod créé ?**
Il portera le nom défini avec un indice précis, ex: `redis-0`.

**6. Pourquoi l'identité stable (redis-0, redis-1) est-elle critique pour un système de base de données en cluster ?**
Parce que dans les bases de données distribuées (maître-esclave ou multi-maîtres), chaque nœud doit savoir à qui se synchroniser. Si leurs noms de domaines/identités changeaient, le cluster entier se désynchroniserait.

**7. Si vous passez à 3 réplicas, comment Kubernetes gère-t-il les volumes (PVC) ?**
Le StatefulSet utilise un "Volume Claim Template". Il crée ainsi pour _chaque_ pod un PVC individuel dédié. Il y a donc un volume par Pod, contrairement au Deployment où tous auraient pointé vers un même disque.

**8. En quoi le stockage persistant change-t-il la manière de « penser » le redémarrage dans Kubernetes ?**
Par défaut, Docker ou les Pods normaux effacent toutes les données (concept éphémère). Avec le StatefulSet et les PV, le cycle de vie de la "donnée" devient totalement découplé du cycle de vie du "conteneur" ou "pod". Si le Pod "redis-0" meurt, lorsqu'il redémarre sur une nouvelle machine, Kubernetes attache automatiquement l'ancien disque contenant les informations.

---

## Partie 8 : Supervision et Observabilité

**C. Configuration du "Scraping" (Collecte)**
**5. Quel est l'avantage d'utiliser un ServiceMonitor plutôt que des annotations directement sur les Pods dans un cluster contenant des centaines d'applications ?**
Le `ServiceMonitor` permet une gestion extrêmement centralisée et déclarative de l'observabilité. On définit via des "Label Selectors" qui est supervisé et comment, sans avoir à modifier et polluer le manifest original de chaque application ou équipe de dev.

**D. Analyse et Diagnostic**
**Pourquoi est-il crucial de surveiller la métrique nodejs_eventloop_lag_seconds pour une application Node.js ?**
Node.js est single-threaded pour de nombreuses tâches. Si la "boucle d'événements" est ralentie/bloquée, le serveur ne réussira plus à répondre aux appels I/O asynchrones ni aux connexions entrantes, causant une paralysie globale. Cette métrique est le signal d'alarme n°1 d'un thread Javascript asynchrone bloqué par une opération synchrone prolongée.
