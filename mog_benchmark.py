"""MoG Benchmark Runner — Tests MoG routing against single models.
Runs diverse tasks through MoG and individual models, compares results.
Uses pi's print mode for agentic tasks, MoG API for routing comparison."""

import json
import os
import sys
import time
import subprocess
import requests
from datetime import datetime
from pathlib import Path

MOG_URL = "http://192.168.0.33:5500"
OLLAMA_URL = "http://192.168.0.33:11434"

# Diverse benchmark tasks covering all 12 god domains
BENCHMARK_TASKS = [
    # Hephaestus — Code generation
    {
        "id": "code-lru",
        "domain": "coding",
        "expected_god": "Hephaestus",
        "prompt": "Write a Python LRU cache class with get, put, and delete methods. Use OrderedDict. Include type hints. No explanation, just the code.",
        "verify": "class LRUCache" ,
    },
    {
        "id": "code-linkedlist",
        "domain": "coding",
        "expected_god": "Hephaestus",
        "prompt": "Implement a doubly linked list in Python with insert, delete, and reverse methods. Type hints. Code only.",
        "verify": "class ",
    },
    # Heracles — Debugging
    {
        "id": "debug-race",
        "domain": "debugging",
        "expected_god": "Heracles",
        "prompt": "This async Python code has a bug: the cache's get() reads without lock, put() writes with lock, and get_or_set() checks then calls factory then writes without lock. What's the race condition and how do I fix it?",
        "verify": "race condition",
    },
    {
        "id": "debug-memory",
        "domain": "debugging",
        "expected_god": "Heracles",
        "prompt": "My Python web server slowly leaks memory. I use aiohttp with a global dict cache that never gets cleared. Requests create large response objects stored in the dict. What's causing the leak and how to fix?",
        "verify": "leak",
    },
    # Hecate — Security
    {
        "id": "security-sqli",
        "domain": "security",
        "expected_god": "Hecate",
        "prompt": "Review this Flask endpoint for security vulnerabilities: it uses f-strings for SQL queries with user input, has no rate limiting, stores passwords with MD5, and has a /admin route with no auth. List all vulnerabilities.",
        "verify": "SQL injection",
    },
    {
        "id": "security-jwt",
        "domain": "security",
        "expected_god": "Hecate",
        "prompt": "My auth system uses JWT with 30-day expiry, no refresh token rotation, HS256 with a hardcoded secret 'my-secret-key', and stores the JWT in localStorage. What are the security issues?",
        "verify": "XSS",
    },
    # Athena — Reasoning/Strategy
    {
        "id": "reasoning-arch",
        "domain": "reasoning",
        "expected_god": "Athena",
        "prompt": "We need to scale from 10K to 1M users in 18 months. Current monolith on Flask+PostgreSQL. Should we migrate to microservices? Consider team size (8 devs), deployment frequency (daily), and failure isolation needs. Give a concrete plan.",
        "verify": "microservice",
    },
    {
        "id": "reasoning-tradeoff",
        "domain": "reasoning",
        "expected_god": "Athena",
        "prompt": "Compare SQLite vs PostgreSQL for a read-heavy web app (95% reads, 5% writes) with 100 concurrent users, 1GB data, running on a single VPS with 2GB RAM. Which do you recommend and why?",
        "verify": "PostgreSQL",
    },
    # Zeus — Decisiveness
    {
        "id": "decisive-ceo",
        "domain": "decisiveness",
        "expected_god": "Zeus",
        "prompt": "As CTO: Engineering wants to rewrite the backend in Rust (6 months). Sales needs 5 new API endpoints next month. Security found a critical auth bypass. The board meets in 2 weeks. Give me your ruling — what's the plan?",
        "verify": "",
    },
    # Aphrodite — Creative writing
    {
        "id": "creative-sunset",
        "domain": "creative",
        "expected_god": "Aphrodite",
        "prompt": "Write a single paragraph describing a sunset over the Aegean Sea. Make the reader feel something they'd forgotten. No cliches. 4 sentences.",
        "verify": "",
    },
    {
        "id": "creative-product",
        "domain": "creative",
        "expected_god": "Aphrodite",
        "prompt": "Write a compelling 3-sentence product description for a smart garden sensor that monitors soil moisture, sunlight, and nutrients. Target urban millennials who kill houseplants. Make it witty.",
        "verify": "",
    },
    # Demeter — Teaching
    {
        "id": "teach-docker",
        "domain": "teaching",
        "expected_god": "Demeter",
        "prompt": "Explain Docker containers to someone who has never programmed, using a cooking or gardening metaphor. Be warm and patient. 3-4 sentences.",
        "verify": "container",
    },
    # Hermes — Speed/Summary
    {
        "id": "summary-quantum",
        "domain": "speed",
        "expected_god": "Hermes",
        "prompt": "Summarize in exactly 3 bullets each under 15 words: Quantum computing grew in 2026. IBM made 10000-qubit chip. Google did drug discovery. Error correction challenges remain. China invested 15 billion. EU launched 6 billion program.",
        "verify": "",
    },
    # Persephone — Synthesis
    {
        "id": "synthesis-monolith",
        "domain": "synthesis",
        "expected_god": "Persephone",
        "prompt": "Team A wants microservices for scalability. Team B wants monolith for speed. We're building ecommerce, currently 10K users, targeting 100K in 2 years. Propose a unified architecture in 4 sentences.",
        "verify": "",
    },
    # Dionysus — Creative chaos
    {
        "id": "chaos-review",
        "domain": "creative_chaos",
        "expected_god": "Dionysus",
        "prompt": "Write 3 sentences starting as a restaurant review that become something entirely different by the end. Surprise the reader.",
        "verify": "",
    },
    # Hestia — Safety
    {
        "id": "safety-vulns",
        "domain": "safety",
        "expected_god": "Hestia",
        "prompt": "Name the security vulnerabilities (not style issues): 1) SQL uses f-string with user input 2) read_file has no path validation 3) password hashed with md5. Just list the vulnerability names.",
        "verify": "SQL injection",
    },
]


def run_mog(prompt, mode="auto"):
    """Run a task through MoG router."""
    try:
        r = requests.post(f"{MOG_URL}/ask", json={
            "prompt": prompt, "mode": mode
        }, timeout=300)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def run_direct(model, prompt):
    """Run a task directly through Ollama."""
    try:
        r = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {"num_predict": 2048}
        }, stream=True, timeout=300)

        full_response = ""
        for line in r.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            if "error" in chunk:
                return {"error": chunk["error"]}
            full_response += chunk.get("response", "")
            if chunk.get("done", False):
                break
        return {"response": full_response}
    except Exception as e:
        return {"error": str(e)}


def score_response(task, response):
    """Simple scoring: check if expected content is present, measure length appropriateness."""
    if not response or "error" in response:
        return {"present": False, "score": 0.0, "reason": "error or empty"}

    verify = task.get("verify", "")
    present = verify.lower() in response.lower() if verify else True
    length = len(response)
    words = len(response.split())

    # Score: presence (0.5) + reasonable length (0.3) + not too short (0.2)
    score = 0.0
    if present:
        score += 0.5
    if 20 <= words <= 500:
        score += 0.3
    elif words > 500:
        score += 0.1  # too long, slight penalty
    if words >= 10:
        score += 0.2

    return {"present": present, "score": round(score, 2), "words": words, "length": length}


def run_benchmark(models_to_compare=None, tasks=None):
    """Run the full benchmark suite."""
    results = {
        "date": datetime.now().isoformat(),
        "mog_results": [],
        "direct_results": {},
    }

    task_list = tasks or BENCHMARK_TASKS

    print(f"\n{'='*60}")
    print(f"  MoG Benchmark — {len(task_list)} tasks")
    print(f"{'='*60}")

    # Test MoG routing
    print("\n--- MoG Routing ---")
    for task in task_list:
        tid = task["id"]
        print(f"  [{tid}] ", end="", flush=True)
        start = time.time()
        result = run_mog(task["prompt"])
        wall = round(time.time() - start, 1)

        response = result.get("response", "")
        god = result.get("god", "?")
        model = result.get("model", "?")
        speed = result.get("tokens_per_sec", 0)
        correct_god = god == task.get("expected_god", "")
        scoring = score_response(task, response)

        results["mog_results"].append({
            "task_id": tid,
            "domain": task["domain"],
            "expected_god": task.get("expected_god", ""),
            "routed_god": god,
            "routed_model": model,
            "correct_god": correct_god,
            "wall_sec": wall,
            "speed": speed,
            "response_len": len(response),
            **scoring,
        })
        god_mark = "Y" if correct_god else "N"
        print(f"{god}({model}) {god_mark} {wall}s {scoring['score']:.1f}")

    # Test individual models directly
    if models_to_compare is None:
        # Get current MoG config to find active models
        try:
            r = requests.get(f"{MOG_URL}/config", timeout=10)
            cfg = r.json()
            active_models = list(set(m["model"] for m in cfg["gods"].values()))
        except:
            active_models = ["qwen3:4b", "phi3.5"]
        models_to_compare = active_models

    for model in models_to_compare:
        print(f"\n--- {model} (direct) ---")
        results["direct_results"][model] = []
        for task in task_list:
            tid = task["id"]
            print(f"  [{tid}] ", end="", flush=True)
            start = time.time()
            result = run_direct(model, task["prompt"])
            wall = round(time.time() - start, 1)

            response = result.get("response", "")
            scoring = score_response(task, response)

            results["direct_results"][model].append({
                "task_id": tid,
                "domain": task["domain"],
                "wall_sec": wall,
                "response_len": len(response),
                **scoring,
            })
            print(f"{wall}s {scoring['score']:.1f}")

    # Summary
    print(f"\n{'='*60}")
    print(f"  RESULTS SUMMARY")
    print(f"{'='*60}")

    # MoG aggregate
    mog_scores = [r["score"] for r in results["mog_results"]]
    mog_god_accuracy = sum(1 for r in results["mog_results"] if r.get("correct_god")) / max(len(results["mog_results"]), 1)
    print(f"  MoG:     avg={sum(mog_scores)/len(mog_scores):.2f}  god_accuracy={mog_god_accuracy:.0%}")

    for model, model_results in results["direct_results"].items():
        scores = [r["score"] for r in model_results]
        print(f"  {model:20s}: avg={sum(scores)/len(scores):.2f}")

    # Save results
    out_path = Path(__file__).parent / "benchmark_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {out_path}")

    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MoG Benchmark Runner")
    parser.add_argument("--models", nargs="*", help="Specific models to compare against")
    parser.add_argument("--quick", action="store_true", help="Run only 5 tasks")
    args = parser.parse_args()

    tasks = BENCHMARK_TASKS[:5] if args.quick else None
    run_benchmark(models_to_compare=args.models, tasks=tasks)
