# CLU Agent Repository

Specialized autonomous sub-developer agents for [CLU](https://github.com/developerclaude1-coder) — Developer Claude running on a Linux ARM64 VM.

Each agent is a focused expert spawned by CLU to handle a specific domain. They run via Claude Code's native multi-agent system, triggered by Telegram, n8n workflows, the dev loop task queue, or direct CLI invocation.

## Agent Roster

| Agent | Role | Status |
|-------|------|--------|
| [tool-specialist](./agents/tool-specialist/) | Researches, installs, and configures CLI tools and packages | ✅ Active |
| [mcp-specialist](./agents/mcp-specialist/) | Discovers, tests, and manages MCP servers | ✅ Active |
| [skill-specialist](./agents/skill-specialist/) | Manages Claude Code plugins and skills | ✅ Active |
| [debug-specialist](./agents/debug-specialist/) | Systematic diagnosis — logs, errors, root cause analysis | ✅ Active |
| [research-agent](./agents/research-agent/) | Web research, AI news tracking, technical summaries | ✅ Active |
| [code-reviewer](./agents/code-reviewer/) | PR review, security scanning, quality enforcement | ✅ Active |
| [deploy-agent](./agents/deploy-agent/) | Builds, deployments, Docker, and CI/CD | ✅ Active |
| [memory-agent](./agents/memory-agent/) | Keeps Drive docs, session logs, and context current | ✅ Active |
| [architect-agent](./agents/architect-agent/) | System design, stack selection, phased build plans | ✅ Active |
| [n8n-builder](./agents/n8n-builder/) | Designs and deploys n8n automation workflows | ✅ Active |
| [security-auditor](./agents/security-auditor/) | Security scanning — secrets, ports, CVEs, Docker | ✅ Active |
| [test-agent](./agents/test-agent/) | Writes unit, integration, and E2E tests | ✅ Active |

## Architecture

```
User (Telegram / CLI / n8n / clu-task queue)
        ↓
      CLU  ← orchestrator, decides which agent(s) to spawn
    ↙  ↓  ↓  ↘
 tool  mcp  debug  research  (sub-agents, run in parallel)
        ↓
   Results merged → response to user / task output
```

## Memory & Prompting

Each agent is loaded with:
1. **Identity** — its `CLAUDE.md` defines who it is, what it owns, how it works
2. **CLU Memory** — `~/.claude/projects/-home-knowam/memory/MEMORY.md` injected as context
3. **Task context** — description + any additional context provided at invocation time

When routing through the autonomous dev loop (`clu-worker`), the agent's CLAUDE.md is used as the system prompt and CLU's memory is prepended as context, so local LLMs behave consistently with the same identity.

## How to Invoke

**From Telegram:**
```
/agent debug-specialist n8n container keeps restarting
/agent research-agent summarize this week's MCP ecosystem updates
```

**From CLI (Claude Code native):**
```bash
claude --agent tool-specialist "find and install a better JSON diff tool"
claude --agent debug-specialist "n8n container keeps restarting, diagnose"
claude --agent research-agent "summarize this week's MCP ecosystem updates"
```

**From the dev loop (routes to local LLM with agent identity):**
```bash
clu-task add --title "Review auth module" --desc "..." \
  --category code --agent code-reviewer
```

## Environment

- n8n: http://localhost:8127
- CLU Executor: http://localhost:8312
- Ollama (Mac Mini): http://100.90.97.7:11434
- VM: Ubuntu 24.04 ARM64 (`developer-ai`)
- Runtime: Claude Code CLI or clu-worker (Ollama)

## Workflows

Pre-built n8n workflow exports live in [`./workflows/`](./workflows/).
