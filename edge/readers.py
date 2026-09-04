"""
READERS - read the register back.

The Worker writes one row per request to Workers Analytics Engine. This queries
that dataset over the SQL API and prints what came, by class of reader, by name,
and by path. It answers the question the gallery could not previously ask about
itself: how much of the traffic is a machine, and which machines.

    export CF_ACCOUNT_ID=...      # Cloudflare dashboard, right-hand column
    export CF_API_TOKEN=...       # token with Account Analytics: Read
    python3 edge/readers.py --days 7

Free plan allows 10,000 read queries a day. This makes four.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

DATASET = "gallery_readers"
API = "https://api.cloudflare.com/client/v4/accounts/{acct}/analytics_engine/sql"


def query(sql):
    acct = os.environ.get("CF_ACCOUNT_ID")
    token = os.environ.get("CF_API_TOKEN")
    if not acct or not token:
        sys.exit("Set CF_ACCOUNT_ID and CF_API_TOKEN.")
    req = urllib.request.Request(
        API.format(acct=acct),
        data=sql.encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "text/plain"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r).get("data", [])
    except urllib.error.HTTPError as e:
        sys.exit(f"{e.code} {e.reason}: {e.read().decode()[:400]}")


def table(rows, cols, title):
    print(f"\n{title}")
    print("-" * len(title))
    if not rows:
        print("  (nothing yet)")
        return
    widths = [max(len(c), max(len(str(r[c])) for r in rows)) for c in cols]
    print("  " + "  ".join(c.ljust(w) for c, w in zip(cols, widths)))
    for r in rows:
        print("  " + "  ".join(str(r[c]).ljust(w) for c, w in zip(cols, widths)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    args = ap.parse_args()
    since = f"timestamp > NOW() - INTERVAL '{args.days}' DAY"

    # _sample_interval undoes Analytics Engine's sampling, so the counts are
    # estimates of the true number rather than of the number stored.
    table(
        query(f"""SELECT blob1 AS class, SUM(_sample_interval) AS requests
                  FROM {DATASET} WHERE {since}
                  GROUP BY class ORDER BY requests DESC"""),
        ["class", "requests"],
        f"By class of reader, last {args.days} days",
    )
    table(
        query(f"""SELECT blob2 AS reader, blob1 AS class,
                         SUM(_sample_interval) AS requests
                  FROM {DATASET} WHERE {since}
                  GROUP BY reader, class ORDER BY requests DESC LIMIT 30"""),
        ["reader", "class", "requests"],
        "By reader",
    )
    table(
        query(f"""SELECT blob3 AS path, SUM(_sample_interval) AS requests
                  FROM {DATASET} WHERE {since} AND blob1 != 'browser'
                  GROUP BY path ORDER BY requests DESC LIMIT 30"""),
        ["path", "requests"],
        "Paths that a machine fetched",
    )
    table(
        query(f"""SELECT blob6 AS referer, SUM(_sample_interval) AS requests
                  FROM {DATASET} WHERE {since} AND blob6 != ''
                  GROUP BY referer ORDER BY requests DESC LIMIT 20"""),
        ["referer", "requests"],
        "Where a reader came from",
    )


if __name__ == "__main__":
    main()
