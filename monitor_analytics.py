#!/usr/bin/env python3
"""
Weekly analytics monitor for OwnPalosVerdes.com.

Pulls a small, consistent set of GA4 + Google Search Console metrics using the
ownpv-svc service account and appends a timestamped snapshot to two CSVs under
docs/. Designed to run unattended (launchd/cron) so we accumulate a trend line
to see whether the buried target queries climb over time.

  GA4 property : 533060681   (measurement id G-ZY3DD9BYZ2)
  GSC property : sc-domain:ownpalosverdes.com
  Key          : ~/.config/ownpv/ga4-sa-key.json

Outputs:
  docs/analytics-log.csv      one row per run (top-line GA4 + GSC)
  docs/analytics-queries.csv  one row per run per tracked query (GSC position)
"""

import csv
import json
import os
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timedelta, timezone

from google.oauth2 import service_account
import google.auth.transport.requests as gtr

KEY = os.path.expanduser("~/.config/ownpv/ga4-sa-key.json")
GA4_PROPERTY = "533060681"
GSC_SITE = "sc-domain:ownpalosverdes.com"
# Logs live OUTSIDE the repo — this repo is served publicly by GitHub Pages,
# so analytics data must not sit in a deployed path.
DATA_DIR = os.path.expanduser("~/.config/ownpv")
LOG_CSV = os.path.join(DATA_DIR, "analytics-log.csv")
QUERIES_CSV = os.path.join(DATA_DIR, "analytics-queries.csv")

# The high-intent local queries we're trying to move up (from the GSC baseline).
TRACKED_QUERIES = [
    "palos verdes real estate",
    "palos verdes real estate agent",
    "palos verdes realtors",
    "palos verdes luxury homes",
    "palos verdes estates luxury real estate",
]

GA4_SCOPE = ["https://www.googleapis.com/auth/analytics.readonly"]
GSC_SCOPE = ["https://www.googleapis.com/auth/webmasters.readonly"]


def token(scopes):
    creds = service_account.Credentials.from_service_account_file(KEY, scopes=scopes)
    creds.refresh(gtr.Request())
    return creds.token


def post(url, tok, body):
    req = urllib.request.Request(
        url,
        headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"},
        data=json.dumps(body).encode(),
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode()[:300]}


def ga4():
    """US sessions/engaged (real-signal, bot-filtered) + generate_lead, last 28d."""
    tok = token(GA4_SCOPE)
    url = f"https://analyticsdata.googleapis.com/v1beta/properties/{GA4_PROPERTY}:runReport"
    out = {"ga4_us_sessions_28d": "", "ga4_us_engaged_28d": "", "ga4_leads_28d": ""}
    # US sessions + engaged sessions
    st, d = post(url, tok, {
        "dateRanges": [{"startDate": "28daysAgo", "endDate": "today"}],
        "dimensions": [{"name": "country"}],
        "metrics": [{"name": "sessions"}, {"name": "engagedSessions"}],
        "dimensionFilter": {"filter": {"fieldName": "country",
                                       "stringFilter": {"value": "United States"}}},
    })
    if st == 200 and d.get("rows"):
        m = d["rows"][0]["metricValues"]
        out["ga4_us_sessions_28d"] = m[0]["value"]
        out["ga4_us_engaged_28d"] = m[1]["value"]
    # generate_lead events
    st, d = post(url, tok, {
        "dateRanges": [{"startDate": "28daysAgo", "endDate": "today"}],
        "dimensions": [{"name": "eventName"}],
        "metrics": [{"name": "eventCount"}],
        "dimensionFilter": {"filter": {"fieldName": "eventName",
                                       "stringFilter": {"value": "generate_lead"}}},
    })
    if st == 200:
        out["ga4_leads_28d"] = d["rows"][0]["metricValues"][0]["value"] if d.get("rows") else "0"
    return out


def gsc():
    """GSC totals + per-tracked-query position over a fresh 28d window."""
    tok = token(GSC_SCOPE)
    enc = urllib.parse.quote(GSC_SITE, safe="")
    url = f"https://www.googleapis.com/webmasters/v3/sites/{enc}/searchAnalytics/query"
    # GSC data lags ~2 days; end the window 3 days back so it's complete.
    end = datetime.now(timezone.utc).date() - timedelta(days=3)
    start = end - timedelta(days=27)
    START, END = start.isoformat(), end.isoformat()

    totals = {"gsc_clicks_28d": "", "gsc_impressions_28d": "", "gsc_avg_position_28d": ""}
    st, d = post(url, tok, {"startDate": START, "endDate": END})
    if st == 200 and d.get("rows"):
        r = d["rows"][0]
        totals["gsc_clicks_28d"] = str(int(r["clicks"]))
        totals["gsc_impressions_28d"] = str(int(r["impressions"]))
        totals["gsc_avg_position_28d"] = f"{r['position']:.1f}"

    # Per-query rows (pull a wide slice, then pick out the tracked queries).
    st, d = post(url, tok, {"startDate": START, "endDate": END,
                            "dimensions": ["query"], "rowLimit": 250})
    byq = {}
    if st == 200:
        for r in d.get("rows", []):
            byq[r["keys"][0].lower()] = r
    query_rows = []
    for q in TRACKED_QUERIES:
        r = byq.get(q.lower())
        query_rows.append({
            "query": q,
            "impressions": str(int(r["impressions"])) if r else "0",
            "clicks": str(int(r["clicks"])) if r else "0",
            "position": f"{r['position']:.1f}" if r else "",
        })
    return totals, query_rows, START, END


def append_csv(path, header, row):
    exists = os.path.exists(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        if not exists:
            w.writeheader()
        w.writerow(row)


def main():
    run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    g = ga4()
    totals, query_rows, gsc_start, gsc_end = gsc()

    log_header = ["run_date", "ga4_us_sessions_28d", "ga4_us_engaged_28d",
                  "ga4_leads_28d", "gsc_clicks_28d", "gsc_impressions_28d",
                  "gsc_avg_position_28d", "gsc_window"]
    log_row = {"run_date": run_date, "gsc_window": f"{gsc_start}..{gsc_end}", **g, **totals}
    append_csv(LOG_CSV, log_header, log_row)

    q_header = ["run_date", "query", "impressions", "clicks", "position"]
    for qr in query_rows:
        append_csv(QUERIES_CSV, q_header, {"run_date": run_date, **qr})

    # Console summary (captured to the launchd log).
    print(f"[{run_date}] GA4 US 28d: sessions={g['ga4_us_sessions_28d']} "
          f"engaged={g['ga4_us_engaged_28d']} leads={g['ga4_leads_28d']}  |  "
          f"GSC 28d: clicks={totals['gsc_clicks_28d']} "
          f"impr={totals['gsc_impressions_28d']} avgPos={totals['gsc_avg_position_28d']}")
    for qr in query_rows:
        print(f"    {qr['query']:<42} pos={qr['position'] or '—':>5}  impr={qr['impressions']}")


if __name__ == "__main__":
    main()
