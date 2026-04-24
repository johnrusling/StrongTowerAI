_GUIDES = {
    'google': """\
GOOGLE ADS — MANUAL UPLOAD GUIDE
──────────────────────────────────────────────────────────────
1. Go to https://ads.google.com and sign in.
2. Click "+ New campaign" → choose goal: Leads (or Website traffic).
3. Campaign type: Search.
4. Set daily budget and bidding strategy (Target CPA recommended).
5. Create an Ad Group and add your target keywords.
6. Create a Responsive Search Ad:
     • Add 3–15 headlines (≤ 30 chars each)
     • Add 2–4 descriptions (≤ 90 chars each)
     • Final URL: https://strongtowerai.com
7. Add ad extensions: sitelinks, callouts, call extension.
8. Save and review in "Drafts" before enabling.

AD CONTENT TO UPLOAD:
{ad_content}
""",
    'linkedin': """\
LINKEDIN ADS — MANUAL UPLOAD GUIDE
──────────────────────────────────────────────────────────────
1. Go to https://www.linkedin.com/campaignmanager.
2. Select your ad account → click "+ Create" → Campaign.
3. Objective: Lead generation or Website visits.
4. Set audience: job titles, industries, company size, seniority.
5. Ad format: Single Image Ad.
6. Click "+ Create new ad":
     • Introductory text (body copy)
     • Headline
     • Call-to-action button
     • Destination URL: https://strongtowerai.com
7. Image: 1200×627 px, JPG/PNG, < 5 MB.
8. Save → set bid → launch.

AD CONTENT TO UPLOAD:
{ad_content}
""",
    'meta': """\
META ADS — MANUAL UPLOAD GUIDE
──────────────────────────────────────────────────────────────
1. Go to https://business.facebook.com/adsmanager.
2. Click "+ Create" → choose objective: Leads.
3. Set audience, placements (Facebook + Instagram), and budget.
4. Ad format: Single Image or Single Video.
5. In the ad creative:
     • Primary text (body copy)
     • Headline
     • Call-to-action button
     • Destination URL: https://strongtowerai.com
6. Image: 1080×1080 px (square) or 1200×628 px (landscape).
7. Preview and publish (start paused, review before enabling).

AD CONTENT TO UPLOAD:
{ad_content}
""",
}


def print_manual_guide(platform: str, ad: dict):
    guide = _GUIDES.get(platform.lower())
    if not guide:
        print(f'  [No manual guide available for {platform}]')
        return

    image_line = ''
    if ad.get('image_path'):
        image_line = f'\n  Image    : {ad["image_path"]}'
    else:
        image_line = '\n  Image    : ⚠  Not generated yet — run `python main.py images`'

    ad_content = (
        f'  Headline : {ad["headline"]}\n'
        f'  Body Copy: {ad["body_copy"]}\n'
        f'  CTA      : {ad["cta"]}\n'
        f'  Creative : {ad["creative_notes"]}'
        f'{image_line}'
    )
    print(guide.format(ad_content=ad_content))
