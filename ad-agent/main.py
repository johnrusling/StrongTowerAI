#!/usr/bin/env python3
"""Strong Tower AI — Ad Content Agent CLI"""

import argparse
import sys
import os

# Force UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add project root to path so submodules resolve correctly
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from db.database import init_db


# ── subcommand handlers ───────────────────────────────────────────────────────

def cmd_generate(args):
    from generator.content_generator import generate_ads

    print(f'\nGenerating {args.count} {args.platform.upper()} ad(s)...')
    print(f'  Audience : {args.audience}')
    print(f'  Offer    : {args.offer}')
    print(f'  Goal     : {args.goal}\n')

    try:
        generate_ads(
            platform=args.platform,
            audience=args.audience,
            offer=args.offer,
            goal=args.goal,
            count=args.count,
        )
        print('\nDone — run `python main.py review` to approve drafts.\n')
    except Exception as exc:
        print(f'\n✗ Generation failed: {exc}\n', file=sys.stderr)
        sys.exit(1)


def cmd_review(_args):
    from approval.approval_cli import run_approval_queue
    run_approval_queue()


def cmd_publish(_args):
    from publisher.publisher import publish_approved
    publish_approved()


def cmd_images(args):
    from images.image_generator import generate_images

    ad_ids = None
    if args.ids:
        ad_ids = [int(i) for i in args.ids.split(',')]

    generate_images(ad_ids=ad_ids)


def cmd_preview(args):
    from db.database import get_ads_by_status
    from publisher.page_poster import _build_hashtags
    import os

    ads = get_ads_by_status('approved')
    ad_ids = [int(i) for i in args.ids.split(',')] if args.ids else None
    if ad_ids:
        ads = [a for a in ads if a['id'] in ad_ids]

    # Also include live ads if specific IDs requested
    if not ads and ad_ids:
        import sqlite3
        conn = sqlite3.connect('data/ads.db')
        conn.row_factory = sqlite3.Row
        placeholders = ','.join('?' * len(ad_ids))
        ads = [dict(r) for r in conn.execute(f'SELECT * FROM ads WHERE id IN ({placeholders})', ad_ids)]
        conn.close()

    if not ads:
        print('\nNo ads found.\n')
        return

    LINE = '─' * 60
    for ad in ads:
        hashtags = _build_hashtags(ad.get('audience', ''))
        message = f"{ad['headline']}\n\n{ad['body_copy']}\n\n{ad['cta']} -> https://strongtowerai.com\n\n{hashtags}"
        image_path = ad.get('image_path', '')

        print(f'\n{LINE}')
        print(f'Ad {ad["id"]} [{ad["platform"].upper()}] — copy and paste below')
        print(LINE)
        print(message)
        print(LINE)
        if image_path and os.path.exists(image_path):
            print(f'IMAGE: {image_path}')
        else:
            print('IMAGE: not yet generated — run `python main.py images`')
        print()


def cmd_post(args):
    from publisher.page_poster import post_approved_ads

    ad_ids = None
    if args.ids:
        ad_ids = [int(i) for i in args.ids.split(',')]

    post_approved_ads(ad_ids=ad_ids)


def cmd_monitor(_args):
    from monitor.performance_monitor import run_monitor
    run_monitor()


def cmd_status(_args):
    from db.database import get_status_counts

    rows = get_status_counts()
    if not rows:
        print('\nNo ads in the database yet.\n')
        return

    print('\nAd Queue Status')
    print('─' * 30)
    total = 0
    for r in rows:
        print(f'  {r["status"]:20} {r["count"]}')
        total += r['count']
    print('─' * 30)
    print(f'  {"TOTAL":20} {total}\n')


# ── CLI definition ────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='ad-agent',
        description='Strong Tower AI — Ad Content Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''\
examples:
  python main.py generate --platform meta --audience "real estate agents" \\
      --offer "free AI workflow audit" --count 3
  python main.py review
  python main.py publish
  python main.py monitor
  python main.py status
''',
    )
    sub = parser.add_subparsers(dest='command', required=True)

    # generate
    gen = sub.add_parser('generate', help='Generate new ad drafts via Claude')
    gen.add_argument('--platform', choices=['meta', 'google', 'linkedin'], required=True,
                     help='Ad platform')
    gen.add_argument('--audience', required=True,
                     help='Target audience description')
    gen.add_argument('--offer', required=True,
                     help='Offer or hook (e.g. "free AI audit")')
    gen.add_argument('--goal', default='lead generation',
                     help='Campaign goal (default: lead generation)')
    gen.add_argument('--count', type=int, default=3, metavar='N',
                     help='Number of variants to generate (default: 3)')
    gen.set_defaults(func=cmd_generate)

    # review
    rev = sub.add_parser('review', help='Approve / reject / edit drafts in the CLI')
    rev.set_defaults(func=cmd_review)

    # publish
    pub = sub.add_parser('publish', help='Publish approved ads (Meta API or manual guide)')
    pub.set_defaults(func=cmd_publish)

    # images
    img = sub.add_parser('images', help='Generate DALL-E 3 images for approved ads')
    img.add_argument('--ids', default=None, metavar='1,2,3',
                     help='Comma-separated ad IDs to target (default: all approved without images)')
    img.set_defaults(func=cmd_images)

    # preview
    prev = sub.add_parser('preview', help='Print formatted post ready to copy-paste into Facebook')
    prev.add_argument('--ids', default=None, metavar='1,2,3',
                      help='Comma-separated ad IDs to preview (default: all approved)')
    prev.set_defaults(func=cmd_preview)

    # post
    post = sub.add_parser('post', help='Post approved ads to Facebook page (organic)')
    post.add_argument('--ids', default=None, metavar='1,2,3',
                      help='Comma-separated ad IDs to post (default: all approved)')
    post.set_defaults(func=cmd_post)

    # monitor
    mon = sub.add_parser('monitor', help='Pull performance metrics for live ads')
    mon.set_defaults(func=cmd_monitor)

    # status
    stat = sub.add_parser('status', help='Show queue status summary')
    stat.set_defaults(func=cmd_status)

    return parser


def main():
    init_db()
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
