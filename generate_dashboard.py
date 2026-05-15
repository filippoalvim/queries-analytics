import openpyxl
import json
import urllib.request

print("Baixando Chart.js inline...")
chartjs_url = "https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"
annotation_url = "https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3.0.1/dist/chartjs-plugin-annotation.min.js"

with urllib.request.urlopen(chartjs_url) as r:
    chartjs_code = r.read().decode("utf-8")
with urllib.request.urlopen(annotation_url) as r:
    annotation_code = r.read().decode("utf-8")

print(f"Chart.js: {len(chartjs_code):,} chars | Annotation: {len(annotation_code):,} chars")

wb = openpyxl.load_workbook(r'C:\Cupolillo\churn-project\queries-analytics\portfolio_distribuicao_dias_sem_envio_sintetico.xlsx')
ws = wb.active
rows = list(ws.iter_rows(values_only=True))

data = []
for row in rows[1:]:
    if row[0] is not None:
        data.append({
            "dia": row[0],
            "qtd": row[1] if row[1] is not None else 0,
            "acumulado": row[2] if row[2] is not None else 0,
            "pct_acumulado": row[3] if row[3] is not None else 0,
            "pct_diff": row[5] if row[5] is not None else 0,
        })

total_usuarios = data[-1]["acumulado"] if data else 0
data_json = json.dumps(data)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Churn Analysis — Receipt Submission Interval | VR</title>
  <script>{chartjs_code}</script>
  <script>{annotation_code}</script>
  <style>
    :root {{
      --bg: #0f1117;
      --surface: #1a1d27;
      --surface2: #22263a;
      --border: #2e3347;
      --accent: #6366f1;
      --accent2: #22d3ee;
      --accent3: #f59e0b;
      --green: #22c55e;
      --red: #ef4444;
      --text: #e2e8f0;
      --muted: #94a3b8;
      --pareto: #f59e0b;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Segoe UI', system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      padding: 24px 20px 48px;
    }}
    .header {{
      text-align: center;
      margin-bottom: 36px;
    }}
    .header h1 {{
      font-size: 1.75rem;
      font-weight: 700;
      letter-spacing: -0.5px;
    }}
    .header h1 span {{ color: var(--accent); }}
    .header p {{
      color: var(--muted);
      margin-top: 8px;
      font-size: 0.95rem;
      max-width: 620px;
      margin-left: auto;
      margin-right: auto;
      line-height: 1.6;
    }}
    .badge {{
      display: inline-block;
      background: var(--surface2);
      border: 1px solid var(--border);
      color: var(--muted);
      font-size: 0.75rem;
      padding: 3px 10px;
      border-radius: 999px;
      margin-top: 10px;
    }}
    .controls {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 20px 24px;
      margin-bottom: 24px;
      max-width: 960px;
      margin-left: auto;
      margin-right: auto;
    }}
    .controls label {{
      font-size: 0.85rem;
      color: var(--muted);
      display: block;
      margin-bottom: 10px;
    }}
    .controls label strong {{ color: var(--text); font-size: 0.95rem; }}
    .slider-row {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .slider-row input[type=range] {{
      flex: 1;
      -webkit-appearance: none;
      height: 6px;
      border-radius: 4px;
      background: var(--border);
      outline: none;
      cursor: pointer;
    }}
    .slider-row input[type=range]::-webkit-slider-thumb {{
      -webkit-appearance: none;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: var(--accent);
      cursor: pointer;
      box-shadow: 0 0 6px rgba(99,102,241,0.6);
    }}
    .slider-val {{
      min-width: 44px;
      text-align: right;
      font-size: 0.9rem;
      color: var(--accent);
      font-weight: 600;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      max-width: 960px;
      margin: 0 auto 24px;
    }}
    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 18px 20px;
      position: relative;
      overflow: hidden;
    }}
    .card::before {{
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0;
      height: 3px;
      background: var(--accent);
      border-radius: 3px 3px 0 0;
    }}
    .card.green::before {{ background: var(--green); }}
    .card.cyan::before {{ background: var(--accent2); }}
    .card.amber::before {{ background: var(--pareto); }}
    .card.red::before {{ background: var(--red); }}
    .card-label {{
      font-size: 0.75rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 8px;
    }}
    .card-value {{
      font-size: 1.7rem;
      font-weight: 700;
      line-height: 1.1;
    }}
    .card-value.accent {{ color: var(--accent); }}
    .card-value.green {{ color: var(--green); }}
    .card-value.cyan {{ color: var(--accent2); }}
    .card-value.amber {{ color: var(--pareto); }}
    .card-sub {{
      font-size: 0.75rem;
      color: var(--muted);
      margin-top: 6px;
    }}
    .chart-wrap {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 24px;
      max-width: 960px;
      margin: 0 auto 24px;
    }}
    .chart-title {{
      font-size: 0.9rem;
      color: var(--muted);
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .chart-title strong {{ color: var(--text); font-size: 1rem; }}
    .legend-row {{
      display: flex;
      gap: 18px;
      flex-wrap: wrap;
      margin-bottom: 16px;
    }}
    .leg-item {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.8rem;
      color: var(--muted);
    }}
    .leg-dot {{
      width: 10px;
      height: 10px;
      border-radius: 2px;
    }}
    .pareto-note {{
      background: rgba(245,158,11,0.08);
      border: 1px solid rgba(245,158,11,0.25);
      border-radius: 10px;
      padding: 12px 16px;
      max-width: 960px;
      margin: 0 auto 0;
      font-size: 0.83rem;
      color: var(--muted);
      line-height: 1.6;
      display: flex;
      gap: 10px;
      align-items: flex-start;
    }}
    .pareto-note .icon {{ font-size: 1.1rem; margin-top: 1px; }}
    .pareto-note strong {{ color: var(--pareto); }}
    canvas {{ max-height: 380px; }}
    @media (max-width: 600px) {{
      .cards {{ grid-template-columns: 1fr 1fr; }}
      .header h1 {{ font-size: 1.35rem; }}
    }}
  </style>
</head>
<body>

<div class="header">
  <h1>Receipt <span>Submission Interval</span> Distribution</h1>
  <p>Behavioral churn analysis for VR's receipt scanning product, based on the median gap between consecutive submissions per user.</p>
  <span class="badge">97,378 users analyzed · Synthetic data for portfolio</span>
</div>

<div class="controls" style="max-width:960px">
  <label>
    Filter day interval (X axis):<br/>
    <span style="font-size:0.78rem;color:var(--muted)">Drag to explore the distribution across different time windows</span>
  </label>
  <div class="slider-row">
    <span style="font-size:0.8rem;color:var(--muted)">0</span>
    <input type="range" id="sliderMax" min="1" max="90" value="30" step="1" oninput="onSlider(this.value)"/>
    <span class="slider-val" id="sliderDisplay">30 days</span>
  </div>
</div>

<div class="cards">
  <div class="card cyan">
    <div class="card-label">Selected Day</div>
    <div class="card-value cyan" id="cardDia">—</div>
    <div class="card-sub">Reference point on the X axis</div>
  </div>
  <div class="card">
    <div class="card-label">Users on Day</div>
    <div class="card-value accent" id="cardQtd">—</div>
    <div class="card-sub">Median interval = X days</div>
  </div>
  <div class="card green">
    <div class="card-label">Cumulative Users</div>
    <div class="card-value green" id="cardAcum">—</div>
    <div class="card-sub" id="cardAcumSub">up to selected day</div>
  </div>
  <div class="card amber">
    <div class="card-label">Cumulative %</div>
    <div class="card-value amber" id="cardPct">—</div>
    <div class="card-sub" id="cardPctSub">of total user base</div>
  </div>
</div>

<div class="chart-wrap">
  <div class="chart-title"><strong>Cumulative Distribution Curve</strong> · Median Days Between Receipt Submissions</div>
  <div class="legend-row">
    <div class="leg-item"><div class="leg-dot" style="background:#6366f1"></div>Cumulative % of Users (line)</div>
    <div class="leg-item"><div class="leg-dot" style="background:rgba(34,211,238,0.5)"></div>Users on Day (bars)</div>
    <div class="leg-item"><div class="leg-dot" style="background:#f59e0b;border-radius:50%"></div>Pareto Line (80%)</div>
  </div>
  <canvas id="chartMain"></canvas>
</div>

<div class="pareto-note">
  <span class="icon">📐</span>
  <span>
    <strong>Pareto principle applied:</strong> 80% of users have a median submission interval of <strong>up to 15 days</strong>.
    The chart forms a <strong>logarithmic curve</strong>: the incremental gain of users per additional day of interval decreases progressively,
    revealing a user base concentrated in highly frequent submitters.
    <strong>40% of users</strong> have a median interval of up to 1 day — meaning they submit receipts practically every day.
  </span>
</div>

<script>
const RAW_DATA = {data_json};

const totalUsuarios = {total_usuarios};

function getDataUpTo(maxDia) {{
  return RAW_DATA.filter(d => d.dia <= maxDia);
}}

function fmt(n) {{
  if (n === null || n === undefined) return '—';
  return n.toLocaleString('en-US');
}}

let chart;

function buildChart(maxDia) {{
  const slice = getDataUpTo(maxDia);
  const labels = slice.map(d => d.dia);
  const qtds = slice.map(d => d.qtd);
  const pcts = slice.map(d => d.pct_acumulado);

  const paretoY = 80;
  const ctx = document.getElementById('chartMain').getContext('2d');

  if (chart) chart.destroy();

  chart = new Chart(ctx, {{
    type: 'bar',
    data: {{
      labels,
      datasets: [
        {{
          type: 'line',
          label: 'Cumulative %',
          data: pcts,
          borderColor: '#6366f1',
          backgroundColor: 'rgba(99,102,241,0.08)',
          borderWidth: 2.5,
          pointRadius: 0,
          pointHoverRadius: 5,
          pointHoverBackgroundColor: '#6366f1',
          fill: true,
          tension: 0.3,
          yAxisID: 'yPct',
          order: 1,
        }},
        {{
          type: 'bar',
          label: 'Users on Day',
          data: qtds,
          backgroundColor: 'rgba(34,211,238,0.3)',
          borderColor: 'rgba(34,211,238,0.6)',
          borderWidth: 1,
          borderRadius: 2,
          yAxisID: 'yQtd',
          order: 2,
        }}
      ]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: true,
      interaction: {{
        mode: 'index',
        intersect: false,
      }},
      onHover: (evt, elements) => {{
        if (elements.length > 0) {{
          const idx = elements[0].index;
          const d = getDataUpTo(maxDia)[idx];
          if (d) updateCards(d);
        }}
      }},
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          backgroundColor: '#1a1d27',
          borderColor: '#2e3347',
          borderWidth: 1,
          titleColor: '#e2e8f0',
          bodyColor: '#94a3b8',
          padding: 12,
          callbacks: {{
            title: (items) => `Day ${{items[0].label}}`,
            label: (item) => {{
              if (item.dataset.label === 'Cumulative %')
                return ` ${{item.raw}}% cumulative`;
              return ` ${{item.raw.toLocaleString('en-US')}} users`;
            }}
          }}
        }},
        annotation: {{
          annotations: {{
            pareto: {{
              type: 'line',
              yScaleID: 'yPct',
              yMin: paretoY,
              yMax: paretoY,
              borderColor: '#f59e0b',
              borderWidth: 1.5,
              borderDash: [6, 4],
              label: {{
                display: true,
                content: '80% — Pareto',
                color: '#f59e0b',
                backgroundColor: 'rgba(245,158,11,0.12)',
                font: {{ size: 11, weight: '600' }},
                position: 'end',
                yAdjust: -10,
              }}
            }}
          }}
        }}
      }},
      scales: {{
        x: {{
          grid: {{ color: 'rgba(255,255,255,0.04)' }},
          ticks: {{
            color: '#64748b',
            maxTicksLimit: 16,
            font: {{ size: 11 }},
            callback: (val, idx) => labels[idx]
          }},
          title: {{
            display: true,
            text: 'Median Days Between Receipt Submissions',
            color: '#64748b',
            font: {{ size: 11 }}
          }}
        }},
        yPct: {{
          position: 'left',
          min: 0, max: 100,
          grid: {{ color: 'rgba(255,255,255,0.05)' }},
          ticks: {{
            color: '#6366f1',
            font: {{ size: 11 }},
            callback: v => v + '%'
          }},
          title: {{
            display: true,
            text: 'Cumulative % of Users',
            color: '#6366f1',
            font: {{ size: 11 }}
          }}
        }},
        yQtd: {{
          position: 'right',
          grid: {{ display: false }},
          ticks: {{
            color: 'rgba(34,211,238,0.7)',
            font: {{ size: 11 }},
            callback: v => v >= 1000 ? (v/1000).toFixed(0)+'k' : v
          }},
          title: {{
            display: true,
            text: 'Users on Day',
            color: 'rgba(34,211,238,0.7)',
            font: {{ size: 11 }}
          }}
        }}
      }}
    }}
  }});
}}

function updateCards(d) {{
  document.getElementById('cardDia').textContent = d.dia + (d.dia === 1 ? ' day' : ' days');
  document.getElementById('cardQtd').textContent = fmt(d.qtd);
  document.getElementById('cardAcum').textContent = fmt(d.acumulado);
  document.getElementById('cardAcumSub').textContent = `up to day ${{d.dia}}`;
  document.getElementById('cardPct').textContent = d.pct_acumulado + '%';
  document.getElementById('cardPctSub').textContent = d.pct_acumulado >= 80
    ? '✅ Above Pareto threshold (80%)'
    : `${{(80 - d.pct_acumulado).toFixed(2)}}pp below Pareto`;
}}

function onSlider(val) {{
  document.getElementById('sliderDisplay').textContent = val + ' days';
  buildChart(parseInt(val));
  const slice = getDataUpTo(parseInt(val));
  if (slice.length) updateCards(slice[slice.length - 1]);
}}

buildChart(30);
const initial = getDataUpTo(30);
if (initial.length) updateCards(initial[initial.length - 1]);
</script>
</body>
</html>"""

with open(r'C:\Cupolillo\churn-project\queries-analytics\assets\churn-dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Dashboard gerado com sucesso!")
print(f"Total de linhas de dados: {len(data)}")
print(f"Total de usuários: {total_usuarios:,}")
