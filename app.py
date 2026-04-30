import random
from datetime import datetime, timedelta

random.seed(42)

PRODUCTS = {
    "Wireless Headphones": ("Electronics",  89.99),
    "Running Shoes":       ("Footwear",      74.99),
    "Coffee Maker":        ("Appliances",    49.99),
    "Yoga Mat":            ("Sports",        29.99),
    "Bluetooth Speaker":   ("Electronics",   59.99),
    "Leather Wallet":      ("Accessories",   34.99),
    "Desk Lamp":           ("Home",          24.99),
    "Protein Powder":      ("Health",        44.99),
    "Sunglasses":          ("Accessories",   54.99),
    "Air Fryer":           ("Appliances",    79.99),
}
REGIONS  = ["North", "South", "East", "West", "Central"]
CHANNELS = ["Online", "Mobile App", "In-Store"]

def generate_data(n=2000):
    start = datetime(2024, 1, 1)
    rows = []
    for i in range(n):
        name = random.choice(list(PRODUCTS))
        cat, base = PRODUCTS[name]
        qty     = random.choices([1,2,3,4,5], weights=[50,25,12,8,5])[0]
        disc    = random.choices([0,.05,.10,.15,.20], weights=[50,20,15,10,5])[0]
        price   = round(base * (1 - disc), 2)
        revenue = round(price * qty, 2)
        date    = start + timedelta(days=random.randint(0, 364))
        rows.append({
            "product": name, "category": cat, "qty": qty,
            "revenue": revenue, "region": random.choice(REGIONS),
            "channel": random.choices(CHANNELS, weights=[45,35,20])[0],
            "returned": random.random() < 0.05,
            "month": date.strftime("%Y-%m"),
        })
    return rows

def analyse(rows):
    net = [r for r in rows if not r["returned"]]
    total_revenue = round(sum(r["revenue"] for r in net), 2)
    total_orders  = len(rows)
    avg_order     = round(total_revenue / len(net), 2)
    return_rate   = round(sum(1 for r in rows if r["returned"]) / len(rows) * 100, 1)

    monthly = {}
    for r in net:
        monthly[r["month"]] = monthly.get(r["month"], 0) + r["revenue"]
    peak_month = max(monthly, key=monthly.get)

    by_product  = {}
    by_category = {}
    by_region   = {}
    by_channel  = {}
    for r in net:
        by_product[r["product"]]   = by_product.get(r["product"], 0)   + r["revenue"]
        by_category[r["category"]] = by_category.get(r["category"], 0) + r["revenue"]
        by_region[r["region"]]     = by_region.get(r["region"], 0)     + r["revenue"]
        by_channel[r["channel"]]   = by_channel.get(r["channel"], 0)   + r["revenue"]

    return {
        "total_revenue": total_revenue,
        "total_orders":  total_orders,
        "avg_order":     avg_order,
        "return_rate":   return_rate,
        "peak_month":    peak_month,
        "monthly":       dict(sorted(monthly.items())),
        "by_product":    dict(sorted(by_product.items(), key=lambda x: -x[1])[:8]),
        "by_category":   dict(sorted(by_category.items(), key=lambda x: -x[1])),
        "by_region":     dict(sorted(by_region.items(), key=lambda x: -x[1])),
        "by_channel":    dict(sorted(by_channel.items(), key=lambda x: -x[1])),
    }

def bar_chart(data, color="#4f46e5"):
    max_val = max(data.values())
    bars = ""
    for label, val in data.items():
        pct = round(val / max_val * 100)
        bars += f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
          <div style="width:130px;font-size:12px;color:#94a3b8;text-align:right;flex-shrink:0">{label}</div>
          <div style="flex:1;background:#1e293b;border-radius:4px;height:22px">
            <div style="width:{pct}%;background:{color};height:100%;border-radius:4px"></div>
          </div>
          <div style="width:80px;font-size:12px;color:#e2e8f0">${val:,.0f}</div>
        </div>"""
    return bars

def build_html(d):
    now = datetime.now().strftime("%B %d, %Y %H:%M")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>E-Commerce Sales Report</title>
<style>
  * {{ box-sizing:border-box; margin:0; padding:0 }}
  body {{ font-family:'Segoe UI',system-ui,sans-serif; background:#020617; color:#e2e8f0 }}
  header {{ background:linear-gradient(135deg,#1e1b4b,#0f172a); padding:2rem 3rem; border-bottom:1px solid #1e293b }}
  header h1 {{ font-size:1.8rem; font-weight:700; color:#a5b4fc }}
  header p {{ color:#64748b; font-size:.85rem; margin-top:.3rem }}
  main {{ max-width:1000px; margin:0 auto; padding:2rem 1.5rem }}
  .kpis {{ display:flex; gap:1rem; flex-wrap:wrap; margin-bottom:2rem }}
  .kpi {{ flex:1 1 150px; background:#0f172a; border:1px solid #1e293b; border-radius:12px; padding:1.2rem 1.5rem }}
  .kpi-label {{ font-size:.7rem; text-transform:uppercase; letter-spacing:.08em; color:#64748b; margin-bottom:.4rem }}
  .kpi-value {{ font-size:1.5rem; font-weight:700; color:#a5b4fc }}
  .card {{ background:#0f172a; border:1px solid #1e293b; border-radius:12px; padding:1.5rem; margin-bottom:1.5rem }}
  .card h2 {{ font-size:1rem; font-weight:600; color:#cbd5e1; margin-bottom:1.2rem }}
  .two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:1.5rem }}
  @media(max-width:640px) {{ .two-col {{ grid-template-columns:1fr }} }}
  footer {{ text-align:center; padding:2rem; color:#334155; font-size:.8rem }}
</style>
</head>
<body>
<header>
  <h1>E-Commerce Sales Report</h1>
  <p>Generated on {now} &nbsp;·&nbsp; {d['total_orders']:,} orders analysed</p>
</header>
<main>
  <div class="kpis">
    <div class="kpi"><div class="kpi-label">Total Revenue</div><div class="kpi-value">${d['total_revenue']:,.2f}</div></div>
    <div class="kpi"><div class="kpi-label">Total Orders</div><div class="kpi-value">{d['total_orders']:,}</div></div>
    <div class="kpi"><div class="kpi-label">Avg Order Value</div><div class="kpi-value">${d['avg_order']:,.2f}</div></div>
    <div class="kpi"><div class="kpi-label">Return Rate</div><div class="kpi-value">{d['return_rate']}%</div></div>
    <div class="kpi"><div class="kpi-label">Peak Month</div><div class="kpi-value">{d['peak_month']}</div></div>
  </div>
  <div class="card"><h2>Monthly Revenue</h2>{bar_chart(d['monthly'], '#4f46e5')}</div>
  <div class="two-col">
    <div class="card"><h2>Top Products</h2>{bar_chart(d['by_product'], '#06b6d4')}</div>
    <div class="card"><h2>Revenue by Region</h2>{bar_chart(d['by_region'], '#10b981')}</div>
  </div>
  <div class="two-col">
    <div class="card"><h2>Revenue by Category</h2>{bar_chart(d['by_category'], '#8b5cf6')}</div>
    <div class="card"><h2>Revenue by Channel</h2>{bar_chart(d['by_channel'], '#f59e0b')}</div>
  </div>
</main>
<footer>E-Commerce Sales Analyzer · {now}</footer>
</body>
</html>"""

def main():
    print("Analysis Report")
    print("=" * 40)
    rows = generate_data()
    d    = analyse(rows)
    print(f"  Total Revenue  :  ${d['total_revenue']:>12,.2f}")
    print(f"  Total Orders   :  {d['total_orders']:>12,}")
    print(f"  Avg Order      :  ${d['avg_order']:>12,.2f}")
    print(f"  Return Rate    :  {d['return_rate']:>11}%")
    print(f"  Peak Month     :  {d['peak_month']:>12}")
    print("=" * 40)
    with open("report.html", "w", encoding="utf-8") as f:
        f.write(build_html(d))
    print("Report saved: report.html")

if __name__ == "__main__":
    main()
