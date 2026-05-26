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

### Current Champions (Round 2)

| God | Champion | Composite |
|-----|----------|-----------|
| Zeus | qwen3:4b | 0.730 |
| Athena | phi3.5 | 0.679 |
| Hephaestus | phi3.5 | 0.850 |
| Prometheus | phi3.5 | 0.716 |
| Heracles | phi3.5 | 0.711 |
| Hermes | qwen3:4b | 0.820 |
| Aphrodite | qwen3:4b | 0.730 |
| Demeter | qwen3:4b | 0.730 |
| Hecate | qwen3:4b | 0.718 |
| Persephone | phi3.5 | 0.730 |
| Hestia | phi3.5 | 0.749 |
| Dionysus | qwen3:4b | 0.730 |

## Roster (17 Models)

8 current + 9 being pulled:

| Model | Size | Tier | Strength |
|-------|------|------|----------|
| qwen3:4b | 2.5GB | GPU | Speed, coding, general |
| phi3.5 | 2.0GB | GPU | Compact reasoning |
| glm4:9b | 5.5GB | GPU | Reasoning, bilingual |
| qwen2.5-coder:7b | 4.4GB | GPU | Coding specialist |
| deepseek-r1:8b | 4.9GB | GPU | Reasoning, math |
| qwen3:8b | 4.9GB | GPU | General purpose |
| gemma4 | 9.6GB | RAM | All-rounder |
| glm-4.7-flash | 19GB | RAM | Best quality |
| **phi4:14b** | 9.1GB | RAM | SOTA general, function calling |
| **phi4-mini:3.8b** | 2.5GB | GPU | Compact, multilingual, tool use |
| **qwen3-coder:30b** | 19GB | RAM | Agentic coding |
| **dolphin3:8b** | 4.9GB | GPU | Uncensored creative |
| **exaone-deep:7.8b** | 4.8GB | GPU | Math, coding reasoning |
| **phi4-reasoning:14b** | 11GB | RAM | Deep chain-of-thought |
| **command-r7b:7b** | 5.1GB | GPU | Tool use, RAG |
| **granite4.1:8b** | 5.3GB | GPU | Enterprise, multilingual |
| **lfm2.5-thinking:1.2b** | 1.2GB | GPU | Ultra-tiny thinking |

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

Round 1: qwen3:4b vs glm4:9b → qwen3:4b won speed, glm4:9b won quality
Round 2: +4 models → phi3.5 dominated 6 gods, qwen3:4b won 6 by speed
Round 3 (upcoming): +9 new models including phi4, dolphin3, qwen3-coder → expecting major shifts

Models that score lowest in their domain get evicted when disk space is needed. The Olympics runs daily at 03:00 — champions improve over time without human intervention.
