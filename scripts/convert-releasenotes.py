#!/usr/bin/env python3
"""Convert releasenote/*.csv files into annotations.json for the dashboard graph."""

import csv
import json
import os
import re
from datetime import datetime

RELEASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'releasenote')
OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'annotations.json')


def parse_date(s):
    """Parse date string like '2025/1/6' or '2025/01/06' to 'YYYY-MM-DD'."""
    s = s.strip()
    if not s:
        return None
    parts = s.split('/')
    if len(parts) != 3:
        return None
    try:
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        return f'{y:04d}-{m:02d}-{d:02d}'
    except (ValueError, IndexError):
        return None


def extract_first_url(detail):
    """Extract the first URL from the detail field."""
    if not detail:
        return ''
    urls = re.findall(r'https?://[^\s,\'"]+', detail)
    return urls[0] if urls else detail.strip()


def main():
    events = []
    csv_files = sorted(f for f in os.listdir(RELEASE_DIR) if f.endswith('.csv'))

    for fname in csv_files:
        filepath = os.path.join(RELEASE_DIR, fname)
        with open(filepath, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                summary = (row.get('Release Summary') or '').strip()
                if not summary:
                    continue

                release_date = parse_date(row.get('Release Date', ''))
                release_week = parse_date(row.get('Release Week', ''))
                if not release_date:
                    continue

                month = release_date[:7]  # "YYYY-MM"
                area = (row.get('Area') or '').strip()
                by_whom = (row.get('By Whom') or '').strip()
                link = extract_first_url(row.get('Detail', ''))

                events.append({
                    'date': release_date,
                    'month': month,
                    'area': area,
                    'title': summary,
                    'by': by_whom,
                    'link': link,
                })

    # Sort by date
    events.sort(key=lambda e: e['date'])

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump({'events': events}, f, ensure_ascii=False, indent=2)

    print(f'Generated {OUTPUT} with {len(events)} events from {len(csv_files)} CSV files')


if __name__ == '__main__':
    main()
