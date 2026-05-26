# The Olympics — MoG Model Selection Arena

**Live Scoreboard**: [slothitude.github.io/the-olympics](https://slothitude.github.io/the-olympics/)

## What is MoG?

**Mixture of Gods (MoG)** is a local LLM routing system. You see one assistant; under the hood, 12 specialist models handle what they're best at.

```
User Query → Hermes (router) → Classifies intent → Routes to specialist god → Response
```

No single model is best at everything. MoG lets each model play to its strengths.

## The Pantheon (12 Gods)

| God | Domain | Routes To |
|-----|--------|-----------|
| Zeus | Decisiveness, leadership | CEO rulings, conflict resolution |
| Athena | Deep analysis, strategy | Research, architecture, investigation |
| Hephaestus | Code, engineering | Implementation, building |
| Prometheus | Disruption, innovation | Creative alternatives, security auditing |
| Heracles | Debugging, troubleshooting | Bug fixes, obstacle clearing |
| Hermes | Speed, summaries | Quick answers, information retrieval |
| Aphrodite | Writing, creativity | Beautiful prose, emotional impact |
| Demeter | Teaching, clarity | Explanations, onboarding |
| Hecate | Security, patterns | Forensics, anomaly detection |
| Persephone | Synthesis, bridging | Compromise, integration |
| Hestia | Safety, reliability | Testing, hardening, validation |
| Dionysus | Creative chaos | Brainstorming, unconventional ideas |

## How It Works

### Architecture

```
Claude Code (Rog) → MCP SSE (5501) → Flask API (5500) → Ollama (11434) → GPU/CPU
                                              ↑
                        Olympics benchmarks → auto-updates god→model mapping
```

**Three modes:**
- **`/ask`** — Solo: classify → route to one god → respond
- **`/council`** — Council: 3-5 gods respond → Athena synthesizes
- **`/pipeline`** — Pipeline: gods hand off sequentially (research → code → audit)

**Deliberation mode** (`/ask` with `mode=deliberate`): Before routing, Hermes deliberates about which god to choose, why, confidence level, and how to frame the prompt — like `<thinking>` tokens but pantheon-aware.

### Hardware

- **Lappy** (192.168.0.33): RTX 3060 6GB VRAM, 40GB RAM, Ollama server
- All inference runs locally — no API calls, no data leaves the LAN

## The Olympics

The Olympics is a daily benchmark system that finds the best model for each god role.

### How It Works

1. **12 god-themed events** — each tests a different capability:
   - Zeus (Thunderbolt): Decisiveness — CEO ruling on 3-way faction conflict
   - Athena (Owl's Eye): Reasoning — Geopolitical rare earth strategy
   - Hephaestus (The Forge): Code — LRU cache implementation
   - Prometheus (The Heist): Disruption — Security vulnerability enumeration
   - Heracles (The Labor): Debugging — Async race condition diagnosis
   - Hermes (Winged Sandal): Speed — 3-bullet summary under constraints
   - Aphrodite (The Mirror): Beauty — Aegean sunset creative writing
   - Demeter (The Harvest): Clarity — Docker metaphor for non-programmers
   - Hecate (The Veil): Patterns — Server anomaly detection
   - Persephone (The Descent): Synthesis — Microservices vs monolith compromise
   - Hestia (The Hearth): Safety — Vulnerability naming
   - Dionysus (The Bacchanal): Chaos — Genre-shifting creative writing

2. **Every model runs all 12 events** — responses scored on Quality (60%) + Speed (40%)

3. **Champion per god** — model with highest average composite score wins that god's domain

4. **Auto-update** — `mog_config.json` updated automatically when champions change

### Scoring

- **Quality** (0.0-1.0): God-specific rubric with criteria hits, penalty detection, sentence count bounds
- **Speed** (0-1): Normalized relative to other models in the same event
- **Composite**: `0.6 × quality + 0.4 × speed` — empty responses get composite = 0

### Final Champions (18 Rounds, 16 Models Tested — COMPLETE)

| God | Champion | Quality | Event |
|-----|----------|---------|-------|
| Zeus | qwen3:4b | 0.55 | Thunderbolt (Decisiveness) |
| Athena | phi4-mini:3.8b | 0.55 | Owl's Eye (Reasoning) |
| Hephaestus | medgemma1.5:4b | 0.82 | The Forge (Code) |
| Prometheus | phi4-mini:3.8b | 0.59 | The Heist (Disruption) |
| Heracles | qwen3:4b | 0.64 | The Labor (Debugging) |
| Hermes | qwen3:4b | 0.70 | Winged Sandal (Speed) |
| Aphrodite | qwen3:4b | 0.55 | The Mirror (Beauty) |
| Demeter | medgemma1.5:4b | 0.57 | The Harvest (Clarity) |
| Hecate | medgemma1.5:4b | 0.59 | The Veil (Patterns) |
| Persephone | medgemma1.5:4b | 0.57 | The Descent (Synthesis) |
| Hestia | granite4.1:3b | 0.67 | The Hearth (Safety) |
| Dionysus | qwen3:4b | 0.64 | The Bacchanal (Chaos) |

**Top models by event wins**: qwen3:4b (5), medgemma1.5:4b (4), phi4-mini:3.8b (2), granite4.1:3b (1)

## Models Tested (16)

| Model | Size | Tier | Events Won |
|-------|------|------|------------|
| qwen3:4b | 2.4GB | GPU | 5 — Zeus, Heracles, Hermes, Aphrodite, Dionysus |
| medgemma1.5:4b | 2.8GB | GPU | 4 — Hephaestus, Demeter, Hecate, Persephone |
| phi4-mini:3.8b | 2.3GB | GPU | 2 — Athena, Prometheus |
| granite4.1:3b | 2.0GB | GPU | 1 — Hestia |
| phi3.5 | 2.2GB | GPU | 0 |
| lfm2.5-thinking:1.2b | 0.9GB | GPU | 0 |
| qwen3:8b | 4.9GB | GPU | 0 |
| qwen2.5-coder:7b | 4.7GB | GPU | 0 |
| deepseek-r1:8b | 4.7GB | GPU | 0 |
| glm4:9b | 5.5GB | GPU | 0 |
| qwen3.5:4b | 2.8GB | GPU | 0 |
| qwen3.5:2b | 1.5GB | GPU | 0 |
| granite4.1:8b | 5.3GB | GPU | 0 |
| qwen3.5:9b | 5.5GB | RAM | 0 |
| gemma4 | 9.6GB | RAM | 0 |
| phi4:14b | 9.1GB | RAM | 0 |

## File Structure

```
Lappy: D:\mog\
  mog_server.py          # Flask API (main MoG server, port 5500)
  mog_mcp_server.py      # MCP SSE wrapper (port 5501)
  mog_config.json        # God → model mapping (auto-updated by Olympics)
  olympics_daily.py      # Challenge runner (12 events × N models)
  olympics_score.py      # Quality + speed scoring engine
  olympics_roster.json   # All candidate models

Rog: C:\Users\aaron\Desktop\dev\the-olympics\
  index.html             # Scoreboard (GitHub Pages)
  history.json           # Olympics results
  README.md              # This file
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ask` | POST | Solo mode — classify → route → respond |
| `/council` | POST | Multi-god council with synthesis |
| `/pipeline` | POST | Sequential god handoff |
| `/deliberate` | POST | Routing analysis without response |
| `/state` | GET | Current Ollama model states |
| `/config` | GET/POST | Read/update god→model mapping |
| `/health` | GET | Health check |

## Evolution

- **Round 1-2**: qwen3:4b vs glm4:9b → qwen3:4b won speed, glm4:9b won quality
- **Round 3-8**: +4 models → phi3.5 dominated 6 gods, qwen3:4b won 6 by speed
- **Round 9-14**: +6 new models (phi4-mini, granite4.1, medgemma, qwen3.5) → major shifts, medgemma1.5:4b won 4 events
- **Round 15-18**: RAM-tier models tested (gemma4, phi4:14b, qwen3.5:9b) → slower but competitive quality
- **Final**: 16 models, 18 rounds — qwen3:4b (5 wins), medgemma1.5:4b (4 wins), phi4-mini:3.8b (2), granite4.1:3b (1)

Olympics is complete. Future rounds will run when new models arrive.
