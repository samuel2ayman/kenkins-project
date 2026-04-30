"""
E-Commerce Sales Analyzer
==========================
Generates synthetic sales data, runs analysis, and produces
a self-contained HTML report with embedded charts.

Usage:
    python analyzer.py                  # generates data + report
    python analyzer.py --csv sales.csv  # use your own CSV file
"""

import argparse
import base64
import io
import random
import sys
from datetime import datetime, timedelta

# ── dependency check ──────────────────────────────────────────────────────────
try:
    import pandas as pd
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    from matplotlib.gridspec import GridSpec
except ImportError:
    print("Missing dependencies. Run:  pip install pandas matplotlib")
    sys.exit(1)

# ── palette ───────────────────────────────────────────────────────────────────
COLORS = ["#4f46e5", "#06b6d4", "#10b981", "#f59e0b", "#ef4444",
          "#8b5cf6", "#ec4899", "#14b8a6"]

# ─────────────────────────────────────────────────────────────────────────────
# 1.  DATA GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def generate_data(n_rows: int = 2000, seed: int = 42) -> pd.DataFrame:
    """Return a DataFrame of synthetic e-commerce orders."""
    random.seed(seed)
    rng = pd.to_datetime("2024-01-01")

    products = {
        "Wireless Headphones":  ("Electronics",  89.99),
        "Running Shoes":        ("Footwear",      74.99),
        "Coffee Maker":         ("Appliances",    49.99),
        "Yoga Mat":             ("Sports",        29.99),
        "Bluetooth Speaker":    ("Electronics",   59.99),
        "Leather Wallet":       ("Accessories",   34.99),
        "Desk Lamp":            ("Home",          24.99),
        "Protein Powder":       ("Health",        44.99),
        "Sunglasses":           ("Accessories",   54.99),
        "Air Fryer":            ("Appliances",    79.99),
    }
    regions    = ["North", "South", "East", "West", "Central"]
    channels   = ["Online", "Mobile App", "In-Store"]
    weights    = [0.45, 0.35, 0.20]

    rows = []
    for i in range(n_rows):
        product = random.choice(list(products))
        category, base_price = products[product]
        qty      = random.choices([1, 2, 3, 4, 5], weights=[50, 25, 12, 8, 5])[0]
        discount = random.choices([0, 0.05, 0.10, 0.15, 0.20],
                                  weights=[50, 20, 15, 10, 5])[0]
        price    = round(base_price * (1 - discount), 2)
        revenue  = round(price * qty, 2)
        date     = rng + timedelta(days=random.randint(0, 364))

        rows.append({
            "order_id":   f"ORD-{10000 + i}",
            "date":       date,
            "product":    product,
            "category":   category,
            "quantity":   qty,
            "unit_price": price,
            "discount":   discount,
            "revenue":    revenue,
            "region":     random.choice(regions),
            "channel":    random.choices(channels, weights=weights)[0],
            "returned":   random.random() < 0.05,
        })

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 2.  ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def analyse(df: pd.DataFrame) -> dict:
    net = df[~df["returned"]]

    monthly   = (net.groupby("month")["revenue"].sum()
                    .reset_index()
                    .rename(columns={"revenue": "total"}))
    monthly["month_str"] = monthly["month"].astype(str)

    top_products = (net.groupby("product")["revenue"].sum()
                       .sort_values(ascending=False)
                       .head(8))

    by_category  = net.groupby("category")["revenue"].sum().sort_values(ascending=False)
    by_region    = net.groupby("region")["revenue"].sum().sort_values(ascending=False)
    by_channel   = net.groupby("channel")["revenue"].sum().sort_values(ascending=False)

    peak_month = monthly.loc[monthly["total"].idxmax(), "month_str"]
    avg_order  = round(net["revenue"].mean(), 2)
    return_rate = round(df["returned"].mean() * 100, 1)
    total_rev  = round(net["revenue"].sum(), 2)
    total_orders = len(df)

    return dict(
        df=df, net=net,
        monthly=monthly,
        top_products=top_products,
        by_category=by_category,
        by_region=by_region,
        by_channel=by_channel,
        kpis=dict(
            total_revenue=total_rev,
            total_orders=total_orders,
            avg_order=avg_order,
            return_rate=return_rate,
            peak_month=peak_month,
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3.  CHARTS  (each returns a base64 PNG string)
# ─────────────────────────────────────────────────────────────────────────────

def _fig_to_b64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()


def chart_revenue_trend(data: dict) -> str:
    m = data["monthly"]
    fig, ax = plt.subplots(figsize=(10, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")

    ax.fill_between(m["month_str"], m["total"], alpha=0.18, color=COLORS[0])
    ax.plot(m["month_str"], m["total"], color=COLORS[0], linewidth=2.5, marker="o",
            markersize=5)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.tick_params(colors="white", labelsize=9)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="y", color="white", alpha=0.08)
    ax.set_title("Monthly Net Revenue", color="white", fontsize=13, pad=10)
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    return _fig_to_b64(fig)


def chart_top_products(data: dict) -> str:
    tp = data["top_products"]
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")

    bars = ax.barh(tp.index[::-1], tp.values[::-1],
                   color=COLORS[:len(tp)], edgecolor="none", height=0.6)
    for bar, val in zip(bars, tp.values[::-1]):
        ax.text(val + 200, bar.get_y() + bar.get_height() / 2,
                f"${val:,.0f}", va="center", color="white", fontsize=8.5)

    ax.set_xlabel("Revenue ($)", color="#94a3b8", fontsize=9)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.tick_params(colors="white", labelsize=9)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="x", color="white", alpha=0.08)
    ax.set_title("Top Products by Revenue", color="white", fontsize=13, pad=10)
    fig.tight_layout()
    return _fig_to_b64(fig)


def chart_breakdown(data: dict) -> str:
    fig = plt.figure(figsize=(11, 4.2), facecolor="#0f172a")
    gs  = GridSpec(1, 2, figure=fig, wspace=0.38)

    # --- by category (donut) ---
    ax1 = fig.add_subplot(gs[0])
    ax1.set_facecolor("#0f172a")
    cat = data["by_category"]
    wedges, texts, autotexts = ax1.pie(
        cat.values, labels=cat.index,
        colors=COLORS[:len(cat)],
        autopct="%1.1f%%", startangle=140,
        wedgeprops=dict(width=0.55, edgecolor="#0f172a"),
        pctdistance=0.78,
    )
    for t in texts:
        t.set_color("white"); t.set_fontsize(8.5)
    for at in autotexts:
        at.set_color("white"); at.set_fontsize(7.5)
    ax1.set_title("Revenue by Category", color="white", fontsize=12, pad=12)

    # --- by channel (bar) ---
    ax2 = fig.add_subplot(gs[1])
    ax2.set_facecolor("#0f172a")
    ch  = data["by_channel"]
    ax2.bar(ch.index, ch.values, color=COLORS[1:1+len(ch)],
            edgecolor="none", width=0.5)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax2.tick_params(colors="white", labelsize=9)
    for spine in ax2.spines.values():
        spine.set_visible(False)
    ax2.grid(axis="y", color="white", alpha=0.08)
    ax2.set_title("Revenue by Channel", color="white", fontsize=12, pad=12)

    fig.tight_layout()
    return _fig_to_b64(fig)


def chart_region(data: dict) -> str:
    reg = data["by_region"]
    fig, ax = plt.subplots(figsize=(7, 3.5), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")

    bars = ax.bar(reg.index, reg.values, color=COLORS[3:3+len(reg)],
                  edgecolor="none", width=0.55)
    for bar, val in zip(bars, reg.values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 200,
                f"${val:,.0f}", ha="center", color="white", fontsize=8)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.tick_params(colors="white", labelsize=9)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="y", color="white", alpha=0.08)
    ax.set_title("Revenue by Region", color="white", fontsize=13, pad=10)
    fig.tight_layout()
    return _fig_to_b64(fig)


# ─────────────────────────────────────────────────────────────────────────────
# 4.  HTML REPORT
# ─────────────────────────────────────────────────────────────────────────────

def build_html(data: dict, charts: dict) -> str:
    k = data["kpis"]

    kpi_html = "".join(f"""
        <div class="kpi">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{value}</div>
        </div>""" for label, value in [
        ("Total Revenue",    f"${k['total_revenue']:,.2f}"),
        ("Total Orders",     f"{k['total_orders']:,}"),
        ("Avg Order Value",  f"${k['avg_order']:,.2f}"),
        ("Return Rate",      f"{k['return_rate']}%"),
        ("Peak Month",       k["peak_month"]),
    ])

    now = datetime.now().strftime("%B %d, %Y  %H:%M")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>E-Commerce Sales Report</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body     {{ font-family: 'Segoe UI', system-ui, sans-serif;
              background: #020617; color: #e2e8f0; min-height: 100vh; }}
  header   {{ background: linear-gradient(135deg,#1e1b4b 0%,#0f172a 100%);
              padding: 2.5rem 3rem; border-bottom: 1px solid #1e293b; }}
  header h1 {{ font-size: 1.9rem; font-weight: 700; color: #a5b4fc; letter-spacing:-.5px; }}
  header p  {{ color: #64748b; font-size: .85rem; margin-top: .35rem; }}
  main     {{ max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem; }}
  .kpi-row {{ display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 2rem; }}
  .kpi     {{ flex: 1 1 160px; background: #0f172a; border: 1px solid #1e293b;
              border-radius: 12px; padding: 1.25rem 1.5rem; }}
  .kpi-label {{ font-size: .75rem; text-transform: uppercase; letter-spacing: .08em;
                color: #64748b; margin-bottom: .4rem; }}
  .kpi-value {{ font-size: 1.65rem; font-weight: 700; color: #a5b4fc; }}
  .card    {{ background: #0f172a; border: 1px solid #1e293b; border-radius: 14px;
              padding: 1.5rem; margin-bottom: 1.5rem; }}
  .card img {{ width: 100%; border-radius: 8px; }}
  .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}
  @media(max-width:640px) {{ .two-col {{ grid-template-columns:1fr; }} }}
  footer   {{ text-align:center; padding: 2rem; color: #334155; font-size:.8rem; }}
</style>
</head>
<body>
<header>
  <h1>📦 E-Commerce Sales Report</h1>
  <p>Generated on {now} &nbsp;·&nbsp; {k['total_orders']:,} orders analysed</p>
</header>
<main>
  <div class="kpi-row">{kpi_html}</div>

  <div class="card">
    <img src="data:image/png;base64,{charts['trend']}" alt="Revenue trend">
  </div>

  <div class="two-col">
    <div class="card">
      <img src="data:image/png;base64,{charts['products']}" alt="Top products">
    </div>
    <div class="card">
      <img src="data:image/png;base64,{charts['region']}" alt="By region">
    </div>
  </div>

  <div class="card">
    <img src="data:image/png;base64,{charts['breakdown']}" alt="Category & channel">
  </div>
</main>
<footer>E-Commerce Sales Analyzer · {now}</footer>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# 5.  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="E-Commerce Sales Analyzer")
    parser.add_argument("--csv",  help="Path to a CSV file (optional)")
    parser.add_argument("--rows", type=int, default=2000,
                        help="Rows to generate when no CSV is provided (default 2000)")
    parser.add_argument("--out",  default="report.html",
                        help="Output HTML filename (default: report.html)")
    args = parser.parse_args()

    # ── load or generate data ─────────────────────────────────────────────────
    if args.csv:
        print(f"📂  Loading data from {args.csv} ...")
        df = pd.read_csv(args.csv, parse_dates=["date"])
        required = {"date", "product", "category", "quantity",
                    "unit_price", "revenue", "region", "channel", "returned"}
        missing = required - set(df.columns)
        if missing:
            print(f"❌  CSV is missing columns: {missing}")
            sys.exit(1)
        df["month"] = df["date"].dt.to_period("M")
    else:
        print(f"🔧  Generating {args.rows:,} synthetic orders ...")
        df = generate_data(n_rows=args.rows)

    # ── analyse ───────────────────────────────────────────────────────────────
    print("📊  Running analysis ...")
    data = analyse(df)
    k    = data["kpis"]

    print(f"\n{'─'*40}")
    print(f"  Total Revenue  :  ${k['total_revenue']:>12,.2f}")
    print(f"  Total Orders   :  {k['total_orders']:>12,}")
    print(f"  Avg Order      :  ${k['avg_order']:>12,.2f}")
    print(f"  Return Rate    :  {k['return_rate']:>11}%")
    print(f"  Peak Month     :  {k['peak_month']:>12}")
    print(f"{'─'*40}\n")

    # ── charts ────────────────────────────────────────────────────────────────
    print("🎨  Rendering charts ...")
    charts = {
        "trend":     chart_revenue_trend(data),
        "products":  chart_top_products(data),
        "breakdown": chart_breakdown(data),
        "region":    chart_region(data),
    }

    # ── write report ──────────────────────────────────────────────────────────
    html = build_html(data, charts)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅  Report saved →  {args.out}")
    print("    Open it in any browser — no internet required.\n")


if __name__ == "__main__":
    main()
