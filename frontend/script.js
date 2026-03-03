const API_BASE = 'http://127.0.0.1:5000/api';  // change to deployed backend later

// Helper: get stored token
function getToken() {
    return localStorage.getItem('token');
}

// Helper: include auth header
function authFetch(url, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers
    };
    return fetch(url, { ...options, headers });
}

// --- Login/Register Page Logic ---
if (window.location.pathname.endsWith('index.html') || window.location.pathname === '/') {
    document.getElementById('login-tab').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('login-tab').classList.add('active');
        document.getElementById('register-tab').classList.remove('active');
        document.getElementById('login-form').style.display = 'block';
        document.getElementById('register-form').style.display = 'none';
    });
    document.getElementById('register-tab').addEventListener('click', (e) => {
        e.preventDefault();
        document.getElementById('register-tab').classList.add('active');
        document.getElementById('login-tab').classList.remove('active');
        document.getElementById('register-form').style.display = 'block';
        document.getElementById('login-form').style.display = 'none';
    });
}

async function register() {
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const msgDiv = document.getElementById('register-message');
    
    const response = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
    });
    const data = await response.json();
    if (response.ok) {
        localStorage.setItem('token', data.token);
        window.location.href = 'dashboard.html';
    } else {
        msgDiv.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
    }
}

async function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    const msgDiv = document.getElementById('login-message');
    
    const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    const data = await response.json();
    if (response.ok) {
        localStorage.setItem('token', data.token);
        window.location.href = 'dashboard.html';
    } else {
        msgDiv.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
    }
}

// --- Dashboard Functions (only if on dashboard) ---
if (window.location.pathname.endsWith('dashboard.html')) {
    // Load portfolio and orders on page load
    loadPortfolio();
    loadOrders();
    // Refresh every 10 seconds
    setInterval(() => {
        loadPortfolio();
        loadOrders();
    }, 10000);
}

async function loadPortfolio() {
    const response = await authFetch(`${API_BASE}/portfolio/`);
    const data = await response.json();
    if (response.ok) {
        document.getElementById('cash-balance').textContent = data.cash_balance.toFixed(2);
        document.getElementById('total-value').textContent = data.total_value.toFixed(2);
        
        const holdingsDiv = document.getElementById('holdings-list');
        if (data.holdings.length === 0) {
            holdingsDiv.innerHTML = '<p>No holdings</p>';
        } else {
            let html = '<ul class="list-group">';
            data.holdings.forEach(h => {
                const plClass = h.unrealized_pl >= 0 ? 'positive' : 'negative';
                html += `<li class="list-group-item d-flex justify-content-between align-items-center">
                    ${h.symbol} ${h.quantity} shares @ $${h.avg_price.toFixed(2)}<br>
                    Current: $${h.current_price.toFixed(2)} 
                    <span class="${plClass}">$${h.unrealized_pl.toFixed(2)}</span>
                </li>`;
            });
            html += '</ul>';
            holdingsDiv.innerHTML = html;
        }
    } else {
        console.error('Failed to load portfolio');
    }
}

async function loadOrders() {
    const response = await authFetch(`${API_BASE}/orders/`);
    const orders = await response.json();
    const ordersDiv = document.getElementById('orders-list');
    if (orders.length === 0) {
        ordersDiv.innerHTML = '<p>No orders</p>';
    } else {
        let html = '<ul class="list-group">';
        orders.slice(0, 5).forEach(o => {
            html += `<li class="list-group-item">${o.side.toUpperCase()} ${o.quantity} ${o.symbol} @ $${o.price.toFixed(2)} on ${new Date(o.created_at).toLocaleDateString()}</li>`;
        });
        html += '</ul>';
        ordersDiv.innerHTML = html;
    }
}

async function lookupStock() {
    const symbol = document.getElementById('symbol').value.toUpperCase();
    if (!symbol) return;
    const response = await authFetch(`${API_BASE}/stocks/quote/${symbol}`);
    const data = await response.json();
    const quoteDiv = document.getElementById('quote-result');
    if (response.ok) {
        const changeClass = data.change >= 0 ? 'positive' : 'negative';
        quoteDiv.innerHTML = `
            <div class="alert alert-info">
                <strong>${data.symbol}</strong> $${data.price.toFixed(2)} 
                <span class="${changeClass}">${data.change.toFixed(2)} (${data.change_percent}%)</span>
            </div>
        `;
        // Also fetch historical for chart
        fetchHistorical(symbol);
    } else {
        quoteDiv.innerHTML = `<div class="alert alert-warning">${data.message}</div>`;
    }
}

let chartInstance = null;
async function fetchHistorical(symbol) {
    const response = await authFetch(`${API_BASE}/stocks/historical/${symbol}`);
    const data = await response.json();
    if (data.length === 0) return;
    
    const ctx = document.getElementById('stockChart').getContext('2d');
    if (chartInstance) chartInstance.destroy();
    
    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.date).reverse(),
            datasets: [{
                label: `${symbol} Close Price`,
                data: data.map(d => d.close).reverse(),
                borderColor: 'blue',
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

async function placeOrder(side) {
    const symbol = document.getElementById('trade-symbol').value.toUpperCase();
    const quantity = parseInt(document.getElementById('trade-quantity').value);
    if (!symbol || !quantity) {
        alert('Enter symbol and quantity');
        return;
    }
    
    const response = await authFetch(`${API_BASE}/orders/`, {
        method: 'POST',
        body: JSON.stringify({ symbol, side, quantity })
    });
    const data = await response.json();
    const msgDiv = document.getElementById('trade-message');
    if (response.ok) {
        msgDiv.innerHTML = `<div class="alert alert-success">Order filled at $${data.price.toFixed(2)}. Cash: $${data.cash_balance.toFixed(2)}</div>`;
        loadPortfolio();
        loadOrders();
    } else {
        msgDiv.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
    }
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = 'index.html';
}
