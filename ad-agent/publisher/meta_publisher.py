import os
import requests

from db.database import update_ad_status

META_API_BASE = 'https://graph.facebook.com/v19.0'


def _creds() -> dict:
    return {
        'access_token': os.environ.get('META_ACCESS_TOKEN', ''),
        'ad_account_id': os.environ.get('META_AD_ACCOUNT_ID', ''),
        'page_id': os.environ.get('META_PAGE_ID', ''),
    }


def credentials_available() -> bool:
    c = _creds()
    return all([c['access_token'], c['ad_account_id'], c['page_id']])


def _post(path: str, payload: dict) -> dict:
    resp = requests.post(f'{META_API_BASE}{path}', json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if 'error' in data:
        raise RuntimeError(data['error'].get('message', str(data['error'])))
    return data


def publish_ad(ad: dict) -> str:
    """Create a paused Meta ad from an approved ad record. Returns platform ad ID."""
    creds = _creds()
    account = f"/act_{creds['ad_account_id']}"

    # 1. Campaign
    campaign = _post(f'{account}/campaigns', {
        'name': ad['campaign_name'],
        'objective': 'LEAD_GENERATION',
        'status': 'PAUSED',
        'special_ad_categories': [],
        'access_token': creds['access_token'],
    })
    campaign_id = campaign['id']

    # 2. Ad Set
    ad_set = _post(f'{account}/adsets', {
        'name': f"{ad['campaign_name']} — Ad Set",
        'campaign_id': campaign_id,
        'billing_event': 'IMPRESSIONS',
        'optimization_goal': 'LEAD_GENERATION',
        'bid_amount': 200,      # $2.00 in cents
        'daily_budget': 1000,   # $10.00 in cents
        'targeting': {
            'geo_locations': {'countries': ['US']},
            'age_min': 25,
            'age_max': 65,
        },
        'status': 'PAUSED',
        'access_token': creds['access_token'],
    })
    ad_set_id = ad_set['id']

    # 3. Creative
    creative = _post(f'{account}/adcreatives', {
        'name': ad['headline'],
        'object_story_spec': {
            'page_id': creds['page_id'],
            'link_data': {
                'message': ad['body_copy'],
                'link': 'https://strongtowerai.com',
                'name': ad['headline'],
                'call_to_action': {
                    'type': 'LEARN_MORE',
                    'value': {'link': 'https://strongtowerai.com'},
                },
            },
        },
        'access_token': creds['access_token'],
    })
    creative_id = creative['id']

    # 4. Ad
    result = _post(f'{account}/ads', {
        'name': ad['headline'],
        'adset_id': ad_set_id,
        'creative': {'creative_id': creative_id},
        'status': 'PAUSED',
        'access_token': creds['access_token'],
    })
    platform_ad_id = result['id']

    update_ad_status(
        ad['id'],
        'live',
        platform_campaign_id=campaign_id,
        platform_ad_id=platform_ad_id,
    )
    return platform_ad_id
