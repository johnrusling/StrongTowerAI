from db.database import get_ads_by_status, update_ad_status

_LINE = '─' * 62
_DLINE = '═' * 62


def run_approval_queue():
    drafts = get_ads_by_status('draft')

    # Also surface edit-requested ads that have been regenerated
    edit_drafts = get_ads_by_status('edit_requested')
    all_pending = drafts + edit_drafts

    if not all_pending:
        print('\nNo ads pending review.\n')
        return

    print(f'\n{_DLINE}')
    print(f'  APPROVAL QUEUE — {len(all_pending)} ad(s) pending review')
    print(f'{_DLINE}\n')

    approved = rejected = edited = skipped = 0

    for i, ad in enumerate(all_pending, 1):
        label = 'RE-REVIEW' if ad['status'] == 'edit_requested' else 'NEW'
        print(f'[{i}/{len(all_pending)}] {label} · {ad["platform"].upper()} · {ad["campaign_name"]}')
        print(_LINE)
        print(f'  HEADLINE : {ad["headline"]}')
        print(f'  COPY     : {ad["body_copy"]}')
        print(f'  CTA      : {ad["cta"]}')
        print(f'  CREATIVE : {ad["creative_notes"]}')
        print(f'  AUDIENCE : {ad["audience"]}')
        print(f'  GOAL     : {ad["goal"]}')
        if ad.get('edit_notes'):
            print(f'  (prev edit note: {ad["edit_notes"]})')
        print()

        while True:
            raw = input('  [A]pprove  [R]eject  [E]dit  [S]kip  → ').strip().upper()

            if raw == 'A':
                update_ad_status(ad['id'], 'approved')
                print('  ✓ Approved\n')
                approved += 1
                break
            elif raw == 'R':
                update_ad_status(ad['id'], 'rejected')
                print('  ✗ Rejected\n')
                rejected += 1
                break
            elif raw == 'E':
                note = input('  Edit note: ').strip()
                update_ad_status(ad['id'], 'edit_requested', edit_notes=note)
                print('  ↺ Queued for re-generation\n')
                edited += 1
                break
            elif raw == 'S':
                print('  → Skipped\n')
                skipped += 1
                break
            else:
                print('  Invalid — enter A, R, E, or S.')

    print(_DLINE)
    print(f'  Done: {approved} approved · {rejected} rejected · {edited} edit · {skipped} skipped')
    print(f'{_DLINE}\n')
