#!/usr/bin/env bash
# Build CLU agent Docker images
# Usage: ./build-agents.sh [agent-name]  — build one agent
#        ./build-agents.sh all           — build all agents
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS=(tool-specialist mcp-specialist skill-specialist debug-specialist
        research-agent code-reviewer deploy-agent memory-agent
        architect-agent n8n-builder security-auditor test-agent goo clu)

TARGET="${1:-all}"

build_agent() {
    local name="$1"
    echo "▶ Building clu-agent-${name}..."
    docker build \
        --file "${DIR}/Dockerfile.base" \
        --tag "clu-agent-${name}:latest" \
        --build-arg "AGENT_NAME=${name}" \
        "${DIR}"
    echo "  ✅ clu-agent-${name}:latest"
}

if [ "$TARGET" = "all" ]; then
    for agent in "${AGENTS[@]}"; do
        build_agent "$agent"
    done
    echo ""
    echo "All agents built. Images:"
    docker images --filter "reference=clu-agent-*" --format "  {{.Repository}}:{{.Tag}}  {{.Size}}"
else
    build_agent "$TARGET"
fi
