import os
import requests

from db.database import get_ads_by_status, update_ad_status

META_API_BASE = 'https://graph.facebook.com/v19.0'

_AUDIENCE_HASHTAGS = {
    'real estate':     ['#RealEstate', '#RealtorLife', '#RealEstateAgent'],
    'home services':   ['#HomeServices', '#Plumber', '#HVAC', '#Trades'],
    'plumber':         ['#HomeServices', '#Plumber', '#HVAC', '#Trades'],
    'hvac':            ['#HomeServices', '#Plumber', '#HVAC', '#Trades'],
    'lawyer':          ['#LawFirm', '#Attorney', '#LegalMarketing'],
    'legal':           ['#LawFirm', '#Attorney', '#LegalMarketing'],
    'accountant':      ['#Accounting', '#CPA', '#SmallBusinessFinance'],
    'consultant':      ['#Consulting', '#BusinessConsultant', '#B2B'],
    'healthcare':      ['#Healthcare', '#MedSpa', '#PrivatePractice'],
    'retail':          ['#Retail', '#SmallBusiness', '#Ecommerce'],
}

_BASE_HASHTAGS = ['#AIAutomation', '#SmallBusiness', '#StrongTowerAI']


def _build_hashtags(audience: str) -> str:
    audience_lower = (audience or '').lower()
    extras = []
    for keyword, tags in _AUDIENCE_HASHTAGS.items():
        if keyword in audience_lower:
            extras = tags
            break
    tags = extras + _BASE_HASHTAGS
    return ' '.join(tags)


def post_to_page(ad: dict) -> str:
    """Post ad copy to Facebook page. Attaches image if available. Returns post ID."""
    access_token = os.environ.get('META_ACCESS_TOKEN')
    page_id = os.environ.get('META_PAGE_ID')

    if not access_token or not page_id:
        raise EnvironmentError('META_ACCESS_TOKEN and META_PAGE_ID must be set in .env')

    hashtags = _build_hashtags(ad.get('audience', ''))
    message = f"{ad['headline']}\n\n{ad['body_copy']}\n\n{ad['cta']} -> https://strongtowerai.com\n\n{hashtags}"
    image_path = ad.get('image_path')

    if image_path and os.path.exists(image_path):
        # Step 1: upload image unpublished to get a photo ID
        with open(image_path, 'rb') as img_file:
            upload = requests.post(
                f'{META_API_BASE}/{page_id}/photos',
                data={
                    'published': 'false',
                    'access_token': access_token,
                },
                files={'source': img_file},
                timeout=60,
            )
        upload.raise_for_status()
        upload_data = upload.json()
        if 'error' in upload_data:
            raise RuntimeError(upload_data['error'].get('message', str(upload_data['error'])))
        photo_id = upload_data['id']

        # Step 2: create a feed post with the image attached
        resp = requests.post(
            f'{META_API_BASE}/{page_id}/feed',
            json={
                'message': message,
                'attached_media': [{'media_fbid': photo_id}],
                'published': True,
                'access_token': access_token,
            },
            timeout=30,
        )
    else:
        # Text-only post
        resp = requests.post(
            f'{META_API_BASE}/{page_id}/feed',
            json={
                'message': message,
                'published': True,
                'access_token': access_token,
            },
            timeout=30,
        )

    resp.raise_for_status()
    data = resp.json()
    if 'error' in data:
        raise RuntimeError(data['error'].get('message', str(data['error'])))

    post_id = data.get('id', data.get('post_id', ''))
    update_ad_status(ad['id'], 'live')
    return post_id


def post_approved_ads(ad_ids: list[int] | None = None):
    """Post approved ads to the Facebook page."""
    ads = get_ads_by_status('approved')
    if ad_ids:
        ads = [a for a in ads if a['id'] in ad_ids]

    if not ads:
        print('\nNo approved ads to post.\n')
        return

    print(f'\nPosting {len(ads)} ad(s) to Facebook page...\n')

    for ad in ads:
        headline = (ad['headline'] or '')[:55]
        has_image = bool(ad.get('image_path') and os.path.exists(ad.get('image_path', '')))
        print(f'  Ad {ad["id"]} — "{headline}" [{"with image" if has_image else "text only"}]')
        try:
            post_id = post_to_page(ad)
            print(f'  Posted (Post ID: {post_id})\n')
        except Exception as exc:
            print(f'  Failed: {exc}\n')
