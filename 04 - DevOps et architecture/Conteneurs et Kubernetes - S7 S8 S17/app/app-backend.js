const express = require("express");
const client = require("prom-client");

const app = express();
const port = process.env.PORT || 3000;

// Constante pour activer la fonctionnalité CPU intensive
const FEATURE_HEAVY = process.env.FEATURE_HEAVY === "true";

// Initialisation de la collecte des métriques par défaut (pour Prometheus)
const collectDefaultMetrics = client.collectDefaultMetrics;
collectDefaultMetrics({ register: client.register });

// Route pour la simulation de charge CPU
app.get("/heavy", (req, res) => {
  // Vérification si la fonctionnalité est activée via variable d'environnement
  if (!FEATURE_HEAVY) {
    return res.status(403).json({
      error: "FEATURE_HEAVY disabled",
      message:
        "Activez FEATURE_HEAVY=true dans la ConfigMap (ou env) pour tester.",
    });
  }

  const durationMs = Number(req.query.ms || 500);
  const end = Date.now() + durationMs;

  // Ce blocage volontaire va faire grimper l'usage CPU du Pod
  while (Date.now() < end) {}

  res.json({
    status: "busy",
    simulatedCpuMs: durationMs,
    msg: "La boucle while a bloqué l'Event Loop.",
  });
});

// Définition de la route /metric pour Prometheus
app.get("/metric", async (req, res) => {
  res.set("Content-Type", client.register.contentType);
  res.end(await client.register.metrics());
});

app.get("/", (req, res) => {
  res.json({ message: "Bienvenue sur l'API Backend Ops" });
});

app.listen(port, () => {
  console.log(`Serveur démarré sur le port ${port}`);
});
