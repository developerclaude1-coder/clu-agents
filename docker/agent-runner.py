#!/usr/bin/env python3
"""
CLU Agent Runner — executes inside each agent Docker container.

Receives a task (via env TASK_JSON), runs it with the agent's identity,
saves output to the shared task queue output dir, updates agent memory.

Usage (called by clu-worker via docker run):
  docker run --rm \
    -e TASK_JSON='{"id":"t-...","title":"...","description":"...",...}' \
    -v /path/to/CLAUDE.md:/agent/CLAUDE.md:ro \
    -v agent-goo-memory:/agent/memory \
    -v ~/tools/clu-tasks/outputs:/agent/outputs \
    clu-agent:goo
"""
import json, os, re, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
AGENT_NAME    = os.environ.get("AGENT_NAME", "unknown")
OLLAMA_HOST   = os.environ.get("OLLAMA_HOST",        "http://100.90.97.7:11434")
FAST_MODEL    = os.environ.get("OLLAMA_FAST_MODEL",  "llama3.1:8b")
CODE_MODEL    = os.environ.get("OLLAMA_CODE_MODEL",  "qwen2.5-coder:14b")
THINK_MODEL   = os.environ.get("OLLAMA_THINK_MODEL", "deepseek-r1:14b")
GEMINI_KEY    = os.environ.get("GEMINI_API_KEY",     "")
GEMINI_MODEL  = os.environ.get("GEMINI_MODEL",       "gemini-2.5-flash")
TIMEOUT       = int(os.environ.get("OLLAMA_TIMEOUT", "240"))

CLAUDE_MD     = Path("/agent/CLAUDE.md")
MEMORY_DIR    = Path("/agent/memory")
OUTPUTS_DIR   = Path("/agent/outputs")
MEMORY_FILE   = MEMORY_DIR / "agent-memory.md"
TASK_LOG      = MEMORY_DIR / "task-log.md"

GEMINI_AGENTS = {"goo"}
THINK_AGENTS  = {"debug-specialist", "architect-agent", "security-auditor", "research-agent"}
CODE_AGENTS   = {"code-reviewer", "deploy-agent", "n8n-builder", "test-agent"}

THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)

def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def load_agent_identity() -> str:
    if CLAUDE_MD.exists():
        return CLAUDE_MD.read_text().strip()
    return f"You are {AGENT_NAME}, a CLU specialist agent. Be precise and helpful."

def load_memory() -> str:
    if MEMORY_FILE.exists():
        lines = MEMORY_FILE.read_text().splitlines()[-80:]
        return "\n".join(lines)
    return ""

def build_system_prompt(task: dict) -> str:
    identity = load_agent_identity()
    memory   = load_memory()
    parts    = [identity]
    if memory:
        parts.append(f"\n---\n## My Memory (recent context)\n{memory}")
    return "\n".join(parts)

def ollama_call(system: str, user: str) -> tuple[str, str, dict]:
    model = (
        GEMINI_MODEL if AGENT_NAME in GEMINI_AGENTS else
        THINK_MODEL  if AGENT_NAME in THINK_AGENTS  else
        CODE_MODEL   if AGENT_NAME in CODE_AGENTS   else
        FAST_MODEL
    )
    # Use Gemini if agent is goo and key is set
    if AGENT_NAME in GEMINI_AGENTS and GEMINI_KEY:
        return gemini_call(system, user)

    url = f"{OLLAMA_HOST}/api/chat"
    messages = [{"role": "system", "content": system}] if system else []
    messages.append({"role": "user", "content": user})
    payload = json.dumps({"model": model, "messages": messages, "stream": False,
                          "options": {"num_predict": 4096}}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        body = json.loads(r.read())
    raw = body.get("message", {}).get("content", "")
    thinking_blocks = THINK_RE.findall(raw)
    thinking = "\n".join(b.replace("<think>","").replace("</think>","").strip()
                         for b in thinking_blocks)
    response = THINK_RE.sub("", raw).strip()
    usage = {
        "prompt_tokens":     body.get("prompt_eval_count", 0),
        "completion_tokens": body.get("eval_count", 0),
        "total_tokens":      body.get("prompt_eval_count", 0) + body.get("eval_count", 0),
        "tokens_per_second": round(
            body.get("eval_count", 0) / max(body.get("eval_duration", 1) / 1e9, 0.001), 1),
        "model": model,
    }
    return response, thinking, usage

def gemini_call(system: str, user: str) -> tuple[str, str, dict]:
    url  = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_KEY}"
    body = {"contents": [{"parts": [{"text": user}]}],
            "generationConfig": {"maxOutputTokens": 8192}}
    if system:
        body["system_instruction"] = {"parts": [{"text": system}]}
    payload = json.dumps(body).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        data = json.loads(r.read())
    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    meta = data.get("usageMetadata", {})
    usage = {
        "prompt_tokens":     meta.get("promptTokenCount", 0),
        "completion_tokens": meta.get("candidatesTokenCount", 0),
        "total_tokens":      meta.get("totalTokenCount", 0),
        "tokens_per_second": 0,
        "model": f"gemini/{GEMINI_MODEL}",
    }
    return text, "", usage

def update_memory(task: dict, response: str) -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    # Append to task log
    entry = f"\n## [{now_iso()}] {task.get('title','Task')}\n**Status**: completed\n**Response preview**: {response[:200]}\n"
    with open(TASK_LOG, "a") as f:
        f.write(entry)
    # Trim task log to last 100 entries
    if TASK_LOG.exists():
        lines = TASK_LOG.read_text().splitlines()
        if len(lines) > 500:
            TASK_LOG.write_text("\n".join(lines[-400:]))

def main():
    task_json = os.environ.get("TASK_JSON", "")
    if not task_json:
        print("ERROR: TASK_JSON not set", file=sys.stderr)
        sys.exit(1)

    task = json.loads(task_json)
    print(f"[{AGENT_NAME}] Running task: {task.get('id')} — {task.get('title')}", flush=True)

    user_msg = task["description"]
    if task.get("context"):
        user_msg = f"{task['description']}\n\n---\nContext:\n{task['context']}"

    system = build_system_prompt(task)
    start  = time.time()

    try:
        response, thinking, usage = ollama_call(system, user_msg)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    duration = round(time.time() - start, 1)
    result = {
        "task_id":      task["id"],
        "agent":        AGENT_NAME,
        "model":        usage.get("model", "unknown"),
        "duration_sec": duration,
        "usage":        usage,
        "response":     response,
        "thinking":     thinking,
        "completed_at": now_iso(),
    }

    # Save to shared output dir
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUTS_DIR / f"{task['id']}.json"
    out_file.write_text(json.dumps(result, indent=2))

    # Update agent memory
    update_memory(task, response)

    print(f"[{AGENT_NAME}] Done in {duration}s | tokens: {usage.get('total_tokens',0)} | output: {out_file}", flush=True)
    print(json.dumps(result))  # stdout for clu-worker to capture

if __name__ == "__main__":
    main()
