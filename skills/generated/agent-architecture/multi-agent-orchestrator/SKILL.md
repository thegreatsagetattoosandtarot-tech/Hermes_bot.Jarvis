---
name: "multi-agent-orchestrator"
description: "NVIDIA NemoClaw integration for JARVIS OS Archangel fleet — sandboxed AI agents in OpenShell with routed inference, network policies, and Hermes support. Owner: MICHAEL (Chief of Staff)."
license: "Apache-2.0"
owner: "MICHAEL"
tags:
  - nemoclaw
  - nvidia
  - openshell
  - archangel
  - jarvis-os
  - hermes
  - multi-agent
---

# NemoClaw Multi-Agent Orchestrator — JARVIS OS Integration

## Interface Generation
When requested to build UI for the orchestrator, prefer interactive widgets with toggleable states (e.g. expanding agent cards that reveal deeper information like financial breakdowns, spreadsheets, task queues, or sprint boards). The interface should natively include a "live chat" capability to speak with sub-agents, and a central node for the orchestrator itself that can accept live audio commands and emit TTS responses in return.

**Owner:** MICHAEL (Chief of Staff)  
**Scope:** Archangel fleet sandbox orchestration, NVIDIA inference routing, OpenShell security isolation  
**Stack:** NemoClaw v0.1.0 · OpenShell ≥0.0.72 · Node.js 22.16+

---

## What NemoClaw Provides

NVIDIA NemoClaw is an open-source reference stack for running always-on AI agents **safely inside NVIDIA OpenShell sandboxes**. For the JARVIS OS Archangel fleet it delivers three core capabilities:

### 1. OpenShell Sandboxing
- Each agent runs in a hardened container sandbox with enforced **filesystem policies** (read-only `/usr`, `/lib`, `/etc`; read-write `/tmp`, `/sandbox/.nemoclaw`)
- **Landlock LSM** enforcement (best-effort compatibility mode)
- Docker capability drops and process limits prevent lateral movement between agents
- Sandbox lifecycle managed via `nemoclaw` CLI: create → migrate → snapshot → restore

### 2. Hermes Agent Support
- NemoClaw ships a dedicated **Hermes variant** (`NEMOCLAW_AGENT=hermes` or the `nemohermes` alias)
- Hermes-specific quickstart: `https://docs.nvidia.com/nemoclaw/latest/user-guide/hermes/home.md`
- The plugin registers `/nemoclaw` TUI slash commands inside the agent runtime
- Blueprint profiles available: `default`, `ncp`, `nim-local`, `vllm`, `routed`

### 3. Routed Inference
- **LLM Router** (Qwen3.5-0.8B prefill encoder) routes queries to the most cost-efficient model above an accuracy threshold
- Pool: Nemotron 3 Nano (reasoning, $0.05/M tokens) → Nemotron 3 Super 120B ($0.10/M tokens)
- Tolerance default: `0.20` (allows 20pp accuracy drop for cheaper model)
- Endpoint: `https://integrate.api.nvidia.com/v1`
- Config: `nemoclaw-blueprint/router/pool-config.yaml`

---

## Installation

### Prerequisites
- Node.js 22.16+
- Docker (for OpenShell sandbox)
- NVIDIA API key (`NVIDIA_API_KEY`)

### Install
```bash
# Global install
npm install -g nemoclaw

# Or run directly via npx
npx nemoclaw --help

# Hermes-specific alias (set agent variant)
NEMOCLAW_AGENT=hermes npx nemoclaw onboard
# OR use the dedicated alias after install:
nemohermes onboard
```

### Interactive Installer
```bash
# Full interactive setup (recommended for first run)
npx nemoclaw@latest
```

---

## JARVIS OS Archangel Fleet Integration

### Agent → Sandbox Policy Mapping

| Archangel Agent | Role | Sandbox Policy | Resource Profile |
|----------------|------|----------------|-----------------|
| **MICHAEL** | Chief of Staff / Orchestrator | `default` (balanced) | `developer` (75% CPU/RAM) |
| **RAPHAEL** | Research & Analysis | `default` + full egress | `developer` (75% CPU/RAM) |
| **GABRIEL** | Communications & Email | `shields-up` (restricted egress) | `creator` (50% CPU/RAM) |
| **REMIEL** | Social Media Manager | `shields-up` (restricted egress) | `creator` (50% CPU/RAM) |
| **URIEL** | Data Analyst / Financial | `default` + financial API egress | `developer` (75% CPU/RAM) |
| **BARACHIEL** | Sales & Business Dev | `shields-up` | `creator` (50% CPU/RAM) |
| **CHAMUEL** | Marketing & Brand | `shields-up` | `creator` (50% CPU/RAM) |
| **HANIEL** | Scheduler & Automation | `default` | `creator` (50% CPU/RAM) |
| **JOPHIEL** | Creative Director | `default` + media egress | `game-developer` (60% CPU/RAM) |
| **RAGUEL** | Customer Support | `shields-up` | `creator` (50% CPU/RAM) |
| **SARAQAEL** | CRM & Client Manager | `shields-up` | `creator` (50% CPU/RAM) |
| **ZADKIEL** | Knowledge Base & Docs | `default` | `creator` (50% CPU/RAM) |

### Policy Tiers

**`default`** (`nemoclaw-blueprint/policies/openclaw-sandbox.yaml`):
- Balanced egress, NVIDIA inference endpoints allowed
- Use for: research, data analysis, orchestration

**`shields-up`** (strict):
- Minimal egress; only approved endpoints
- Use for: customer-facing agents, email, social, CRM

**`shields-down`** (`nemoclaw-blueprint/policies/permissive.yaml`):
- All egress allowed — **development/testing ONLY**
- Never deploy to production

### Blueprint Configuration

```yaml
# nemoclaw-blueprint/blueprint.yaml (excerpt)
version: "0.1.0"
min_openshell_version: "0.0.72"

profiles:
  - default    # Standard NVIDIA inference
  - ncp        # NCP provider
  - nim-local  # Local NIM inference
  - vllm       # vLLM backend
  - routed     # LLM router (cost-optimized)

components:
  inference:
    profiles:
      default:
        provider_type: "nvidia"
        endpoint: "https://integrate.api.nvidia.com/v1"
        model: "nvidia/nemotron-3-super-120b-a12b"
```

---

## Key CLI Commands

```bash
# Onboard (first-time setup)
nemohermes onboard

# Create a sandbox for an Archangel agent
nemohermes sandbox create --name michael --profile developer

# Check sandbox status
nemohermes sandbox status

# Apply a network policy
nemohermes policy apply --file nemoclaw-blueprint/policies/openclaw-sandbox.yaml

# Switch to routed inference (cost-optimized)
nemohermes config set inference.profile routed

# Shields down (dev only!)
nemohermes policy shields-down

# Rebuild sandbox after config change
nemohermes sandbox rebuild

# View logs
nemohermes logs --follow
```

---

## Inference Routing for JARVIS Fleet

```yaml
# nemoclaw-blueprint/router/pool-config.yaml
routing:
  method: prefill
  checkpoint: llm-router/checkpoints/prefill_router_qwen08b.pt
  tolerance: 0.20   # Adjust: 0.0 = always best model, 1.0 = always cheapest

models:
  - name: nemotron-3-nano-reasoning    # Fast, cheap — simple tasks
    cost_per_m_input_tokens: 0.05
  - name: nemotron-3-super            # Powerful — complex reasoning
    cost_per_m_input_tokens: 0.10
```

**Recommended tolerance settings by agent:**
- MICHAEL (orchestration): `0.10` — accuracy-first
- RAPHAEL (research): `0.10` — accuracy-first
- GABRIEL, REMIEL, RAGUEL (comms): `0.25` — cost-balanced
- URIEL (financial): `0.05` — always best model
- HANIEL (scheduling): `0.30` — cost-optimized

---

## Security Controls

- **SSRF validation**: `nemoclaw/src/blueprint/ssrf.ts` blocks server-side request forgery
- **Credential sanitization**: secrets never leaked into sandbox or chat
- **Network egress control**: L7 proxy with TLS termination; all traffic routed through policy engine
- **Capability drops**: Docker `--cap-drop ALL` with selective re-adds
- **Process limits**: `ulimit` enforced per sandbox

**Best practice for JARVIS fleet:**
1. Set `NVIDIA_API_KEY` in Hermes secrets vault — never in plaintext config
2. Use `shields-up` for all customer-facing Archangel agents by default
3. Run `nemohermes policy shields-down` only in isolated dev/test environments
4. Monitor egress with `nemohermes logs --network`

---

## Documentation References

- Hermes quickstart: `https://docs.nvidia.com/nemoclaw/latest/user-guide/hermes/get-started/quickstart.md`
- Architecture: `https://docs.nvidia.com/nemoclaw/latest/about/how-it-works.md`
- Network policies: `https://docs.nvidia.com/nemoclaw/latest/reference/network-policies.md`
- Security best practices: `https://docs.nvidia.com/nemoclaw/latest/security/best-practices.md`
- CLI reference: `https://docs.nvidia.com/nemoclaw/latest/reference/commands.md`
- AI docs index: `https://docs.nvidia.com/nemoclaw/llms.txt`

---

## Pitfalls

- **Node.js version**: Must be 22.16+; run `npm run dev:doctor` to verify
- **Key permissions**: SSH/API keys must be `chmod 600`; NemoClaw checks at startup
- **Sandbox image pinning**: Blueprint uses digest-pinned images — bump both `digest:` and `components.sandbox.image` together on upgrades
- **`shields-down` in production**: Disables most security controls — always reapply `shields-up` after dev sessions
- **Memory path on VPS**: Ensure `/docker/hermes-agent-7t79/data/profiles/unrestricted/memory/` exists before syncing (mkdir -p first)
- **Concurrent sandboxes**: Each Archangel agent should have its own named sandbox; don't share sandbox instances across agents
