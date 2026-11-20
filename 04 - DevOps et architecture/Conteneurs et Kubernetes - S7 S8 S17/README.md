# Projet DevOps - Gestions des états scalables & observabilité

## Structure du projet

- `app/` : Code source Node.js et Dockerfile.
- `k8s/` : Manifestes Kubernetes (Deployment, Service, HPA, StatefulSet, ServiceMonitor).

---

## 1. Application Node.js (Stateless) & Auto-Scaling (HPA)

### Construction et déploiement

```bash
cd app
docker build -t mon-app-js:1.0 .
# (Si vous utilisez Minikube) : minikube image load mon-app-js:1.0

cd ../k8s
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml
kubectl apply -f hpa.yaml
```

### Test de montée en charge (HPA)

1. Ouvrir un terminal et observer le HPA :
   ```bash
   kubectl get hpa -w
   ```
2. Dans un autre terminal, générer de la charge (Windows PowerShell) :
   ```powershell
   while($true) { curl http://localhost:80/heavy?ms=500; Start-Sleep -Milliseconds 100 }
   # Remarque: Utilisez le port exposé par le service ou un port-forward
   # kubectl port-forward svc/mon-app-service 8080:80
   ```
3. Le nombre de pods devrait augmenter jusqu'à 6.

### Mises à jour fluides (Rolling Update)

```bash
# Modifier l'image à la volée
kubectl set image deployment/mon-app-deployment mon-app-js=mon-app-js:2.0
# Observer le statut du déploiement
kubectl rollout status deployment/mon-app-deployment
```

### Auto-guérison (Auto-healing)

```bash
# Supprimer un Pod au hasard
kubectl delete pod <nom-du-pod>
# Observer sa recréation immédiate
kubectl get pods -w
```

---

## 2. Base de données Redis (StatefulSet)

### Déploiement

```bash
kubectl apply -f redis-service.yaml
kubectl apply -f redis-statefulset.yaml
```

### Test de persistance

1. Se connecter au pod et enregistrer une donnée :
   ```bash
   kubectl exec -it redis-0 -- redis-cli
   127.0.0.1:6379> set test "DevOps_Power"
   127.0.0.1:6379> exit
   ```
2. Supprimer brutalement le pod :
   ```bash
   kubectl delete pod redis-0
   ```
3. Attendre la recréation du pod et vérifier que la donnée est toujours là :
   ```bash
   kubectl exec -it redis-0 -- redis-cli get test
   # Doit retourner "DevOps_Power"
   ```

---

## 3. Observabilité (Prometheus & Grafana)

### Installation de la stack Kube-Prometheus

_Avertissement : La stack kube-prometheus nécessite beaucoup de ressources._

```bash
git clone https://github.com/prometheus-operator/kube-prometheus.git
cd kube-prometheus
kubectl apply --server-side -f manifests/setup
kubectl apply -f manifests/
```

### Configurer le scraping de l'application

Le `ServiceMonitor` indique à Prometheus de scraper l'endpoint `/metric` de notre application.

```bash
kubectl apply -f backend-monitor.yaml
```

### Visualisation Grafana

```bash
kubectl port-forward svc/grafana 8082:3000 -n monitoring
# Ouvrir le navigateur sur http://localhost:8082 (admin/admin)
```

Dans Prometheus (Port 9090), la cible `mon-app-servicemonitor` devrait apparaître comme `UP`.
