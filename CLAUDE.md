# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development
- Format and lint: `just fmt` (runs ruff check --fix and ruff format)
- Deploy to kernel: `just deploy` (deploys src/app.py)
- View logs: `just logs` (follows browser-agent logs)

### Dependencies
- Install/manage dependencies: `uv` (Python package manager)
- Run Python with dependencies: `uv run <command>`

## Architecture

This is a browser automation agent built on the Kernel platform that uses browser-use for web automation.

### Core Components

- **src/app.py**: Main Kernel app with `browser-agent` action. Creates browsers via kernel, instantiates Agent with custom session, runs tasks and returns trajectory results.
- **src/lib/browser/session.py**: CustomBrowserSession that extends browser-use's BrowserSession, fixing viewport handling for CDP connections and setting fixed 1024x786 resolution.
- **src/lib/browser/models.py**: BrowserAgentRequest model handling LLM provider abstraction (anthropic, gemini, openai) with AI gateway integration.
- **src/lib/gateway.py**: AI gateway configuration from environment variables.

### Key Dependencies
- `browser-use`: Web automation library providing Agent and BrowserSession
- `kernel`: Platform for running the browser agent service
- `zenbase-llml`: LLM templating used in task construction
- Environment: Python 3.11, uses `uv` for dependency management, `just` for task running

### Environment Variables
Requires `AI_GATEWAY_URL` and `AI_GATEWAY_TOKEN` for LLM provider routing through AI gateway.
