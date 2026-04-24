import json
import os
import re
import anthropic

from db.database import save_ads

# Cached system prompt — placed with cache_control so repeated calls hit the cache
SYSTEM_PROMPT = """You are an expert paid advertising copywriter for Strong Tower AI, an AI automation company that helps small and mid-sized businesses take advantage of the AI revolution — before their competitors do.

COMPANY:
Strong Tower AI makes AI automation simple, fast, and affordable for everyday businesses. No tech background needed. They handle the setup; the business owner just sees the results.

TARGET AUDIENCES (write for the specific audience given, calling out their world):
- Home Services: plumbers, HVAC technicians, appliance repair, electricians, landscapers
- Professional Services: lawyers, consultants, accountants, financial advisors
- Healthcare: private practices, clinics, med spas, therapists
- Retail / E-commerce: local retailers, online store owners
- Real Estate: agents, brokers, property managers

WHAT STRONG TOWER AI ACTUALLY SELLS:
- Website chatbots that capture leads and answer visitor questions 24/7
- Automated booking — website visitors can schedule a call or appointment without the owner doing anything
- Lead follow-up automation — no more leads going cold because nobody followed up
- Admin automation — quotes, confirmations, reminders, intake forms
Strong Tower AI is NOT a phone answering service. Never reference answering phone calls, call centers, or phone AI. The product lives on their website and in their digital workflow.

TONE & MESSAGING RULES:
- Lead with the AI revolution angle: competitors are already using AI — are they?
- Speak plain English. No jargon. These are busy, skeptical business owners, not tech people.
- Use "AI" in headlines — it hooks curiosity and signals opportunity, not threat.
- Body copy focuses on the website and digital side: "your website books jobs while you work", "online leads stop going cold", "visitors get answers instantly".
- Never oversell. One clear, believable claim beats three vague ones.
- The CTA is always to book a free 15-minute call. Make it feel low-commitment and easy.
- For home services: speak to the reality of being on a job site while online leads go unanswered, losing work to competitors whose websites respond instantly, spending evenings on follow-ups instead of family.

Always follow platform-specific character limits and best practices."""

PLATFORM_SPECS = {
    'meta': {
        'headline_limit': 40,
        'body_limit': 125,
        'description': 'Facebook/Instagram. Primary text ≤ 125 chars, headline ≤ 40 chars.',
    },
    'google': {
        'headline_limit': 30,
        'body_limit': 90,
        'description': 'Google Responsive Search Ad (RSA). Each headline ≤ 30 chars, each description ≤ 90 chars.',
    },
    'linkedin': {
        'headline_limit': 70,
        'body_limit': 600,
        'description': 'LinkedIn Sponsored Content. Intro text ≤ 600 chars, headline ≤ 70 chars.',
    },
}


def _strip_json_fences(text: str) -> str:
    """Remove markdown code fences if present."""
    text = text.strip()
    match = re.match(r'^```(?:json)?\s*([\s\S]*?)```$', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text


def generate_ads(
    platform: str,
    audience: str,
    offer: str,
    goal: str,
    count: int = 3,
) -> list[dict]:
    specs = PLATFORM_SPECS.get(platform, PLATFORM_SPECS['meta'])

    prompt = f"""Generate {count} distinct ad variations for this campaign brief:

Platform: {platform.upper()} — {specs['description']}
Target audience: {audience}
Offer: {offer}
Campaign goal: {goal}

Return a JSON array of exactly {count} objects, each with these fields:
  "headline"       — max {specs['headline_limit']} chars
  "body_copy"      — max {specs['body_limit']} chars
  "cta"            — call-to-action button text, max 20 chars
  "creative_notes" — image/video direction, 1–2 sentences

Output ONLY the JSON array, no other text."""

    api_key = os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('CLAUDE_API_KEY')
    if not api_key:
        raise EnvironmentError('Set ANTHROPIC_API_KEY or CLAUDE_API_KEY in ad-agent/.env')
    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=2048,
        system=[
            {
                'type': 'text',
                'text': SYSTEM_PROMPT,
                'cache_control': {'type': 'ephemeral'},
            }
        ],
        messages=[{'role': 'user', 'content': prompt}],
    )

    raw = response.content[0].text
    variants: list[dict] = json.loads(_strip_json_fences(raw))

    campaign_name = f"{audience[:40]} — {offer[:30]}"
    ads_to_save = [
        {
            'platform': platform,
            'campaign_name': campaign_name,
            'headline': v.get('headline', ''),
            'body_copy': v.get('body_copy', ''),
            'cta': v.get('cta', ''),
            'creative_notes': v.get('creative_notes', ''),
            'audience': audience,
            'offer': offer,
            'goal': goal,
        }
        for v in variants
    ]

    ids = save_ads(ads_to_save)
    cache_read = response.usage.cache_read_input_tokens or 0
    print(f"  Saved {len(ids)} {platform.upper()} drafts (IDs: {ids}) | cache_read={cache_read}")
    return ads_to_save
