# Strong Tower AI — Ad Agent

## What This Is
A CLI tool that generates ad copy (Claude), ad images (DALL-E 3), and posts them to the Strong Tower AI Facebook page. It targets small/mid-size businesses across home services, real estate, professional services, and healthcare.

## Automatic Setup (run this when opening the project on a new machine)

When a user opens this project for the first time, do the following automatically without being asked:

1. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

2. **Create the .env file** from the example if it doesn't already exist:
   ```
   copy .env.example .env   (Windows)
   cp .env.example .env     (Mac/Linux)
   ```

3. **Check which keys are missing** by reading `.env` and tell the user exactly which ones need to be filled in:
   - `CLAUDE_API_KEY` — from console.anthropic.com
   - `OPENAI_API_KEY` — from platform.openai.com/api-keys
   - `META_APP_ID` — 2038262460907616
   - `META_APP_SECRET` — ask user to retrieve from developers.facebook.com → Strong Tower AI Publisher → App Settings → Basic
   - `META_ACCESS_TOKEN` — from Graph API Explorer (expires, must be regenerated periodically)
   - `META_PAGE_ID` — 996560726884021

4. **Initialize the database** by running:
   ```
   python -c "from db.database import init_db; init_db()"
   ```

5. **Confirm setup** by running `python main.py status` and showing the result.

## API Keys — Where to Get Them

| Key | Where |
|-----|-------|
| `CLAUDE_API_KEY` | console.anthropic.com → API Keys |
| `OPENAI_API_KEY` | platform.openai.com/api-keys |
| `META_APP_ID` | Already known: 2038262460907616 |
| `META_APP_SECRET` | developers.facebook.com → Strong Tower AI Publisher → App Settings → Basic |
| `META_ACCESS_TOKEN` | developers.facebook.com/tools/explorer → Strong Tower AI Publisher → Get Token → Get Page Access Token. Requires permissions: pages_manage_posts, pages_read_engagement, pages_show_list, pages_manage_ads |
| `META_PAGE_ID` | Already known: 996560726884021 |

**Note:** The Meta Access Token expires periodically. When posting fails with an auth error, regenerate it at the Graph API Explorer using the steps above.

## Daily Workflow

```
# Generate new ad drafts
python main.py generate --platform meta --audience "Home Services businesses — plumbers, HVAC, appliance repair" --offer "free 15-minute AI strategy call" --count 3

# Review and approve/reject drafts
python main.py review

# Generate images for approved ads
python main.py images

# Preview formatted post (copy-paste into Facebook manually)
python main.py preview

# Post directly via API (requires Meta app to be published)
python main.py post

# Check queue status
python main.py status
```

## Platform Audiences
Use these audience strings for consistent targeting:
- `"Home Services businesses — plumbers, HVAC, appliance repair, electricians, landscapers"`
- `"Real Estate agents, brokers, and property managers"`
- `"Professional Services — lawyers, consultants, accountants, financial advisors"`
- `"Healthcare — private practices, clinics, med spas, therapists"`
- `"Retail and E-commerce — local retailers, online store owners"`

## Project Structure
```
ad-agent/
  main.py                    — CLI entry point (generate, review, images, preview, post, monitor, status)
  generator/content_generator.py  — Claude API, generates ad copy
  images/image_generator.py  — DALL-E 3 image generation
  approval/approval_cli.py   — Interactive review queue
  publisher/page_poster.py   — Facebook page posting (organic)
  publisher/meta_publisher.py — Meta Marketing API (paid ads, requires published app)
  monitor/performance_monitor.py — Pulls Meta ad metrics
  db/database.py             — SQLite, all ad state
  data/ads.db                — Database (not in git, created on first run)
  data/images/               — Generated images (not in git, regenerate with `python main.py images`)
```

## Important Notes
- The Meta app (Strong Tower AI Publisher) is currently in **development mode** — API posts are only visible to app admins. Use `python main.py preview` to copy-paste posts manually until the app is reviewed and published by Meta.
- Never commit `.env` — it contains API keys.
- The `data/` folder is gitignored — database and images are local only.
- Strong Tower AI sells **website chatbots and digital automation**, NOT phone answering services. The system prompt in `content_generator.py` enforces this.
