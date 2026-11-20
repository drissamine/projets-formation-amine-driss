// Créé par DRISS Amine
const express = require('express');
const path = require('path');
const client = require('prom-client'); // Importation
const app = express();

// Configuration via variables d'environnement
const APP_MESSAGE = process.env.APP_MESSAGE || "Hello from mon-app-js";
const LOG_LEVEL = process.env.LOG_LEVEL || "info";
const FEATURE_HEAVY = process.env.FEATURE_HEAVY === "true";

// Metriques simples
const startedAt = Date.now();
let totalRequests = 0;

// Initialisation de la collecte des metriques par defaut
const collectDefaultMetrics = client.collectDefaultMetrics;
collectDefaultMetrics({ register: client.register });

app.use(express.json());
app.use(express.static(path.join(__dirname, 'src')));

// Logs simples (utile pour debug et supervision)
app.use((req, res, next) => {
    const start = Date.now();
    totalRequests++;
    res.on('finish', () => {
        const durationMs = Date.now() - start;
        if (LOG_LEVEL === "debug" || res.statusCode >= 400) {
            console.log(JSON.stringify({
                ts: new Date().toISOString(),
                method: req.method,
                path: req.path,
                status: res.statusCode,
                durationMs
            }));
        }
    });
    next();
});

// Route principale
app.get('/', (req, res) => {
    res.status(200).send(APP_MESSAGE);
});

// Endpoints d'observabilite
app.get('/health/live', (req, res) => res.status(200).send('Alive'));
app.get('/health/ready', (req, res) => res.status(200).send('Ready'));
app.get('/version', (req, res) => {
    res.json({ version: process.env.APP_VERSION || "1.0.0" });
});
app.get('/metrics', (req, res) => {
    const uptimeSec = Math.floor((Date.now() - startedAt) / 1000);
    res.type('text/plain').send(`app_uptime_seconds ${uptimeSec}\napp_requests_total ${totalRequests}`);
});

// Definition de la route /metric pour Prometheus (partie 8)
app.get('/metric', async (req, res) => {
    res.set('Content-Type', client.register.contentType);
    res.end(await client.register.metrics());
});

// Simulation de charge CPU (pour demo / tests)
app.get('/heavy', (req, res) => {
    if (!FEATURE_HEAVY) {
        return res.status(403).json({
            error: "FEATURE_HEAVY disabled",
            message: "Activez FEATURE_HEAVY=true dans la ConfigMap pour tester."
        });
    }
    const durationMs = Number(req.query.ms || 500);
    const end = Date.now() + durationMs;
    // Ce blocage volontaire va faire grimper l'usage CPU du Pod
    while (Date.now() < end) {}
    res.json({ status: "busy", simulatedCpuMs: durationMs, msg: "La boucle while a bloque l'Event Loop." });
});

module.exports = app;
