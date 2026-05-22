#!/usr/bin/env python3
"""Fetch Google Search Console data through Maton Gateway.

The script never stores your Maton key. Set MATON_API_KEY in the environment
or put it in a local .env file that is ignored by git.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import date, timedelta
from pathlib import Path
from typing import Any

GATEWAY = "https://gateway.maton.ai/google-search-console"
DEFAULT_SITE = "https://inservic.com.ua/"
DEFAULT_FILTERS = [
    "elektrosamokat",
    "remont-elektrosamokativ",
    "remont-akumulyatora-elektrosamokata",
    "remont-kontrolera-elektrosamokata",
    "remont-motor-kolesa-elektrosamokata",
    "remont-elektrotransportu",
]


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def maton_request(api_key: str, method: str, native_path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{GATEWAY}/{native_path.lstrip('/')}"
    data = None
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload) if payload else {}
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Maton/GSC request failed: HTTP {exc.code} {exc.reason}\n{details}") from exc


def build_query(start_date: str, end_date: str, dimensions: list[str], page_filter: str | None, row_limit: int, start_row: int) -> dict[str, Any]:
    body: dict[str, Any] = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": dimensions,
        "rowLimit": row_limit,
        "startRow": start_row,
    }
    if page_filter:
        body["dimensionFilterGroups"] = [{
            "filters": [{
                "dimension": "page",
                "operator": "contains",
                "expression": page_filter,
            }]
        }]
    return body


def rows_to_csv(rows: list[dict[str, Any]], dimensions: list[str], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [*dimensions, "clicks", "impressions", "ctr", "position"]
    with output.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in rows:
            keys = item.get("keys", [])
            row = {dim: keys[i] if i < len(keys) else "" for i, dim in enumerate(dimensions)}
            row.update({
                "clicks": item.get("clicks", 0),
                "impressions": item.get("impressions", 0),
                "ctr": item.get("ctr", 0),
                "position": item.get("position", 0),
            })
            writer.writerow(row)


def fetch_search_analytics(api_key: str, site: str, start_date: str, end_date: str, dimensions: list[str], page_filter: str | None, row_limit: int) -> list[dict[str, Any]]:
    encoded_site = urllib.parse.quote(site, safe="")
    native_path = f"webmasters/v3/sites/{encoded_site}/searchAnalytics/query"
    all_rows: list[dict[str, Any]] = []
    start_row = 0
    while True:
        body = build_query(start_date, end_date, dimensions, page_filter, row_limit, start_row)
        response = maton_request(api_key, "POST", native_path, body)
        batch = response.get("rows", [])
        all_rows.extend(batch)
        if len(batch) < row_limit:
            break
        start_row += row_limit
    return all_rows


def cmd_sites(api_key: str) -> int:
    data = maton_request(api_key, "GET", "webmasters/v3/sites")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def cmd_fetch(args: argparse.Namespace, api_key: str) -> int:
    dimensions = [part.strip() for part in args.dimensions.split(",") if part.strip()]
    rows = fetch_search_analytics(api_key, args.site, args.start_date, args.end_date, dimensions, args.page_filter, args.row_limit)
    output = Path(args.output)
    rows_to_csv(rows, dimensions, output)
    print(f"Saved {len(rows)} rows -> {output}")
    return 0


def cmd_fetch_all(args: argparse.Namespace, api_key: str) -> int:
    output_dir = Path(args.output_dir)
    filters = DEFAULT_FILTERS if args.default_filters else [None]
    configs = [
        ("page_query_date", ["page", "query", "date"]),
        ("pages", ["page"]),
        ("queries", ["query"]),
        ("daily", ["date"]),
    ]
    total = 0
    for page_filter in filters:
        suffix = page_filter or "all"
        for name, dimensions in configs:
            rows = fetch_search_analytics(api_key, args.site, args.start_date, args.end_date, dimensions, page_filter, args.row_limit)
            output = output_dir / f"gsc_{name}_{suffix}_{args.start_date}_{args.end_date}.csv"
            rows_to_csv(rows, dimensions, output)
            total += len(rows)
            print(f"Saved {len(rows):5d} rows -> {output}")
    print(f"Done. Total rows: {total}")
    return 0


def parse_args() -> argparse.Namespace:
    yesterday = date.today() - timedelta(days=2)  # GSC normally has a 2-3 day delay.
    start = yesterday - timedelta(days=28)
    parser = argparse.ArgumentParser(description="Maton Google Search Console exporter for InService SEO.")
    parser.add_argument("--env-file", default=".env", help="Local env file path. Default: .env")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("sites", help="List Search Console properties available through Maton.")

    fetch = sub.add_parser("fetch", help="Export one Search Analytics report to CSV.")
    fetch.add_argument("--site", default=DEFAULT_SITE)
    fetch.add_argument("--start-date", default=start.isoformat())
    fetch.add_argument("--end-date", default=yesterday.isoformat())
    fetch.add_argument("--dimensions", default="page,query,date")
    fetch.add_argument("--page-filter", default=None)
    fetch.add_argument("--row-limit", type=int, default=25000)
    fetch.add_argument("--output", default="data/gsc/gsc_export.csv")

    all_cmd = sub.add_parser("fetch-all", help="Export standard reports for electric transport filters.")
    all_cmd.add_argument("--site", default=DEFAULT_SITE)
    all_cmd.add_argument("--start-date", default=start.isoformat())
    all_cmd.add_argument("--end-date", default=yesterday.isoformat())
    all_cmd.add_argument("--row-limit", type=int, default=25000)
    all_cmd.add_argument("--output-dir", default="data/gsc")
    all_cmd.add_argument("--default-filters", action="store_true", help="Export reports for the InService electric transport URL filters.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_dotenv(Path(args.env_file))
    api_key = os.environ.get("MATON_API_KEY")
    if not api_key:
        print("MATON_API_KEY is not set. Create a local .env from .env.example or set the environment variable.", file=sys.stderr)
        return 2
    if args.command == "sites":
        return cmd_sites(api_key)
    if args.command == "fetch":
        return cmd_fetch(args, api_key)
    if args.command == "fetch-all":
        return cmd_fetch_all(args, api_key)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
