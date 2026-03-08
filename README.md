# CLU Agent Repository

Specialized autonomous sub-developer agents for [CLU](https://github.com/developerclaude1-coder) — Developer Claude running on a Linux ARM64 VM.

Each agent is a focused expert spawned by CLU to handle a specific domain. They run via Claude Code's native multi-agent system, triggered by Telegram, n8n workflows, or direct CLI invocation.

## Agent Roster

| Agent | Role | Status |
|-------|------|--------|
| [tool-specialist](./agents/tool-specialist/) | Researches, installs, and configures CLI tools and packages | ✅ Active |
| [mcp-specialist](./agents/mcp-specialist/) | Discovers, tests, and manages MCP servers | ✅ Active |
| [skill-specialist](./agents/skill-specialist/) | Manages Claude Code plugins and skills | ✅ Active |
| [debug-specialist](./agents/debug-specialist/) | Systematic diagnosis — logs, errors, root cause analysis | ✅ Active |
| [research-agent](./agents/research-agent/) | Web research, AI news tracking, technical summaries | ✅ Active |
| [code-reviewer](./agents/code-reviewer/) | PR review, security scanning, quality enforcement | ✅ Active |
| [deploy-agent](./agents/deploy-agent/) | Builds, deployments, environment management | ✅ Active |
| [memory-agent](./agents/memory-agent/) | Keeps Drive docs, session logs, and context current | ✅ Active |

## Architecture

```
User (Telegram / CLI / n8n)
        ↓
      CLU  ← orchestrator, decides which agent(s) to spawn
    ↙  ↓  ↓  ↘
 tool  mcp  debug  research  (sub-agents, run in parallel)
        ↓
   Results merged → response to user
```

## How to Invoke

**From Telegram:** Just describe the task — CLU routes to the right agent.

**From CLI:**
```bash
claude --agent tool-specialist "find and install a better JSON diff tool"
claude --agent debug-specialist "n8n container keeps restarting, diagnose"
claude --agent research-agent "summarize this week's MCP ecosystem updates"
```

**From n8n:** HTTP webhook → CLU orchestrator → agent(s)

## Stack
- Runtime: Claude Code CLI (`claude --agent`)
- Orchestration: CLU + n8n (port 5678)
- Trigger: Telegram `@Dev_26vm_Bot`, n8n webhooks, GitHub Actions
- VM: Ubuntu 24.04 ARM64 (`developer-ai`)
