import os
import re
import requests
import anthropic
from openai import OpenAI

from db.database import get_approved_without_images, save_image_path
from generator.content_generator import SYSTEM_PROMPT

# DALL-E 3 size per platform
_SIZES = {
    'meta': '1024x1024',       # square — works on Feed + Stories
    'google': '1792x1024',     # landscape — closest to 1200x628
    'linkedin': '1792x1024',   # landscape — closest to 1200x627
}

_IMAGES_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'images')

_PROMPT_REFINER = """You are a DALL-E 3 prompt engineer specializing in paid advertising imagery.

Given an ad's creative direction, headline, and platform, write a single optimized DALL-E 3 image generation prompt. The prompt must:
- Describe the scene, composition, lighting, and mood in concrete visual terms
- Avoid any text, logos, or UI elements in the image (those are added in post)
- Be appropriate for professional B2B advertising
- Fit the platform's aspect ratio expectations
- Be 2–4 sentences maximum

Output ONLY the prompt text, nothing else."""


def _build_dalle_prompt(ad: dict) -> str:
    """Use Claude to refine creative_notes into an optimized DALL-E 3 prompt."""
    api_key = os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('CLAUDE_API_KEY')
    if not api_key:
        raise EnvironmentError('Set ANTHROPIC_API_KEY or CLAUDE_API_KEY in ad-agent/.env')

    client = anthropic.Anthropic(api_key=api_key)

    user_msg = f"""Platform: {ad['platform'].upper()}
Headline: {ad['headline']}
Creative direction: {ad['creative_notes']}
Audience: {ad['audience']}

Write the DALL-E 3 prompt."""

    response = client.messages.create(
        model='claude-sonnet-4-6',
        max_tokens=256,
        system=[
            {
                'type': 'text',
                'text': _PROMPT_REFINER,
                'cache_control': {'type': 'ephemeral'},
            }
        ],
        messages=[{'role': 'user', 'content': user_msg}],
    )
    return response.content[0].text.strip()


def _safe_filename(ad: dict) -> str:
    slug = re.sub(r'[^a-z0-9]+', '-', (ad['headline'] or '').lower()).strip('-')[:40]
    return f"ad{ad['id']}_{ad['platform']}_{slug}.png"


def generate_images(ad_ids: list[int] | None = None):
    """Generate DALL-E 3 images for approved ads that don't have one yet.

    Pass ad_ids to target specific ads, or None to process all eligible.
    """
    openai_key = os.environ.get('OPENAI_API_KEY')
    if not openai_key:
        print('\n✗ OPENAI_API_KEY not set in ad-agent/.env')
        print('  Get a key at https://platform.openai.com/api-keys\n')
        return

    ads = get_approved_without_images()
    if ad_ids:
        ads = [a for a in ads if a['id'] in ad_ids]

    if not ads:
        print('\nNo approved ads need images.\n')
        return

    os.makedirs(_IMAGES_DIR, exist_ok=True)
    oai = OpenAI(api_key=openai_key)

    print(f'\nGenerating images for {len(ads)} ad(s)...\n')

    for ad in ads:
        headline_short = (ad['headline'] or '')[:50]
        print(f'  [{ad["platform"].upper()}] Ad {ad["id"]} — "{headline_short}"')

        try:
            # Step 1: Claude refines the creative brief into a DALL-E prompt
            print('    Refining prompt with Claude...', end=' ', flush=True)
            dalle_prompt = _build_dalle_prompt(ad)
            print('done')

            # Step 2: DALL-E 3 generates the image
            size = _SIZES.get(ad['platform'].lower(), '1024x1024')
            print(f'    Generating {size} image with DALL-E 3...', end=' ', flush=True)
            result = oai.images.generate(
                model='dall-e-3',
                prompt=dalle_prompt,
                size=size,
                quality='standard',
                n=1,
            )
            image_url = result.data[0].url

            # Step 3: Download and save locally
            img_bytes = requests.get(image_url, timeout=60).content
            filename = _safe_filename(ad)
            save_path = os.path.join(_IMAGES_DIR, filename)
            with open(save_path, 'wb') as f:
                f.write(img_bytes)

            save_image_path(ad['id'], save_path)
            print('done')
            print(f'    Saved → data/images/{filename}')

            # Show the refined prompt for reference
            print(f'    Prompt: "{dalle_prompt[:100]}{"..." if len(dalle_prompt) > 100 else ""}"\n')

        except Exception as exc:
            err_str = str(exc)
            if 'billing_hard_limit_reached' in err_str or 'insufficient_quota' in err_str:
                print('\n  ----------------------------------------')
                print('  OpenAI credit limit reached.')
                print('  Add credits at: https://platform.openai.com/settings/billing')
                print(f'  Remaining ads skipped — re-run `python main.py images` after topping up.')
                print('  ----------------------------------------\n')
                break
            print(f'\n    ✗ Failed: {exc}\n')

    print('Image generation complete.\n')
