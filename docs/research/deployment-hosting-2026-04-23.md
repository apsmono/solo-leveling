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
