#!/usr/bin/env python3
"""
Generate monthly market report pages for OwnPalosVerdes.com
from Top Producer CRMLS export data.

Usage:
    python3 generate_reports.py

Reads .tp files from ~/GrowDirect/Angel/Top Producer - Residential*/
Outputs HTML to market/YYYY-MM/index.html
"""

import csv
import glob
import os
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────
TP_GLOB = os.path.expanduser("~/GrowDirect/Angel/Top Producer - Residential*/*.tp")
OUTPUT_DIR = Path(__file__).parent / "market"
SITE_URL = "https://ownpalosverdes.com"

CITY_NAMES = {
    "Rancho Palos Verdes": "RPV",
    "Palos Verdes Estates": "PVE",
    "Rolling Hills Estates": "RHE",
    "Rolling Hills": "RH",
    "Palos Verdes Peninsula": "PVP",
    "San Pedro": "San Pedro",
}

REDFIN_LINKS = {
    "RPV": "https://www.redfin.com/city/30573/CA/Rancho-Palos-Verdes/housing-market",
    "PVE": "https://www.redfin.com/city/30570/CA/Palos-Verdes-Estates/housing-market",
    "RHE": "https://www.redfin.com/city/30574/CA/Rolling-Hills-Estates/housing-market",
    "RH": "https://www.redfin.com/city/15808/CA/Rolling-Hills/housing-market",
}

REDFIN_CITY_SLUGS = {
    "RPV": "Rancho-Palos-Verdes",
    "PVE": "Palos-Verdes-Estates",
    "RHE": "Rolling-Hills-Estates",
    "RH": "Rolling-Hills",
    "PVP": "Palos-Verdes-Peninsula",
    "San Pedro": "San-Pedro",
}

COMPASS_LINKS = {
    "RPV": "https://www.compass.com/homes-for-sale/rancho-palos-verdes-ca/",
    "PVE": "https://www.compass.com/homes-for-sale/palos-verdes-estates-ca/",
    "RHE": "https://www.compass.com/homes-for-sale/rolling-hills-estates-ca/",
    "RH": "https://www.compass.com/homes-for-sale/rolling-hills-ca/",
}

MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


# ── Data loading ──────────────────────────────────────────────────
def load_all_sales():
    """Load all closed sales from .tp files."""
    sales = []
    seen_ids = set()

    for tp_path in sorted(glob.glob(TP_GLOB)):
        with open(tp_path, errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                listing_id = row.get("Listing Id", "").strip()
                if not listing_id or listing_id in seen_ids:
                    continue

                close_date_raw = row.get("Close Date", "").strip()
                close_price_raw = row.get("Close Price", "").strip()
                if not close_date_raw or not close_price_raw:
                    continue

                try:
                    close_date = datetime.strptime(
                        close_date_raw.split(" ")[0], "%m/%d/%Y"
                    )
                    close_price = int(
                        close_price_raw.replace("$", "")
                        .replace(",", "")
                        .replace(".00", "")
                        .split(".")[0]
                    )
                except (ValueError, IndexError):
                    continue

                if close_price < 100000:
                    continue

                city_raw = row.get("City", "").strip()
                city_abbr = CITY_NAMES.get(city_raw, city_raw)

                sqft_raw = row.get("Living Area", "").strip()
                try:
                    sqft = int(float(sqft_raw)) if sqft_raw else None
                except ValueError:
                    sqft = None

                dom_raw = row.get("Cumulative Days Active In MLS", "").strip()
                try:
                    dom = int(float(dom_raw)) if dom_raw else None
                except ValueError:
                    dom = None

                ppsf_raw = row.get("Price Per Square Foot", "").strip()
                try:
                    ppsf = float(ppsf_raw) if ppsf_raw else None
                except ValueError:
                    ppsf = None

                list_price_raw = row.get("List Price", "").strip()
                try:
                    list_price = int(
                        list_price_raw.replace("$", "")
                        .replace(",", "")
                        .split(".")[0]
                    ) if list_price_raw else None
                except ValueError:
                    list_price = None

                beds = row.get("Bedrooms Total", "").strip()
                baths = row.get("Bathrooms Total Integer", "").strip()
                street = row.get("Street Name", "").strip()
                street_num = row.get("Street Number Numeric", "").strip()
                year_built = row.get("Year Built", "").strip()
                zipcode = row.get("Zip Code", "").strip()

                seen_ids.add(listing_id)
                sales.append({
                    "id": listing_id,
                    "close_date": close_date,
                    "close_price": close_price,
                    "list_price": list_price,
                    "city": city_abbr,
                    "city_full": city_raw,
                    "sqft": sqft,
                    "dom": dom,
                    "ppsf": ppsf,
                    "beds": beds,
                    "baths": baths,
                    "address": f"{street_num} {street}".strip(),
                    "street": street,
                    "street_num": street_num,
                    "zipcode": zipcode,
                    "year_built": year_built,
                })

    return sales


def aggregate_month(sales):
    """Compute stats for a list of sales."""
    if not sales:
        return None

    prices = [s["close_price"] for s in sales]
    doms = [s["dom"] for s in sales if s["dom"] is not None]
    ppsfs = [s["ppsf"] for s in sales if s["ppsf"] is not None]

    sp_lp_ratios = []
    for s in sales:
        if s["list_price"] and s["list_price"] > 0:
            sp_lp_ratios.append(s["close_price"] / s["list_price"] * 100)

    stats = {
        "count": len(sales),
        "median_price": int(statistics.median(prices)),
        "avg_price": int(statistics.mean(prices)),
        "min_price": min(prices),
        "max_price": max(prices),
        "median_dom": int(statistics.median(doms)) if doms else None,
        "avg_dom": round(statistics.mean(doms), 1) if doms else None,
        "median_ppsf": round(statistics.median(ppsfs)) if ppsfs else None,
        "sp_lp_ratio": round(statistics.mean(sp_lp_ratios), 1) if sp_lp_ratios else None,
        "top_sale": max(sales, key=lambda s: s["close_price"]),
    }
    return stats


def fmt_price(n):
    """Format price as $1.85M or $985K."""
    if n >= 1_000_000:
        m = n / 1_000_000
        return f"${m:,.2f}M" if m < 10 else f"${m:,.1f}M"
    return f"${n // 1000:,}K"


def fmt_price_full(n):
    """Format price with full digits."""
    return f"${n:,}"


def redfin_url(sale):
    """Build a Redfin address page URL for a sale."""
    city_slug = REDFIN_CITY_SLUGS.get(sale["city"], "")
    if not city_slug or not sale.get("street") or not sale.get("street_num"):
        return ""
    street_slug = sale["street"].strip().replace(" ", "-")
    num = sale["street_num"].strip()
    zipcode = sale.get("zipcode", "90275")
    return f"https://www.redfin.com/CA/{city_slug}/{num}-{street_slug}-{zipcode}/home"


def pct_change(current, previous):
    """Return formatted % change string."""
    if previous is None or previous == 0:
        return ""
    change = (current - previous) / previous * 100
    arrow = "+" if change > 0 else ""
    return f"{arrow}{change:.1f}%"


# ── HTML template ─────────────────────────────────────────────────
def render_report(year, month, stats, city_stats, prev_stats, all_months, sales):
    month_name = MONTH_NAMES[month]
    title = f"Palos Verdes Market Report &mdash; {month_name} {year}"
    desc = f"Peninsula housing market data for {month_name} {year}. Median price, days on market, price per sqft, and city breakdowns for RPV, PVE, RHE, and Rolling Hills."

    # Previous / next month links
    month_keys = sorted(all_months.keys())
    current_key = f"{year}-{month:02d}"
    idx = month_keys.index(current_key) if current_key in month_keys else -1
    prev_link = f"/market/{month_keys[idx-1]}/" if idx > 0 else None
    next_link = f"/market/{month_keys[idx+1]}/" if idx < len(month_keys) - 1 else None

    prev_month_name = ""
    if prev_stats:
        pk = month_keys[idx - 1] if idx > 0 else None
        if pk:
            py, pm = pk.split("-")
            prev_month_name = f"{MONTH_NAMES[int(pm)]} {py}"

    # Median price change
    price_change_str = ""
    if prev_stats:
        price_change_str = pct_change(stats["median_price"], prev_stats["median_price"])

    # City breakdown rows
    city_rows = ""
    for abbr in ["PVE", "RPV", "RHE", "RH"]:
        cs = city_stats.get(abbr)
        if not cs:
            continue
        city_rows += f"""
      <tr>
        <td><strong>{abbr}</strong></td>
        <td>{fmt_price(cs['median_price'])}</td>
        <td>{cs['count']}</td>
        <td>{cs['median_dom'] if cs['median_dom'] is not None else '—'}</td>
        <td>${cs['median_ppsf']:,}/ft&sup2;</td>
        <td><a href="{REDFIN_LINKS.get(abbr, '#')}" target="_blank" rel="noopener">Redfin</a> &middot; <a href="{COMPASS_LINKS.get(abbr, '#')}" target="_blank" rel="noopener">Compass</a></td>
      </tr>"""

    # Notable sales (top 5 by price)
    top_sales = sorted(sales, key=lambda s: s["close_price"], reverse=True)[:5]
    notable_rows = ""
    for s in top_sales:
        rf = redfin_url(s)
        addr_cell = f'<a href="{rf}" target="_blank" rel="noopener">{s["address"]}</a>' if rf else s["address"]
        sqft_cell = f'{s["sqft"]:,} ft&sup2;' if s.get("sqft") else "—"
        dom_cell = f'{s["dom"]} days' if s["dom"] is not None else "—"
        notable_rows += f"""
      <tr>
        <td>{addr_cell}</td>
        <td>{s['city']}</td>
        <td>{fmt_price_full(s['close_price'])}</td>
        <td>{s['beds']}/{s['baths']}</td>
        <td>{sqft_cell}</td>
        <td>{dom_cell}</td>
      </tr>"""

    # Archive links
    archive_links = ""
    for mk in reversed(month_keys):
        y, m = mk.split("-")
        mn = MONTH_NAMES[int(m)]
        active = ' class="active"' if mk == current_key else ""
        archive_links += f'<a href="/market/{mk}/"{active}>{mn} {y}</a>\n        '

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{month_name} {year} Palos Verdes Market Report | OwnPalosVerdes.com</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{month_name} {year} PV Peninsula Market Report">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="article">
<meta property="og:url" content="{SITE_URL}/market/{year}-{month:02d}/">
<link rel="canonical" href="{SITE_URL}/market/{year}-{month:02d}/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;1,400;1,500&family=Outfit:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --ink: #1A1A1A; --stone: #3D3D3D; --drift: #5A5A5A;
    --foam: #F7F5F2; --sand: #EDE8E0; --sand-mid: #E0D9CE;
    --teal: #2E6E68; --teal-hover: #245855; --copper: #C97D54;
    --error: #B44A3E; --white: #FFFFFF;
    --serif: 'Playfair Display', Georgia, serif;
    --sans: 'Outfit', system-ui, sans-serif;
  }}
  html {{ scroll-behavior: smooth; }}
  body {{ font-family: var(--sans); background: var(--foam); color: var(--ink); }}

  /* ── NAV ─────── */
  nav {{
    position: sticky; top: 0; z-index: 100; padding: 0 3rem;
    display: flex; align-items: center; justify-content: space-between;
    height: 68px; background: rgba(249,247,244,0.95); backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(224,217,206,0.25);
  }}
  .nav-logo {{ font-family: var(--serif); font-size: 1.1rem; color: var(--ink); text-decoration: none; }}
  .nav-logo span {{ font-style: italic; color: var(--copper); }}
  .nav-back {{ font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--stone); text-decoration: none; }}
  .nav-back:hover {{ color: var(--ink); }}

  /* ── HERO ─────── */
  .report-hero {{
    background: var(--ink); padding: 5rem 3rem 4rem; text-align: center;
  }}
  .report-hero .eyebrow {{
    font-size: 0.65rem; letter-spacing: 0.22em; text-transform: uppercase;
    color: var(--sand-mid); margin-bottom: 1rem;
  }}
  .report-hero h1 {{
    font-family: var(--serif); font-size: clamp(2rem, 4vw, 3.2rem);
    font-weight: 400; color: var(--sand); line-height: 1.15; margin-bottom: 1rem;
  }}
  .report-hero h1 em {{ font-style: italic; }}
  .report-hero .subtitle {{ color: var(--sand-mid); font-size: 0.95rem; font-weight: 300; }}
  .report-nav {{
    display: flex; justify-content: center; gap: 2rem; margin-top: 2rem;
  }}
  .report-nav a {{
    font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--sand-mid); text-decoration: none; opacity: 0.7; transition: opacity 0.2s;
  }}
  .report-nav a:hover {{ opacity: 1; }}

  /* ── STATS CARDS ─────── */
  .stats-section {{ max-width: 1100px; margin: -2rem auto 0; padding: 0 2rem; position: relative; z-index: 2; }}
  .stats-grid {{
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem;
  }}
  .stat-card {{
    background: var(--white); padding: 2rem; text-align: center;
    box-shadow: 0 2px 20px rgba(26,26,26,0.06);
  }}
  .stat-label {{
    font-size: 0.65rem; letter-spacing: 0.15em; text-transform: uppercase;
    color: var(--drift); margin-bottom: 0.5rem;
  }}
  .stat-value {{
    font-family: var(--serif); font-size: 2rem; font-weight: 400; color: var(--ink);
  }}
  .stat-change {{
    font-size: 0.75rem; margin-top: 0.4rem;
  }}
  .stat-change.up {{ color: #2d8a4e; }}
  .stat-change.down {{ color: #c0392b; }}

  /* ── TABLE ─────── */
  .table-section {{ max-width: 1100px; margin: 4rem auto; padding: 0 2rem; }}
  .section-label {{
    font-size: 0.65rem; letter-spacing: 0.2em; text-transform: uppercase;
    color: var(--copper); margin-bottom: 0.5rem;
    display: flex; align-items: center; gap: 0.8rem;
  }}
  .section-label::before {{
    content: ''; width: 28px; height: 1px; background: var(--copper);
  }}
  .table-section h2 {{
    font-family: var(--serif); font-size: 1.6rem; font-weight: 400;
    color: var(--ink); margin-bottom: 2rem;
  }}
  .table-section h2 em {{ font-style: italic; }}
  table {{
    width: 100%; border-collapse: collapse; font-size: 0.85rem;
  }}
  thead th {{
    text-align: left; padding: 0.8rem 1rem;
    font-size: 0.65rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--drift); border-bottom: 2px solid var(--sand-mid);
    font-weight: 400;
  }}
  tbody td {{
    padding: 0.9rem 1rem; border-bottom: 1px solid var(--sand-mid);
    color: var(--stone);
  }}
  tbody tr:hover {{ background: rgba(244,239,230,0.5); }}
  tbody a {{
    color: var(--teal); text-decoration: none; font-size: 0.75rem;
    letter-spacing: 0.05em;
  }}
  tbody a:hover {{ text-decoration: underline; }}

  /* ── REDFIN / COMPASS LINKS ─────── */
  .platform-links {{
    max-width: 1100px; margin: 3rem auto 4rem; padding: 0 2rem;
    display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;
  }}
  .platform-card {{
    background: var(--white); padding: 2rem; box-shadow: 0 2px 16px rgba(26,26,26,0.05);
  }}
  .platform-card h3 {{
    font-family: var(--serif); font-size: 1.1rem; font-weight: 400;
    color: var(--ink); margin-bottom: 1rem;
  }}
  .platform-card ul {{ list-style: none; }}
  .platform-card li {{ margin-bottom: 0.6rem; }}
  .platform-card a {{
    color: var(--teal); text-decoration: none; font-size: 0.85rem;
    border-bottom: 1px solid rgba(26,26,26,0.2); padding-bottom: 1px;
    transition: border-color 0.2s;
  }}
  .platform-card a:hover {{ border-color: var(--teal); }}
  .platform-card .tag {{
    font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--drift); margin-left: 0.5rem;
  }}

  /* ── ARCHIVE ─────── */
  .archive-section {{
    background: var(--ink); padding: 4rem 3rem; text-align: center;
  }}
  .archive-section h3 {{
    font-family: var(--serif); font-size: 1.3rem; font-weight: 400;
    color: var(--sand); margin-bottom: 2rem;
  }}
  .archive-grid {{
    display: flex; flex-wrap: wrap; justify-content: center; gap: 0.5rem 1rem;
    max-width: 900px; margin: 0 auto;
  }}
  .archive-grid a {{
    font-size: 0.75rem; color: var(--sand-mid); text-decoration: none;
    padding: 0.4rem 0.8rem; border: 1px solid rgba(90,90,90,0.3);
    transition: all 0.2s;
  }}
  .archive-grid a:hover, .archive-grid a.active {{
    color: var(--sand); border-color: var(--sand);
  }}

  /* ── FOOTER ─────── */
  footer {{
    padding: 3rem; text-align: center;
    font-size: 0.75rem; color: var(--drift);
  }}
  footer a {{ color: var(--teal); text-decoration: none; }}

  /* ── CTA BAR ─────── */
  .cta-bar {{
    background: var(--sand); padding: 3rem 2rem; text-align: center;
  }}
  .cta-bar p {{
    font-family: var(--serif); font-size: 1.2rem; color: var(--ink);
    margin-bottom: 1rem;
  }}
  .cta-bar a {{
    display: inline-block; font-size: 0.72rem; letter-spacing: 0.1em;
    text-transform: uppercase; padding: 12px 28px; border: 1px solid var(--ink);
    color: var(--ink); text-decoration: none; font-family: var(--sans);
    transition: background 0.2s, color 0.2s;
  }}
  .cta-bar a:hover {{ background: var(--ink); color: var(--white); }}

  /* ── RESPONSIVE ─────── */
  @media (max-width: 768px) {{
    nav {{ padding: 0 1.5rem; }}
    .report-hero {{ padding: 4rem 1.5rem 3rem; }}
    .stats-grid {{ grid-template-columns: 1fr 1fr; }}
    .table-section {{ overflow-x: auto; }}
    .platform-links {{ grid-template-columns: 1fr; }}
  }}
  @media (max-width: 480px) {{
    .stats-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>

<nav>
  <a href="/" class="nav-logo">Own<span>PV</span></a>
  <a href="/" class="nav-back">&larr; Back to OwnPalosVerdes.com</a>
</nav>

<section class="report-hero">
  <div class="eyebrow">Peninsula Market Data</div>
  <h1>{month_name} {year}<br><em>Market Report</em></h1>
  <p class="subtitle">Closed residential sales across the Palos Verdes Peninsula</p>
  <div class="report-nav">
    {"<a href='" + prev_link + "'>&larr; " + prev_month_name + "</a>" if prev_link else "<span></span>"}
    <a href="/market/">All Reports</a>
    {"<a href='" + next_link + "'>Next month &rarr;</a>" if next_link else "<span></span>"}
  </div>
</section>

<section class="stats-section">
  <div class="stats-grid">
    <div class="stat-card">
      <div class="stat-label">Median Sale Price</div>
      <div class="stat-value">{fmt_price(stats['median_price'])}</div>
      {"<div class='stat-change " + ("up" if stats["median_price"] >= prev_stats["median_price"] else "down") + "'>" + price_change_str + " vs prior month</div>" if prev_stats and price_change_str else ""}
    </div>
    <div class="stat-card">
      <div class="stat-label">Homes Sold</div>
      <div class="stat-value">{stats['count']}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Median Days on Market</div>
      <div class="stat-value">{stats['median_dom'] if stats['median_dom'] is not None else '—'}</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Median $/ft&sup2;</div>
      <div class="stat-value">${stats['median_ppsf']:,}</div>
    </div>
  </div>
</section>

<section class="table-section">
  <div class="section-label">By City</div>
  <h2>Peninsula <em>breakdown.</em></h2>
  <table>
    <thead>
      <tr>
        <th>City</th>
        <th>Median Price</th>
        <th>Sales</th>
        <th>Median DOM</th>
        <th>$/ft&sup2;</th>
        <th>Live Market</th>
      </tr>
    </thead>
    <tbody>{city_rows}
    </tbody>
  </table>
</section>

<section class="table-section">
  <div class="section-label">Notable Sales</div>
  <h2>Top transactions <em>this month.</em></h2>
  <table>
    <thead>
      <tr>
        <th>Address</th>
        <th>City</th>
        <th>Close Price</th>
        <th>Bed/Bath</th>
        <th>Size</th>
        <th>DOM</th>
      </tr>
    </thead>
    <tbody>{notable_rows}
    </tbody>
  </table>
</section>

<section class="platform-links">
  <div class="platform-card">
    <h3>Search on Compass</h3>
    <ul>
      <li><a href="https://www.compass.com/homes-for-sale/palos-verdes-estates-ca/" target="_blank" rel="noopener">Palos Verdes Estates</a> <span class="tag">PVE</span></li>
      <li><a href="https://www.compass.com/homes-for-sale/rancho-palos-verdes-ca/" target="_blank" rel="noopener">Rancho Palos Verdes</a> <span class="tag">RPV</span></li>
      <li><a href="https://www.compass.com/homes-for-sale/rolling-hills-estates-ca/" target="_blank" rel="noopener">Rolling Hills Estates</a> <span class="tag">RHE</span></li>
      <li><a href="https://www.compass.com/homes-for-sale/rolling-hills-ca/" target="_blank" rel="noopener">Rolling Hills</a> <span class="tag">RH</span></li>
    </ul>
  </div>
  <div class="platform-card">
    <h3>Market Data on Redfin</h3>
    <ul>
      <li><a href="https://www.redfin.com/city/30570/CA/Palos-Verdes-Estates/housing-market" target="_blank" rel="noopener">PVE Housing Market</a> <span class="tag">Trends</span></li>
      <li><a href="https://www.redfin.com/city/30573/CA/Rancho-Palos-Verdes/housing-market" target="_blank" rel="noopener">RPV Housing Market</a> <span class="tag">Trends</span></li>
      <li><a href="https://www.redfin.com/city/30574/CA/Rolling-Hills-Estates/housing-market" target="_blank" rel="noopener">RHE Housing Market</a> <span class="tag">Trends</span></li>
      <li><a href="https://www.redfin.com/city/15808/CA/Rolling-Hills/housing-market" target="_blank" rel="noopener">RH Housing Market</a> <span class="tag">Trends</span></li>
    </ul>
  </div>
</section>

<section class="cta-bar">
  <p>Want a deeper look at the numbers for your street?</p>
  <a href="/#contact">Talk to Angelique</a>
</section>

<section class="archive-section">
  <h3>All monthly reports</h3>
  <div class="archive-grid">
    {archive_links}
  </div>
</section>

<footer>
  <p>&copy; {datetime.now().year} Angelique Lyle &middot; Compass &middot; DRE# 01475592</p>
  <p style="margin-top:0.5rem;"><a href="/">OwnPalosVerdes.com</a></p>
  <p style="margin-top:1rem; font-size:0.65rem; max-width:700px; margin-left:auto; margin-right:auto;">
    Data sourced from CRMLS. Deemed reliable but not guaranteed.
    Compass is a licensed real estate broker. Equal Housing Opportunity.
  </p>
</footer>

</body>
</html>"""

    return html


def render_index(all_months, monthly_stats):
    """Render the /market/index.html page."""
    month_keys = sorted(all_months.keys(), reverse=True)

    rows = ""
    for mk in month_keys:
        y, m = mk.split("-")
        mn = MONTH_NAMES[int(m)]
        stats = monthly_stats[mk]
        rows += f"""
      <tr>
        <td><a href="/market/{mk}/">{mn} {y}</a></td>
        <td>{fmt_price(stats['median_price'])}</td>
        <td>{stats['count']}</td>
        <td>{stats['median_dom'] if stats['median_dom'] is not None else '—'}</td>
        <td>${stats['median_ppsf']:,}/ft&sup2;</td>
      </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Palos Verdes Monthly Market Reports | OwnPalosVerdes.com</title>
<meta name="description" content="Monthly housing market reports for the Palos Verdes Peninsula. Median prices, days on market, and sales data for PVE, RPV, RHE, and Rolling Hills.">
<link rel="canonical" href="{SITE_URL}/market/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;1,400;1,500&family=Outfit:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --ink: #1A1A1A; --stone: #3D3D3D; --drift: #5A5A5A;
    --foam: #F7F5F2; --sand: #EDE8E0; --sand-mid: #E0D9CE;
    --teal: #2E6E68; --teal-hover: #245855; --copper: #C97D54;
    --error: #B44A3E; --white: #FFFFFF;
    --serif: 'Playfair Display', Georgia, serif;
    --sans: 'Outfit', system-ui, sans-serif;
  }}
  html {{ scroll-behavior: smooth; }}
  body {{ font-family: var(--sans); background: var(--foam); color: var(--ink); }}
  nav {{
    position: sticky; top: 0; z-index: 100; padding: 0 3rem;
    display: flex; align-items: center; justify-content: space-between;
    height: 68px; background: rgba(249,247,244,0.95); backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(224,217,206,0.25);
  }}
  .nav-logo {{ font-family: var(--serif); font-size: 1.1rem; color: var(--ink); text-decoration: none; }}
  .nav-logo span {{ font-style: italic; color: var(--copper); }}
  .nav-back {{ font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--stone); text-decoration: none; }}
  .nav-back:hover {{ color: var(--ink); }}
  .hero {{
    background: var(--ink); padding: 5rem 3rem 4rem; text-align: center;
  }}
  .hero .eyebrow {{
    font-size: 0.65rem; letter-spacing: 0.22em; text-transform: uppercase;
    color: var(--sand-mid); margin-bottom: 1rem;
  }}
  .hero h1 {{
    font-family: var(--serif); font-size: clamp(2rem, 4vw, 3.2rem);
    font-weight: 400; color: var(--sand); line-height: 1.15; margin-bottom: 1rem;
  }}
  .hero h1 em {{ font-style: italic; }}
  .hero p {{ color: var(--sand-mid); font-size: 0.95rem; font-weight: 300; max-width: 600px; margin: 0 auto; }}
  .content {{ max-width: 1100px; margin: 3rem auto; padding: 0 2rem; }}
  .section-label {{
    font-size: 0.65rem; letter-spacing: 0.2em; text-transform: uppercase;
    color: var(--copper); margin-bottom: 0.5rem;
    display: flex; align-items: center; gap: 0.8rem;
  }}
  .section-label::before {{ content: ''; width: 28px; height: 1px; background: var(--copper); }}
  .content h2 {{
    font-family: var(--serif); font-size: 1.6rem; font-weight: 400;
    color: var(--ink); margin-bottom: 2rem;
  }}
  .content h2 em {{ font-style: italic; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
  thead th {{
    text-align: left; padding: 0.8rem 1rem;
    font-size: 0.65rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--drift); border-bottom: 2px solid var(--sand-mid); font-weight: 400;
  }}
  tbody td {{ padding: 0.9rem 1rem; border-bottom: 1px solid var(--sand-mid); color: var(--stone); }}
  tbody tr:hover {{ background: rgba(244,239,230,0.5); }}
  tbody a {{ color: var(--teal); text-decoration: none; font-weight: 500; }}
  tbody a:hover {{ text-decoration: underline; }}
  .platform-links {{
    max-width: 1100px; margin: 3rem auto 4rem; padding: 0 2rem;
    display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;
  }}
  .platform-card {{
    background: var(--white); padding: 2rem; box-shadow: 0 2px 16px rgba(26,26,26,0.05);
  }}
  .platform-card h3 {{
    font-family: var(--serif); font-size: 1.1rem; font-weight: 400;
    color: var(--ink); margin-bottom: 1rem;
  }}
  .platform-card ul {{ list-style: none; }}
  .platform-card li {{ margin-bottom: 0.6rem; }}
  .platform-card a {{
    color: var(--teal); text-decoration: none; font-size: 0.85rem;
    border-bottom: 1px solid rgba(26,26,26,0.2); padding-bottom: 1px;
  }}
  .platform-card a:hover {{ border-color: var(--teal); }}
  .platform-card .tag {{
    font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--drift); margin-left: 0.5rem;
  }}
  footer {{
    padding: 3rem; text-align: center; font-size: 0.75rem; color: var(--drift);
    border-top: 1px solid var(--sand-mid);
  }}
  footer a {{ color: var(--teal); text-decoration: none; }}
  @media (max-width: 768px) {{
    nav {{ padding: 0 1.5rem; }}
    .hero {{ padding: 4rem 1.5rem 3rem; }}
    .platform-links {{ grid-template-columns: 1fr; }}
    .content {{ overflow-x: auto; }}
  }}
</style>
</head>
<body>

<nav>
  <a href="/" class="nav-logo">Own<span>PV</span></a>
  <a href="/" class="nav-back">&larr; OwnPalosVerdes.com</a>
</nav>

<section class="hero">
  <div class="eyebrow">Market Intelligence</div>
  <h1>Palos Verdes<br><em>Market Reports</em></h1>
  <p>Monthly housing data for the Peninsula. Median prices, days on market, inventory, and city-level breakdowns from closed CRMLS transactions.</p>
</section>

<section class="content">
  <div class="section-label">Monthly Reports</div>
  <h2>All available <em>months.</em></h2>
  <table>
    <thead>
      <tr>
        <th>Month</th>
        <th>Median Price</th>
        <th>Sales</th>
        <th>Median DOM</th>
        <th>$/ft&sup2;</th>
      </tr>
    </thead>
    <tbody>{rows}
    </tbody>
  </table>
</section>

<section class="platform-links">
  <div class="platform-card">
    <h3>Search on Compass</h3>
    <ul>
      <li><a href="https://www.compass.com/homes-for-sale/palos-verdes-estates-ca/" target="_blank" rel="noopener">Palos Verdes Estates</a> <span class="tag">PVE</span></li>
      <li><a href="https://www.compass.com/homes-for-sale/rancho-palos-verdes-ca/" target="_blank" rel="noopener">Rancho Palos Verdes</a> <span class="tag">RPV</span></li>
      <li><a href="https://www.compass.com/homes-for-sale/rolling-hills-estates-ca/" target="_blank" rel="noopener">Rolling Hills Estates</a> <span class="tag">RHE</span></li>
      <li><a href="https://www.compass.com/homes-for-sale/rolling-hills-ca/" target="_blank" rel="noopener">Rolling Hills</a> <span class="tag">RH</span></li>
    </ul>
  </div>
  <div class="platform-card">
    <h3>Market Data on Redfin</h3>
    <ul>
      <li><a href="https://www.redfin.com/city/30570/CA/Palos-Verdes-Estates/housing-market" target="_blank" rel="noopener">PVE Housing Market</a> <span class="tag">Trends</span></li>
      <li><a href="https://www.redfin.com/city/30573/CA/Rancho-Palos-Verdes/housing-market" target="_blank" rel="noopener">RPV Housing Market</a> <span class="tag">Trends</span></li>
      <li><a href="https://www.redfin.com/city/30574/CA/Rolling-Hills-Estates/housing-market" target="_blank" rel="noopener">RHE Housing Market</a> <span class="tag">Trends</span></li>
      <li><a href="https://www.redfin.com/city/15808/CA/Rolling-Hills/housing-market" target="_blank" rel="noopener">RH Housing Market</a> <span class="tag">Trends</span></li>
    </ul>
  </div>
</section>

<footer>
  <p>&copy; {datetime.now().year} Angelique Lyle &middot; Compass &middot; DRE# 01475592</p>
  <p style="margin-top:0.5rem;"><a href="/">OwnPalosVerdes.com</a></p>
  <p style="margin-top:1rem; font-size:0.65rem; max-width:700px; margin-left:auto; margin-right:auto;">
    Data sourced from CRMLS. Deemed reliable but not guaranteed.
    Compass is a licensed real estate broker. Equal Housing Opportunity.
  </p>
</footer>

</body>
</html>"""
    return html


# ── Main ──────────────────────────────────────────────────────────
def main():
    print("Loading sales data...")
    sales = load_all_sales()
    print(f"  {len(sales)} closed sales loaded")

    # Group by month
    by_month = defaultdict(list)
    for s in sales:
        key = f"{s['close_date'].year}-{s['close_date'].month:02d}"
        by_month[key].append(s)

    # Sort months
    month_keys = sorted(by_month.keys())
    print(f"  {len(month_keys)} months: {month_keys[0]} to {month_keys[-1]}")

    # Compute stats for each month
    monthly_stats = {}
    for mk in month_keys:
        monthly_stats[mk] = aggregate_month(by_month[mk])

    # Generate individual month pages
    OUTPUT_DIR.mkdir(exist_ok=True)
    for i, mk in enumerate(month_keys):
        year, month = int(mk.split("-")[0]), int(mk.split("-")[1])
        stats = monthly_stats[mk]
        prev_stats = monthly_stats[month_keys[i - 1]] if i > 0 else None

        # City breakdown
        city_groups = defaultdict(list)
        for s in by_month[mk]:
            city_groups[s["city"]].append(s)
        city_stats = {c: aggregate_month(ss) for c, ss in city_groups.items()}

        html = render_report(year, month, stats, city_stats, prev_stats, by_month, by_month[mk])

        out_dir = OUTPUT_DIR / mk
        out_dir.mkdir(exist_ok=True)
        (out_dir / "index.html").write_text(html)
        print(f"  Generated market/{mk}/index.html ({stats['count']} sales, median {fmt_price(stats['median_price'])})")

    # Generate index page
    index_html = render_index(by_month, monthly_stats)
    (OUTPUT_DIR / "index.html").write_text(index_html)
    print(f"  Generated market/index.html")

    print(f"\nDone! {len(month_keys)} monthly reports + index generated in market/")


if __name__ == "__main__":
    main()
