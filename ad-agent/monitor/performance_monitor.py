import os
import requests
from datetime import datetime, timedelta

from db.database import get_live_ads, save_performance

META_API_BASE = 'https://graph.facebook.com/v19.0'

# CTR benchmarks (percent)
BENCHMARKS = {
    'meta': 1.0,
    'google': 3.0,
    'linkedin': 0.5,
}

_LINE = '─' * 62


def _fetch_meta_insights(ad: dict) -> dict | None:
    access_token = os.environ.get('META_ACCESS_TOKEN')
    if not access_token or not ad.get('platform_ad_id'):
        return None

    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    try:
        resp = requests.get(
            f"{META_API_BASE}/{ad['platform_ad_id']}/insights",
            params={
                'fields': 'impressions,clicks,ctr,spend,actions,cost_per_action_type',
                'time_range': f'{{"since":"{yesterday}","until":"{yesterday}"}}',
                'access_token': access_token,
            },
            timeout=30,
        )
        resp.raise_for_status()
    except Exception:
        return None

    data = resp.json().get('data', [])
    if not data:
        return None

    d = data[0]
    conversions = sum(
        int(a.get('value', 0))
        for a in d.get('actions', [])
        if a.get('action_type') in ('lead', 'offsite_conversion.lead')
    )
    spend = float(d.get('spend', 0))
    clicks = int(d.get('clicks', 0))
    cpc = round(spend / max(clicks, 1), 4)
    roas = round(conversions / max(spend, 0.01), 4)

    return {
        'ad_id': ad['id'],
        'date': yesterday,
        'impressions': int(d.get('impressions', 0)),
        'clicks': clicks,
        'ctr': float(d.get('ctr', 0)),
        'spend': spend,
        'conversions': conversions,
        'cpc': cpc,
        'roas': roas,
    }


def run_monitor():
    live_ads = get_live_ads()

    if not live_ads:
        print('\nNo live ads to monitor.\n')
        return

    print(f'\nMonitoring {len(live_ads)} live ad(s)...\n')
    underperformers = []

    for ad in live_ads:
        platform = ad['platform'].lower()
        label = f'[{platform.upper()}] Ad {ad["id"]}'

        if platform != 'meta':
            print(f'  {label} — {platform.upper()} monitoring not yet integrated. Check platform dashboard.')
            continue

        metrics = _fetch_meta_insights(ad)

        if not metrics:
            reason = 'no credentials' if not os.environ.get('META_ACCESS_TOKEN') else 'no data yet'
            print(f'  {label} — no metrics ({reason})')
            continue

        save_performance(metrics)

        # Meta API returns CTR as a decimal (e.g. 0.0123 = 1.23%) — normalise
        ctr_pct = metrics['ctr'] * 100 if metrics['ctr'] < 1 else metrics['ctr']
        benchmark = BENCHMARKS.get(platform, 1.0)
        flag = '⚠  UNDERPERFORMING' if ctr_pct < benchmark else '✓'

        print(
            f'  {label} — '
            f'Impressions: {metrics["impressions"]:,}  '
            f'CTR: {ctr_pct:.2f}%  '
            f'Spend: ${metrics["spend"]:.2f}  '
            f'{flag}'
        )

        if ctr_pct < benchmark:
            underperformers.append(ad)

    if underperformers:
        print(f'\n  {len(underperformers)} ad(s) below CTR benchmark:')
        for ad in underperformers:
            print(f'    • [{ad["platform"].upper()}] "{ad["headline"]}" (ID {ad["id"]})')
        print("\n  Tip: run 'python main.py generate' with a new brief to create improved variants.\n")
    else:
        print()
