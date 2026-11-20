import fetch from 'node-fetch';

const GATEWAY_URL = 'http://localhost:3000/api';
let TOKEN = '';
let ORDER_ID = '';

async function runSimulation() {
  console.log('🚀 DÉMARRAGE DE LA SIMULATION SHOPFLOW\n');

  try {
    // 1. Inscription
    console.log('1️⃣ Inscription d\'un nouvel utilisateur...');
    const regRes = await fetch(`${GATEWAY_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'alice@example.com', password: 'password123', name: 'Alice' })
    });
    const user = await regRes.json();
    console.log('✅ Utilisateur inscrit:', user.id || 'OK');

    // 2. Connexion
    console.log('\n2️⃣ Connexion...');
    const loginRes = await fetch(`${GATEWAY_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'alice@example.com', password: 'password123' })
    });
    const auth = await loginRes.json();
    TOKEN = auth.token;
    console.log('✅ JWT obtenu (tronqué):', TOKEN.substring(0, 20) + '...');

    // 3. Création Produit
    console.log('\n3️⃣ Création d\'un produit (Admin)...');
    const prodRes = await fetch(`${GATEWAY_URL}/products`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${TOKEN}`
      },
      body: JSON.stringify({ 
        name: 'Gaming Laptop', 
        description: 'Elite performance', 
        price: 1500, 
        stock: 10,
        category: 'Electronics' 
      })
    });
    const product = await prodRes.json();
    console.log('✅ Produit créé:', product.name, `(ID: ${product.id})`);

    // 4. Passage de commande
    console.log('\n4️⃣ Passage d\'une commande...');
    const orderRes = await fetch(`${GATEWAY_URL}/orders`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${TOKEN}`
      },
      body: JSON.stringify({ 
        items: [{ productId: product.id, quantity: 1 }] 
      })
    });
    const order = await orderRes.json();
    ORDER_ID = order.id;
    console.log('✅ Commande validée:', ORDER_ID, `| Total: $${order.totalAmount}`);

    // 5. Paiement
    console.log('\n5️⃣ Simulation du paiement...');
    const payRes = await fetch(`${GATEWAY_URL}/payments`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${TOKEN}`
      },
      body: JSON.stringify({ orderId: ORDER_ID, amount: 1500 })
    });
    const payment = await payRes.json();
    console.log('✅ Paiement SUCCESS:', payment.transactionId);

    console.log('\n🏁 FIN DE LA SIMULATION COEUR');
    console.log('👀 Vérifiez maintenant les logs du Notification Service pour voir les alertes asynchrones !');

  } catch (err) {
    console.error('\n❌ ERREUR SIMULATION:', err.message);
    console.log('👉 Assurez-vous que l\'API Gateway et les microservices sont lancés.');
  }
}

runSimulation();
