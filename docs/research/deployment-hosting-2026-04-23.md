# Deployment Hosting Research

Date: 2026-04-23 10-33-27
Prepared by: GitHub Copilot (GPT-5.3-Codex)
Purpose: Evaluate hosting options for the command-center service and answer Mac mini and domain strategy questions.

## Hosting Purpose Reminder

The project needs hosting that supports:

- Public HTTPS webhook endpoint for WhatsApp callbacks.
- Always-on FastAPI runtime.
- Persistent storage for `library/` and `data/`.
- Secure environment variable management.
- Low-operations maintenance with predictable costs.

## Hosting Recommendations (20)

| # | Host | Category | Pros | Cons |
|---|---|---|---|---|
| 1 | Railway | best value for money | Very fast setup and deploy flow | Cost can increase with sustained scale |
| 2 | Fly.io | best value for money | Docker-native, global deployment options | Volume planning requires care |
| 3 | Render | low budget | Simple managed deployment | Lower-tier limitations and potential cold starts |
| 4 | Koyeb | low budget | Easy container deployment | Smaller ecosystem than major clouds |
| 5 | Northflank | best value for money | Strong container workflow and service controls | Pricing model can be less intuitive |
| 6 | DigitalOcean App Platform | best value for money | Good managed DX and straightforward setup | More expensive than raw VPS at scale |
| 7 | DigitalOcean Droplet | low budget | Full control and stable cost | You own ops and security hardening |
| 8 | Hetzner Cloud VPS | low budget | Strong price/performance | Requires manual DevOps |
| 9 | Vultr VPS | low budget | Global regions, simple pricing | Manual ops burden |
| 10 | Linode VPS | low budget | Solid docs and support | Manual operations overhead |
| 11 | AWS Lightsail | low budget | Easy AWS entry point | Less flexible than full AWS services |
| 12 | AWS ECS/Fargate | pricy | Highly scalable enterprise option | Complex and higher-cost setup |
| 13 | AWS App Runner | best value for money | Managed container runtime | Less granular control than ECS |
| 14 | Google Cloud Run | best value for money | Excellent container platform and scalability | Stateful file persistence needs design |
| 15 | Azure Container Apps | pricy | Strong enterprise integration | Higher operational complexity |
| 16 | Oracle Cloud Free Tier | free | Potentially useful free compute baseline | Region and capacity availability vary |
| 17 | Heroku | best value for money | Smooth deploy workflow | Usually higher cost than VPS |
| 18 | Scalingo | low budget | Straightforward PaaS flow | Smaller ecosystem |
| 19 | Back4App Containers | low budget | Easy to start | Fewer advanced controls |
| 20 | Platform.sh | pricy | Enterprise-grade workflows | Higher cost and complexity |

## Budget Categorization

### free

- Oracle Cloud Free Tier (availability dependent)

### low budget

- Render
- Koyeb
- DigitalOcean Droplet
- Hetzner Cloud VPS
- Vultr VPS
- Linode VPS
- AWS Lightsail
- Scalingo
- Back4App Containers

### best value for money

- Railway
- Fly.io
- Northflank
- DigitalOcean App Platform
- AWS App Runner
- Google Cloud Run
- Heroku

### pricy

- AWS ECS/Fargate
- Azure Container Apps
- Platform.sh

## Most Suitable For Current Work

Top options for this repo's current maturity and constraints:

1. Railway: fastest path to stable public webhook with low setup friction.
2. Fly.io: strong Docker alignment and reliability for production webhook use.
3. Hetzner VPS: best direct cost control if manual ops is acceptable.

## Setup Instructions (Top Options)

### Railway

1. Push repository to GitHub.
2. Create a new Railway project from repository.
3. Set runtime command for the FastAPI app.
4. Add required environment variables from local `.env` (never commit secrets).
5. Configure persistence strategy for `library/` and `data/`.
6. Deploy and obtain HTTPS URL.
7. Register WhatsApp webhook callback URL with provider.
8. Run health and smoke checks.

### Fly.io

1. Install Fly CLI and authenticate.
2. Run `fly launch` from repository root.
3. Verify Dockerfile-based build settings.
4. Create and attach persistent volume for runtime data paths.
5. Configure secrets with Fly secrets management.
6. Deploy with `fly deploy`.
7. Validate HTTPS endpoint and webhook verification flow.
8. Run integration checks and confirm persistence after restart.

## Detailed Deep Dive: Railway vs Fly.io

This section is optimized for immediate decision-making for today's hosting setup.

### Railway (Detailed)

Best when you want the fastest time-to-production with minimal platform operations work.

#### Recommended architecture on Railway

- 1 web service running FastAPI from Dockerfile.
- Persistent storage strategy for runtime state:
  - Preferred: externalize critical state (for long-term) where possible.
  - Transitional: keep mounted runtime paths for `library/` and `data/` if supported by your chosen plan/runtime mode.
- Environment variables in Railway variable store.

#### Step-by-step setup detail

1. Connect GitHub repo and create project from repository.
2. Confirm build source is Dockerfile.
3. Set app start command if Railway does not auto-detect correctly.
4. Configure all required env vars from `.env`.
5. Set region closest to WhatsApp callback geography if available.
6. Deploy and capture generated HTTPS URL.
7. Run health check and smoke tests.
8. Register webhook callback URL in Meta app dashboard.
9. Trigger a test message and confirm inbound/outbound flow.
10. Add usage/billing alert thresholds.

#### Operational notes for this project

- Excellent for quick deployment iteration.
- Simplifies HTTPS and endpoint exposure.
- Watch for cost growth if sustained workloads and logs increase.

### Fly.io (Detailed)

Best when you want Docker-native control with stronger control over region and runtime shape.

#### Recommended architecture on Fly.io

- 1 app with single machine initially.
- Persistent volume attached in app region for `library/` and `data/`.
- Secrets managed via Fly secrets.
- Optional second machine/region after stability verification.

#### Step-by-step setup detail

1. Install Fly CLI and run `fly auth login`.
2. Run `fly launch` in repo root and keep Dockerfile flow.
3. Set internal port in Fly config to match app runtime.
4. Create volume in chosen primary region.
5. Mount volume for runtime data paths.
6. Set env secrets with `fly secrets set`.
7. Deploy with `fly deploy`.
8. Run `fly status` and `fly logs` for readiness checks.
9. Validate public HTTPS endpoint and webhook verification.
10. Configure machine auto-start/stop policy according to uptime needs.

#### Operational notes for this project

- Strong fit for container-first workflows.
- Good regional control and reliable HTTPS edge routing.
- Storage and region planning must be done carefully from day one.

## Railway vs Fly.io Comparison

| Dimension | Railway | Fly.io | Better fit for this project now |
|---|---|---|---|
| Time to first deploy | Very fast | Fast | Railway |
| Docker control depth | Medium | High | Fly.io |
| Persistent storage handling | Simpler at starter level but plan-sensitive | Explicit volume model, predictable once configured | Fly.io |
| Operational complexity | Lower | Medium | Railway |
| Debuggability (platform tooling) | Good | Very good (`fly status/logs/ssh`) | Fly.io |
| Cost predictability at small scale | Good | Good | Tie |
| Cost risk at growth | Can rise with usage patterns | Can rise with machine/volume scaling | Tie |
| Region and placement control | Moderate | Strong | Fly.io |
| Best for non-ops-heavy owner workflow | Strong | Medium | Railway |
| Best for long-term infra control | Medium | Strong | Fly.io |

## Decision Guidance For Today

Choose Railway today if your top priority is speed and low setup friction.

Choose Fly.io today if your top priority is container/runtime control and explicit storage architecture.

### Practical recommendation for your current phase

1. Launch first production webhook on Railway for fastest validation.
2. Keep Fly.io as your hardening/scale path once message flow stabilizes.
3. Use one stable domain/subdomain in front of whichever host you run to reduce migration friction.

## What to verify immediately after deployment

1. `/docs` endpoint returns 200.
2. Health command reports required integration keys as ready.
3. Webhook verification succeeds in Meta dashboard.
4. Inbound test message reaches router and returns expected response.
5. Reminder persistence survives one container restart.

### Hetzner VPS

1. Provision Ubuntu VPS instance.
2. Install Docker and Docker Compose.
3. Clone repository on VPS.
4. Create `.env` on server with required secrets.
5. Run container with mounted volumes for `library/` and `data/`.
6. Configure reverse proxy (Caddy or Nginx) with TLS.
7. Point domain/subdomain DNS to VPS.
8. Register webhook endpoint URL and test end-to-end.
9. Configure backups and restart policies.

## Mac mini M4 As Host

Question: Can this project run on Mac mini M4 hosting?

Short answer: Yes, technically viable for development and light production if your network setup is stable.

### Pros

- You control hardware directly with no monthly compute rent.
- Strong local performance for builds/tests and optional local AI workloads.
- Immediate access for debugging and iteration.

### Cons

- Home/office internet reliability and power outages can impact webhook uptime.
- Requires port forwarding, dynamic DNS or static IP, TLS setup, and router/firewall hardening.
- Less resilient than managed cloud for 24/7 production SLA.

### Practical Recommendation

- Use Mac mini M4 for local development, pre-production, and optional backup-host experiments.
- Use managed cloud host for primary production webhook reliability.

## Railway Acceptable Use Policy Compliance Check

Last reviewed: 2026-04-23 10-47-47 (source: railway.com/legal/acceptable-use)

### Relevant policy clause

> "running bots or scrapers that violate applicable terms of service"
> "send unsolicited bulk messages through any communication channel"
> "gain unauthorized access to systems or data, distribute malware, operate attack infrastructure"

The term "mirrors/userbots" does not appear verbatim in Railway's current policy. The bot
restriction only applies to bots that violate another service's terms or scrape at scale.

### Project compliance assessment

| Dimension | This project | Risk |
|---|---|---|
| Uses official Meta WhatsApp Cloud API (webhook-based) | Yes | None |
| Runs as a persistent always-on process | Yes — FastAPI webhook | None — this is normal Railway usage |
| Is it a userbot? | No — uses official business-number API, not a hijacked user account | None |
| Scrapes any service | No — reads Gmail/Drive via approved OAuth, Notion via API token | None |
| Sends unsolicited bulk messages | No — only responds to owner's own messages | None |
| Self-contained personal automation for a single owner | Yes | Clearly allowed |

### What "userbot" means in policy context

A userbot logs into WhatsApp (or Telegram, Discord, etc.) **as a human user account** using
reverse-engineered unofficial clients. These are prohibited because they violate Meta/WhatsApp user
ToS and scrape data outside the official API path.

This project uses the Meta Cloud API with a registered business number and an approved webhook
flow. This is the official API Meta provides for automation. It is not a userbot.

### Verdict

**This project does not conflict with Railway's Acceptable Use Policy.**

One ongoing obligation: ensure Gmail OAuth only requests `gmail.readonly` scope and never
requests write permissions beyond what is explicitly needed. This keeps the project compliant
with both Railway's policies and Gmail's OAuth scope requirements.

## Domain Name Consideration

Question: Is domain setup needed?

Short answer: Not strictly required if provider gives HTTPS URL, but strongly recommended for long-term operations.

### When a domain is not required

- Early-stage validation where platform URL is acceptable.
- Internal testing with temporary endpoints.

### Pros of using a domain now

- Stable endpoint identity independent of hosting provider migration.
- Professional trust and cleaner webhook/admin references.
- Easier future routing, blue/green migrations, and subservice organization.

### Cons of using a domain now

- Extra annual cost and DNS management overhead.
- Additional setup for certificate and DNS records.

### Recommendation for future work

- Register a domain early and use a dedicated subdomain for webhook traffic.
- Keep DNS TTL moderate during migration periods.
- Abstract endpoint naming so host provider can change without WhatsApp URL churn.
