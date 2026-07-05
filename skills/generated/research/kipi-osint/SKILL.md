---
name: kipi-osint
description: kipi AI entity graph investigator for OSINT, vendor vetting, and competitive intelligence
owners: [RAPHAEL]
tags: [research, osint, competitive-intel, entity-graph]
version: 1.0.0
created: 2026-07-03
---

# kipi OSINT Tool

## Overview
**kipi** (released June 10, 2026) is an AI entity graph investigator that builds knowledge graphs from PDFs, screenshots, WHOIS/DNS records, and breach intelligence. Used by RAPHAEL for deep-dive research on people, businesses, and entities.

## Use Cases for The Great Sage
1. **Vet DFY clients** — research potential Done-For-You AI service buyers before onboarding
2. **Competitive intel** — map other Tucson tattoo studios (owners, social reach, booking systems)
3. **Collaborator vetting** — verify artists, vendors, or event partners before agreements
4. **Brand monitoring** — detect mentions and connections to The Great Sage online

## Access Method
kipi is web-based. Use the **web_search + web_extract** workflow:

```
1. web_search("kipi entity graph [target name/business]")
2. web_search("[target] WHOIS site:whois.domaintools.com")
3. web_extract([target website, LinkedIn, social profiles])
4. Synthesize: connections → entity graph → report
```

## RAPHAEL OSINT Workflow

### Step 1 — Define Target
```
Target: [Person Name / Business Name / Domain]
Objective: [vet client | competitive intel | collaborator check]
```

### Step 2 — Data Collection
```python
sources = [
    web_search(f"{target} owner founder"),
    web_search(f"{target} reviews complaints"),
    web_search(f"{target} social media following"),
    web_search(f"site:instagram.com {target}"),
    web_extract([target_website]),
]
```

### Step 3 — Entity Graph Mapping
Map connections:
- **Identity**: Name, aliases, associated businesses
- **Digital footprint**: Websites, socials, email domains
- **Reputation**: Reviews, complaints, news mentions
- **Network**: Partners, employees, associates

### Step 4 — Report
```markdown
## OSINT Report: [Target]
Date: [date]
Requested by: Angel / JARVIS

### Summary
[2-3 sentence verdict]

### Entity Graph
- Business: ...
- Owner: ...
- Socials: ...
- Reputation signals: ...
- Risk flags: ...

### Recommendation
[PROCEED / PROCEED WITH CAUTION / DO NOT ENGAGE]
```

## Activation Triggers
- "research [person/business]"
- "vet this client"
- "competitive intel on"
- "OSINT on"
- "who is [name]"
- "check out [business]"

## Companion Tools
- **OpenOSINT v2.22.0** — 18-tool suite
- **osint-mcp** — 29-tool suite
- Standard: web_search + web_extract + session_search
