import http from 'http';

const data = JSON.stringify({
  email: 'test@amine.com',
  password: 'secure123',
  name: 'Amine'
});

const options = {
  hostname: 'localhost',
  port: 3000,
  path: '/api/auth/register',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': data.length
  }
};

const req = http.request(options, (res) => {
  let body = '';
  res.on('data', (chunk) => body += chunk);
  res.on('end', () => {
    console.log('STATUS:', res.statusCode);
    console.log('BODY:', body);
    process.exit(res.statusCode === 201 || res.statusCode === 200 ? 0 : 1);
  });
});

req.on('error', (e) => {
  console.error(e);
  process.exit(1);
});

req.write(data);
req.end();
