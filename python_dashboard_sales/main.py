# %%
# generate_sales_dashboard.py
# Создает HTML-дашборд продаж из CSV файла

import pandas as pd
import json
from datetime import datetime
import numpy as np


# --- 1. ЗАГРУЗКА ДАННЫХ ---
def load_data():
    df = pd.read_csv(
        r'C:\Users\User\Desktop\Тестовое\python_dashboard_sales\sales_data_sample.csv',
        delimiter=',',
        encoding='windows-1252'
    )
    df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'], format='%m/%d/%Y %H:%M')
    df['YEAR_MONTH'] = df['ORDERDATE'].dt.to_period('M').astype(str)
    df = df.sort_values('ORDERDATE')
    return df


df = load_data()


# --- 2. АГРЕГАЦИЯ ДАННЫХ ДЛЯ ДАШБОРДА ---
def prepare_dashboard_data(df):
    """Подготавливает все данные для дашборда"""

    # KPI
    total_sales = float(df['SALES'].sum())
    total_orders = int(df['ORDERNUMBER'].nunique())
    avg_check = total_sales / total_orders if total_orders > 0 else 0
    total_items = int(df['QUANTITYORDERED'].sum())

    # Данные для графиков
    # 1. Динамика продаж по месяцам
    monthly_sales = df.groupby('YEAR_MONTH')['SALES'].sum().reset_index()
    monthly_sales = monthly_sales.sort_values('YEAR_MONTH')
    monthly_data = {
        'months': monthly_sales['YEAR_MONTH'].tolist(),
        'sales': [float(x) for x in monthly_sales['SALES'].tolist()]
    }

    # 2. Топ-5 клиентов
    top_customers = df.groupby('CUSTOMERNAME')['SALES'].sum().nlargest(5).reset_index()
    customers_data = {
        'names': top_customers['CUSTOMERNAME'].tolist(),
        'sales': [float(x) for x in top_customers['SALES'].tolist()]
    }

    # 3. Продажи по категориям
    product_sales = df.groupby('PRODUCTLINE')['SALES'].sum().reset_index()
    product_sales = product_sales.sort_values('SALES', ascending=False)
    products_data = {
        'categories': product_sales['PRODUCTLINE'].tolist(),
        'sales': [float(x) for x in product_sales['SALES'].tolist()]
    }

    # 4. Топ-10 стран
    country_sales = df.groupby('COUNTRY')['SALES'].sum().nlargest(10).reset_index()
    countries_data = {
        'countries': country_sales['COUNTRY'].tolist(),
        'sales': [float(x) for x in country_sales['SALES'].tolist()]
    }

    # 5. Последние транзакции
    display_cols = ['ORDERDATE', 'CUSTOMERNAME', 'PRODUCTLINE', 'SALES', 'COUNTRY', 'STATUS']
    last_orders = df[display_cols].tail(10).sort_values('ORDERDATE', ascending=False)
    transactions = []
    for _, row in last_orders.iterrows():
        transactions.append({
            'date': row['ORDERDATE'].strftime('%Y-%m-%d'),
            'customer': row['CUSTOMERNAME'],
            'product': row['PRODUCTLINE'],
            'sales': float(row['SALES']),
            'country': row['COUNTRY'],
            'status': row['STATUS']
        })

    return {
        'kpi': {
            'total_sales': total_sales,
            'total_orders': total_orders,
            'avg_check': avg_check,
            'total_items': total_items
        },
        'monthly': monthly_data,
        'customers': customers_data,
        'products': products_data,
        'countries': countries_data,
        'transactions': transactions,
        'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }


dashboard_data = prepare_dashboard_data(df)


# --- 3. ГЕНЕРАЦИЯ HTML ---
def generate_html(data):
    """Генерирует HTML-дашборд с встроенными данными"""

    json_data = json.dumps(data, ensure_ascii=False, indent=2)

    html_template = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sales Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f0f4f8;
            padding: 20px;
            color: #1a1a2e;
        }
        .container { max-width: 1440px; margin: 0 auto; }

        .header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            padding: 25px 30px;
            border-radius: 16px;
            margin-bottom: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        .header h1 { font-size: 28px; font-weight: 700; }
        .header h1 span { color: #4fc3f7; }
        .header .subtitle { color: #aaa; font-size: 14px; }
        .header .date { background: rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 8px; font-size: 14px; }

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 25px;
        }
        .kpi-card {
            background: #fff;
            border-radius: 12px;
            padding: 20px 24px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            border-left: 4px solid #4a6cf7;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .kpi-card .label { font-size: 13px; color: #888; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
        .kpi-card .value { font-size: 32px; font-weight: 700; color: #1a1a2e; margin-top: 4px; }
        .kpi-card .value.green { color: #2ecc71; }
        .kpi-card .value.blue { color: #4a6cf7; }
        .kpi-card .value.orange { color: #f39c12; }
        .kpi-card .value.purple { color: #9b59b6; }
        .kpi-card:nth-child(1) { border-left-color: #2ecc71; }
        .kpi-card:nth-child(2) { border-left-color: #4a6cf7; }
        .kpi-card:nth-child(3) { border-left-color: #f39c12; }
        .kpi-card:nth-child(4) { border-left-color: #9b59b6; }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }
        .chart-card {
            background: #fff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        }
        .chart-card h3 {
            font-size: 16px;
            font-weight: 600;
            color: #1a1a2e;
            margin-bottom: 12px;
            border-bottom: 2px solid #f0f4f8;
            padding-bottom: 10px;
        }
        .chart-card .chart-container { position: relative; height: 280px; }

        .table-section {
            background: #fff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            margin-bottom: 25px;
        }
        .table-section h3 {
            font-size: 16px;
            font-weight: 600;
            color: #1a1a2e;
            margin-bottom: 12px;
            border-bottom: 2px solid #f0f4f8;
            padding-bottom: 10px;
        }

        .table-wrapper { overflow-x: auto; max-height: 400px; overflow-y: auto; }
        .table-wrapper::-webkit-scrollbar { width: 6px; height: 6px; }
        .table-wrapper::-webkit-scrollbar-thumb { background: #ccc; border-radius: 10px; }

        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        table thead { position: sticky; top: 0; z-index: 10; }
        table th {
            background: #f0f4f8; color: #1a1a2e; font-weight: 600;
            padding: 10px 12px; text-align: left; border-bottom: 2px solid #ddd;
            white-space: nowrap;
        }
        table td { padding: 8px 12px; border-bottom: 1px solid #eee; }
        table tr:hover { background: #f8f9fc; }

        .status-badge {
            display: inline-block; padding: 2px 12px; border-radius: 12px;
            font-size: 12px; font-weight: 500;
        }
        .status-badge.shipped { background: #d1fae5; color: #065f46; }
        .status-badge.disputed { background: #fce4ec; color: #b71c1c; }
        .status-badge.cancelled { background: #fef3c7; color: #92400e; }
        .status-badge.in-process { background: #dbeafe; color: #1e40af; }
        .status-badge.default { background: #e5e7eb; color: #374151; }

        .footer {
            text-align: center;
            color: #999;
            font-size: 13px;
            padding: 20px 0 10px;
            border-top: 1px solid #e0e0e0;
            margin-top: 10px;
        }

        @media (max-width: 768px) {
            .header { flex-direction: column; text-align: center; }
            .kpi-grid { grid-template-columns: repeat(2, 1fr); }
            .charts-grid { grid-template-columns: 1fr; }
            .kpi-card .value { font-size: 24px; }
            body { padding: 12px; }
        }
        @media (max-width: 480px) {
            .kpi-grid { grid-template-columns: 1fr; }
            .header h1 { font-size: 20px; }
        }
    </style>
</head>
<body>
<div class="container">

    <div class="header">
        <div>
            <h1>🚀 Аналитический <span>дашборд продаж</span></h1>
            <div class="subtitle">Sales Dashboard</div>
        </div>
        <div class="date">📅 Обновлено: <span id="generatedAt">DATA_PLACEHOLDER_DATE</span></div>
    </div>

    <div class="kpi-grid" id="kpiGrid"></div>

    <div class="charts-grid">
        <div class="chart-card">
            <h3>📈 Динамика выручки по месяцам</h3>
            <div class="chart-container"><canvas id="monthlyChart"></canvas></div>
        </div>
        <div class="chart-card">
            <h3>🏆 Топ-5 клиентов по выручке</h3>
            <div class="chart-container"><canvas id="customersChart"></canvas></div>
        </div>
        <div class="chart-card">
            <h3>📊 Продажи по категориям</h3>
            <div class="chart-container"><canvas id="productsChart"></canvas></div>
        </div>
        <div class="chart-card">
            <h3>🌍 Выручка по странам</h3>
            <div class="chart-container"><canvas id="countriesChart"></canvas></div>
        </div>
    </div>

    <div class="table-section">
        <h3>📋 Последние транзакции</h3>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Дата</th>
                        <th>Клиент</th>
                        <th>Категория</th>
                        <th>Сумма</th>
                        <th>Страна</th>
                        <th>Статус</th>
                    </tr>
                </thead>
                <tbody id="transactionsBody"></tbody>
            </table>
        </div>
    </div>

    <div class="footer">
        ⚡ Создано с использованием Python (pandas) и Chart.js
    </div>
</div>

<script>
    // ВСТРОЕННЫЕ ДАННЫЕ
    const DATA = DATA_PLACEHOLDER;

    function renderKPI() {
        const kpi = DATA.kpi;
        document.getElementById('kpiGrid').innerHTML = `
            <div class="kpi-card">
                <div class="label">💰 Общая выручка</div>
                <div class="value green">$${kpi.total_sales.toLocaleString()}</div>
            </div>
            <div class="kpi-card">
                <div class="label">📦 Количество заказов</div>
                <div class="value blue">${kpi.total_orders.toLocaleString()}</div>
            </div>
            <div class="kpi-card">
                <div class="label">🧾 Средний чек</div>
                <div class="value orange">$${kpi.avg_check.toLocaleString()}</div>
            </div>
            <div class="kpi-card">
                <div class="label">📈 Продано единиц</div>
                <div class="value purple">${kpi.total_items.toLocaleString()}</div>
            </div>
        `;
        document.getElementById('generatedAt').textContent = DATA.generated_at || '—';
    }

    function renderCharts() {
        const colors = ['#4a6cf7', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c', '#e67e22', '#3498db', '#e84393'];

        // 1. Динамика продаж
        const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
        new Chart(monthlyCtx, {
            type: 'line',
            data: {
                labels: DATA.monthly.months,
                datasets: [{
                    label: 'Выручка ($)',
                    data: DATA.monthly.sales,
                    borderColor: '#4CAF50',
                    backgroundColor: 'rgba(76, 175, 80, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#4CAF50'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, grid: { color: '#f0f0f0' } } }
            }
        });

        // 2. Топ-5 клиентов
        const customersCtx = document.getElementById('customersChart').getContext('2d');
        new Chart(customersCtx, {
            type: 'bar',
            data: {
                labels: DATA.customers.names.map(n => n.length > 20 ? n.substring(0, 20) + '...' : n),
                datasets: [{
                    label: 'Выручка ($)',
                    data: DATA.customers.sales,
                    backgroundColor: ['#4a6cf7', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6'],
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { x: { beginAtZero: true, grid: { color: '#f0f0f0' } } }
            }
        });

        // 3. Категории продуктов
        const productsCtx = document.getElementById('productsChart').getContext('2d');
        new Chart(productsCtx, {
            type: 'doughnut',
            data: {
                labels: DATA.products.categories,
                datasets: [{
                    data: DATA.products.sales,
                    backgroundColor: ['#4a6cf7', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c', '#e67e22', '#3498db'],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'right', labels: { boxWidth: 12, font: { size: 11 } } },
                    tooltip: {
                        callbacks: {
                            label: function(ctx) {
                                const total = ctx.dataset.data.reduce((a,b) => a+b, 0);
                                const pct = total > 0 ? (ctx.parsed / total * 100).toFixed(1) : 0;
                                return `${ctx.label}: $${ctx.parsed.toLocaleString()} (${pct}%)`;
                            }
                        }
                    }
                }
            }
        });

        // 4. Страны
        const countriesCtx = document.getElementById('countriesChart').getContext('2d');
        new Chart(countriesCtx, {
            type: 'bar',
            data: {
                labels: DATA.countries.countries,
                datasets: [{
                    label: 'Выручка ($)',
                    data: DATA.countries.sales,
                    backgroundColor: '#e74c3c',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, grid: { color: '#f0f0f0' } } }
            }
        });
    }

    function getStatusClass(status) {
        const s = status.toLowerCase();
        if (s.includes('shipped')) return 'shipped';
        if (s.includes('disputed')) return 'disputed';
        if (s.includes('cancelled')) return 'cancelled';
        if (s.includes('process')) return 'in-process';
        return 'default';
    }

    function renderTransactions() {
        const tbody = document.getElementById('transactionsBody');
        tbody.innerHTML = DATA.transactions.map(t => `
            <tr>
                <td>${t.date}</td>
                <td>${t.customer}</td>
                <td>${t.product}</td>
                <td>$${t.sales.toLocaleString()}</td>
                <td>${t.country}</td>
                <td><span class="status-badge ${getStatusClass(t.status)}">${t.status}</span></td>
            </tr>
        `).join('');
    }

    function renderAll() {
        if (!DATA) return;
        renderKPI();
        renderCharts();
        renderTransactions();
    }

    renderAll();
</script>
</body>
</html>'''

    # Заменяем плейсхолдеры
    html = html_template.replace('DATA_PLACEHOLDER', json_data)
    html = html.replace('DATA_PLACEHOLDER_DATE', data['generated_at'])

    return html


# --- 4. СОХРАНЕНИЕ HTML ---
html_output = generate_html(dashboard_data)

with open('sales_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_output)

print("✅ Дашборд создан: sales_dashboard.html")
print(f"   - Выручка: ${dashboard_data['kpi']['total_sales']:,.0f}")
print(f"   - Заказов: {dashboard_data['kpi']['total_orders']:,}")
print(f"   - Транзакций: {len(dashboard_data['transactions'])}")
