# Strong Tower AI — Ad Content Agent: Project Spec

## Overview

Build an AI-powered advertising agent for **Strong Tower AI**, an AI automation company that helps businesses in real estate, healthcare, law, e-commerce, and consulting automate time-consuming work and scale efficiently. The agent's job is to continuously create, queue, monitor, and improve paid ad content across **Meta (Facebook/Instagram)**, **Google Ads**, and **LinkedIn** — with a human-in-the-loop approval step before anything goes live.

---

## Business Context

**Company:** Strong Tower AI  
**Value prop:** Affordable AI automation for growing businesses — fast results, plain language, no enterprise pricing.  
**Target customers:** Business owners and operators in real estate, healthcare, law, e-commerce, and consulting who are losing time and leads to manual work.  
**Tone:** Direct, empathetic, results-oriented. Speak to the pain (evenings lost, leads dropped, weekends on admin) and offer a clear way out.

---

## Agent Goals

1. **Generate** ad copy, headlines, and creative briefs for Meta, Google, and LinkedIn
2. **Queue** content for human review before publishing
3. **Publish** approved content via platform APIs (or provide step-by-step manual upload instructions if API access isn't available)
4. **Monitor** live campaigns — CTR, impressions, conversions, cost-per-click
5. **Iterate** — flag underperformers, suggest improvements, A/B test variants

---

## Tech Stack (Recommended)

- **Runtime:** Node.js or Python (your preference; Python preferred for ML/analytics work)
- **Orchestration:** Claude API (claude-sonnet-4-20250514) for content generation and analysis
- **Database:** SQLite (local/simple) or Supabase (if you want a dashboard)
- **Queue/Approval UI:** Simple web UI (React or plain HTML) or CLI with approval prompts
- **Platform integrations:**
  - Meta Marketing API (Facebook/Instagram ads)
  - Google Ads API
  - LinkedIn Marketing API
- **Scheduler:** cron jobs or a task queue (e.g., BullMQ, APScheduler) for recurring content generation and performance checks
- **Storage:** Local file system or S3 for creative assets

---

## Core Modules to Build

### 1. Content Generator
- Takes a **campaign brief** as input (target audience, offer, platform, tone, goal)
- Calls Claude API to generate:
  - 3–5 headline variants
  - Primary ad copy (short and long form)
  - Call-to-action options
  - Creative direction notes (image/video suggestions)
  - Platform-specific formatting (Meta character limits, Google RSA format, LinkedIn sponsored content)
- Stores drafts in a local database with status: `draft`

### 2. Approval Queue
- Simple UI or CLI that presents each draft ad to the user
- User actions: `Approve`, `Reject`, `Request Edit`
- On approval, status changes to `approved` and is handed to the Publisher
- On "Request Edit," a note is passed back to the Content Generator for a revised version

### 3. Publisher
- Reads all `approved` content from the queue
- For each item, attempts to publish via the relevant platform API
- If API credentials are not yet configured, outputs a **step-by-step manual upload guide** for that platform
- Logs publish time, campaign ID, ad set ID, and platform reference
- Updates status to `live`

### 4. Performance Monitor
- Runs on a schedule (e.g., daily)
- Pulls metrics from each platform API:
  - Impressions, clicks, CTR, spend, conversions, CPC, ROAS
- Stores metrics in the database against each ad
- Flags ads that are underperforming vs. benchmarks (e.g., CTR < 1% for Meta, CTR < 2% for Google Search)

### 5. Optimization Engine
- Reviews performance data and calls Claude API to:
  - Diagnose why an ad is underperforming
  - Suggest revised copy, new headlines, or audience targeting changes
  - Generate A/B test variants for top performers
- Outputs new drafts back into the Content Generator queue

---

## Data Schema (Simplified)

```sql
-- ads table
id, platform, campaign_name, headline, body_copy, cta, creative_notes,
status (draft | approved | rejected | live | paused | archived),
created_at, approved_at, published_at, campaign_id, ad_id

-- performance table
id, ad_id, date, impressions, clicks, ctr, spend, conversions, cpc, roas

-- campaigns table
id, name, platform, objective, budget_daily, start_date, end_date, status
```

---

## Workflow (End-to-End)

```
1. User (or scheduler) triggers: "Generate 5 new Meta ads targeting real estate agents"
2. Content Generator calls Claude → produces drafts → saves to DB (status: draft)
3. Approval Queue surfaces drafts to user in UI/CLI
4. User approves/rejects each
5. Publisher picks up approved ads → pushes to Meta API → logs campaign/ad IDs
6. Monitor runs daily → pulls metrics → flags underperformers
7. Optimizer generates new variants → back to step 3
```

---

## Approval UI (Minimum Viable)

A simple web page or CLI that shows:
- Ad preview (headline + body + CTA + platform label)
- Approve / Reject / Edit buttons
- Approved count and queue depth

No need for anything fancy to start — a terminal prompt or a single-page HTML file is fine.

---

## Platform API Setup Notes

Each platform requires credentials. The agent should check for these at startup and guide the user through setup if missing:

- **Meta:** `APP_ID`, `APP_SECRET`, `ACCESS_TOKEN`, `AD_ACCOUNT_ID`
- **Google Ads:** `CLIENT_ID`, `CLIENT_SECRET`, `REFRESH_TOKEN`, `DEVELOPER_TOKEN`, `CUSTOMER_ID`
- **LinkedIn:** `CLIENT_ID`, `CLIENT_SECRET`, `ACCESS_TOKEN`, `AD_ACCOUNT_ID`

Store all credentials in a `.env` file. Never hardcode them.

---

## Phase 1 Deliverables (MVP)

- [ ] Content Generator (Claude API integration, 3 platforms)
- [ ] SQLite database with ads + campaigns schema
- [ ] CLI-based Approval Queue
- [ ] Publisher with Meta API integration (manual upload guides for Google + LinkedIn as fallback)
- [ ] Basic performance monitor (Meta Insights API)
- [ ] README with setup instructions and `.env` template

## Phase 2 (After MVP)

- [ ] Web UI for approval queue with ad preview cards
- [ ] Google Ads API publisher integration
- [ ] LinkedIn API publisher integration
- [ ] Optimization Engine with A/B variant generation
- [ ] Dashboard showing live campaign performance
- [ ] Automated weekly performance digest (email or Slack)

---

## Example Prompt to Kick Off Content Generation

When calling Claude to generate ads, use a system prompt like:

> You are an expert paid advertising copywriter for Strong Tower AI, an AI automation company. Strong Tower AI helps business owners in real estate, healthcare, law, e-commerce, and consulting automate time-consuming tasks so they can stop working evenings and weekends. The tone is direct, empathetic, and results-focused. Speak to real pain points — dropped leads, manual admin, wasted time — and offer a clear, affordable solution. Always follow platform-specific character limits and best practices.

---

## Success Metrics

- Time from brief → live ad: under 30 minutes
- Ad approval rate: track to improve generator quality over time
- CTR benchmarks: Meta ≥ 1%, Google Search ≥ 3%, LinkedIn ≥ 0.5%
- Monthly spend efficiency: ROAS improvement over rolling 30 days

---

*Generated for Strong Tower AI · April 2026*
