#!/bin/bash

# EvalView Agent Testing Runner
# Systematically tests EvalView with multiple agent frameworks

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
PASSED_TESTS=0
FAILED_TESTS=0
TOTAL_FRAMEWORKS=0

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🧪 EvalView Framework Compatibility Testing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Function to test a framework
test_framework() {
    local framework=$1
    local dir="$2"

    echo ""
    echo "${BLUE}━━━ Testing: $framework ━━━${NC}"

    TOTAL_FRAMEWORKS=$((TOTAL_FRAMEWORKS + 1))

    if [ ! -d "$dir" ]; then
        echo "${YELLOW}⚠️  Directory not found: $dir${NC}"
        echo "   Skipping..."
        return
    fi

    cd "$dir"

    # Check if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        echo "📦 Installing dependencies..."
        pip install -q -r requirements.txt 2>&1 | grep -v "already satisfied" || true
    fi

    # Check if agent file exists
    AGENT_FILE=""
    if [ -f "agent.py" ]; then
        AGENT_FILE="agent.py"
    elif [ -f "server.py" ]; then
        AGENT_FILE="server.py"
    elif [ -f "main.py" ]; then
        AGENT_FILE="main.py"
    else
        echo "${RED}✗ No agent file found (agent.py, server.py, or main.py)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        cd - > /dev/null
        return
    fi

    # Start agent in background
    echo "🚀 Starting agent..."
    python "$AGENT_FILE" > /tmp/evalview-agent-${framework}.log 2>&1 &
    AGENT_PID=$!

    # Wait for agent to start
    echo "⏳ Waiting for agent to be ready..."
    sleep 3

    # Check if agent is running
    if ! ps -p $AGENT_PID > /dev/null; then
        echo "${RED}✗ Agent failed to start${NC}"
        echo "   Check logs: /tmp/evalview-agent-${framework}.log"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        cd - > /dev/null
        return
    fi

    # Run EvalView tests
    echo "🧪 Running EvalView tests..."
    if evalview run --verbose > /tmp/evalview-test-${framework}.log 2>&1; then
        echo "${GREEN}✓ Tests PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))

        # Show summary
        echo ""
        grep -A 10 "Test Results" /tmp/evalview-test-${framework}.log || true
    else
        echo "${RED}✗ Tests FAILED${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo "   Check logs: /tmp/evalview-test-${framework}.log"
    fi

    # Cleanup: kill agent
    echo "🧹 Cleaning up..."
    kill $AGENT_PID 2>/dev/null || true
    sleep 1

    cd - > /dev/null
}

# Test Reference Agent
test_framework "Reference Agent" "reference-agent"

# Test LangChain (if exists)
test_framework "LangChain" "langchain"

# Test LangGraph (if exists)
test_framework "LangGraph" "langgraph"

# Test CrewAI (if exists)
test_framework "CrewAI" "crewai"

# Test OpenAI Assistants (if exists)
test_framework "OpenAI Assistants" "openai-assistants"

# Test AutoGen (if exists)
test_framework "AutoGen" "autogen"

# Test LlamaIndex (if exists)
test_framework "LlamaIndex" "llamaindex"

# Test Anthropic Claude (if exists)
test_framework "Anthropic Claude" "anthropic"

# Add more frameworks as they're implemented...

# Final summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  📊 Test Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Total Frameworks Tested: $TOTAL_FRAMEWORKS"
echo "${GREEN}Passed: $PASSED_TESTS${NC}"
echo "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ] && [ $TOTAL_FRAMEWORKS -gt 0 ]; then
    echo "${GREEN}🎉 All tests passed! EvalView is ready for launch!${NC}"
    exit 0
else
    echo "${YELLOW}⚠️  Some tests failed or no frameworks were tested.${NC}"
    echo "   Review logs in /tmp/evalview-*.log"
    exit 1
fi
