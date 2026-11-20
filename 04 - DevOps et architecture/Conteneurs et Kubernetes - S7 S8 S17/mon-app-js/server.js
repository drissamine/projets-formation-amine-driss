// Créé par DRISS Amine
const app = require('./app-backend');
const PORT = process.env.PORT || 3000;
const server = app.listen(PORT, () => {
    console.log(JSON.stringify({
        ts: new Date().toISOString(),
        level: "info",
        msg: "Server started",
        port: PORT
    }));
});
function shutdown(signal) {
    console.log(JSON.stringify({
        ts: new Date().toISOString(),
        level: "info",
        msg: `Signal ${signal} received: shutting down`
    }));
    server.close(() => {
        console.log(JSON.stringify({
            ts: new Date().toISOString(),
            level: "info",
            msg: "Server closed cleanly"
        }));
        process.exit(0);
    });
    setTimeout(() => process.exit(1), 10000).unref();
}
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
