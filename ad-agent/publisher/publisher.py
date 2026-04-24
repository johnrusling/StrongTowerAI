from db.database import get_ads_by_status
from publisher.meta_publisher import credentials_available as meta_ready, publish_ad as meta_publish
from publisher.manual_guides import print_manual_guide

_LINE = '─' * 62


def publish_approved():
    ads = get_ads_by_status('approved')

    if not ads:
        print('\nNo approved ads to publish.\n')
        return

    print(f'\nPublishing {len(ads)} approved ad(s)...\n')
    published = manual = failed = 0

    for ad in ads:
        platform = ad['platform'].lower()
        label = f'[{platform.upper()}]'
        headline_short = (ad['headline'] or '')[:55]
        print(f'{label} "{headline_short}"')

        if platform == 'meta':
            if meta_ready():
                try:
                    ad_id = meta_publish(ad)
                    print(f'  ✓ Published (Meta ad ID: {ad_id}) — status: PAUSED\n')
                    published += 1
                except Exception as exc:
                    print(f'  ✗ Meta API error: {exc}')
                    print('  Falling back to manual upload guide:\n')
                    print_manual_guide('meta', ad)
                    failed += 1
            else:
                print('  Meta credentials not configured — manual upload required:\n')
                print_manual_guide('meta', ad)
                manual += 1
        else:
            print(f'  {platform.upper()} API not integrated yet — manual upload required:\n')
            print_manual_guide(platform, ad)
            manual += 1

    print(_LINE)
    print(f'  Result: {published} published · {manual} manual guide printed · {failed} failed')
    print(f'{_LINE}\n')
