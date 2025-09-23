# Browser Agent

An AI-powered browser automation microservice built on the Kernel platform that uses browser-use for intelligent web browsing tasks.

## Overview

The browser-agent microservice provides AI-powered browser automation capabilities, allowing you to control browsers using natural language instructions. It supports multiple LLM providers (Anthropic Claude, OpenAI GPT, Google Gemini) and can handle complex multi-step web tasks including data extraction, form filling, file downloads, and CAPTCHA solving.

## Features

- **AI-powered browser automation**: Uses LLMs to intelligently control browsers and perform complex web tasks
- **Multi-step task execution**: Decomposes complex requests into sub-tasks and executes them sequentially
- **Multi-provider LLM support**: Works with Anthropic Claude, OpenAI GPT, and Google Gemini
- **File handling**: Automatically downloads PDFs and other files, uploads them to cloud storage
- **CAPTCHA solving**: Built-in capability to handle CAPTCHAs and similar challenges
- **Session management**: Creates isolated browser sessions with proper cleanup
- **Trajectory tracking**: Records and stores complete execution history for analysis
- **Cloudflare AI Gateway integration**: Unified LLM provider routing w/ caching

## Getting Started

- [mise](https://mise.jdx.dev/) - Development environment manager
- Python 3.11+ (managed via mise)
- Node.js with `bun` (for deployment tools, managed via mise)

```bash
# Install development tools
mise install

# Install Python dependencies
uv sync

# Copy environment template
cp .env.example .env
```

Edit your `.env` file with the required values:

```bash
# AI Gateway Configuration (required)
AI_GATEWAY_URL="https://gateway.ai.cloudflare.com/v1/{account_id}/ai-gateway"
AI_GATEWAY_TOKEN="your-gateway-token"

# Kernel Platform (required)
KERNEL_API_KEY="sk_xxxxx"

# Cloudflare R2 Storage (required)
S3_BUCKET="browser-agent"
S3_ACCESS_KEY_ID="your-access-key"
S3_ENDPOINT_URL="https://{account_id}.r2.cloudflarestorage.com"
S3_SECRET_ACCESS_KEY="your-secret-key"
```

Test that everything is working:

```bash
# Start the development server
just dev

# In another terminal, check the service is running
curl http://localhost:8080/health
```

## API Reference

### Endpoint

`POST /apps/browser-agent/actions/perform`

### Request Format

```json
{
  "input": "Task description for the browser agent",
  "provider": "anthropic|gemini|openai",
  "model": "claude-4-sonnet|gpt-4.1|gemini-2.5-pro",
  "api_key": "your-llm-api-key",
  "instructions": "Optional additional instructions",
  "stealth": true,
  "headless": false,
  "browser_timeout": 60,
  "max_steps": 100,
  "reasoning": true,
  "flash": false
}
```

### Request Parameters

- `input` (required): Natural language description of the task to perform
- `provider` (required): LLM provider (`"anthropic"`, `"gemini"`, or `"openai"`)
- `model` (required): Specific model to use (e.g., `"claude-3-sonnet-20240229"`)
- `api_key` (required): API key for the LLM provider
- `instructions` (optional): Additional context or constraints for the task
- `stealth` (optional): Enable stealth mode to avoid detection (default: `true`)
- `headless` (optional): Run browser in headless mode (default: `false`)
- `browser_timeout` (optional): Browser session shutdown timeout in seconds (default: 60)
- `max_steps` (optional): Maximum number of automation steps (default: 100)
- `reasoning` (optional): Enable step-by-step reasoning (default: `true`)
- `flash` (optional): Use faster execution mode (default: `false`)

### Response Format

```json
{
  "session": "browser-session-id",
  "success": true,
  "duration": 45.2,
  "result": "Task completion summary",
  "downloads": {
    "filename.pdf": "https://presigned-url",
    "data.csv": "https://presigned-url"
  }
}
```

### Response Fields

- `session`: Unique browser session identifier
- `success`: Whether the task completed successfully
- `duration`: Execution time in seconds
- `result`: Summary of what was accomplished
- `downloads`: Dictionary of downloaded files with presigned URLs

## Examples

### Basic Web Scraping

```json
{
  "input": "Go to example.com and extract all the text content from the main article",
  "provider": "anthropic",
  "model": "claude-4-sonnet",
  "api_key": "sk-ant-xxxxx",
  "headless": true,
  "max_steps": 50
}
```

### Complex Task with File Download

```json
{
  "input": "Search for Python tutorials on Google and download the first PDF result",
  "instructions": "Make sure to verify the PDF is relevant before downloading",
  "provider": "openai",
  "model": "gpt-4.1",
  "api_key": "sk-xxxxx",
  "headless": false,
  "reasoning": true
}
```

### Form Filling

```json
{
  "input": "Fill out the contact form on example.com with name 'John Doe', email 'john@example.com', and message 'Hello world'",
  "provider": "gemini",
  "model": "gemini-2.5-pro",
  "api_key": "your-gemini-key",
  "stealth": true
}
```

## Available Commands

This project uses [just](https://just.systems) as a task runner. All commands are defined in the `justfile`.

### Development Commands

```bash
just dev          # Run local development server on port 8000
just fmt          # Format and lint code with ruff (auto-fix issues)
just lint         # Check code formatting and linting (no auto-fix)
```

### Deployment Commands

```bash
just deploy       # Deploy main.py to Kernel platform
just logs         # View browser-agent logs with follow mode
```

### AI Tool Integration

```bash
just claude       # Run Claude Code CLI (setup and development assistant)
just gemini       # Run Google Gemini CLI
```

### Kernel Platform Commands

```bash
just kernel <cmd> # Run any Kernel CLI command (e.g., 'just kernel status')
```

## Deployment

The deployment process:
1. Runs formatting and linting checks
2. Deploys `src/app.py` to the Kernel platform
3. Service becomes available at the configured Kernel endpoint

## Architecture

### Core Components

- **`src/app.py`**: Main Kernel app with `browser-agent` action. Creates browsers via kernel, instantiates Agent with custom session, runs tasks and returns trajectory results.
- **`src/lib/browser/session.py`**: CustomBrowserSession that extends browser-use's BrowserSession, fixing viewport handling for CDP connections and setting fixed 1024x786 resolution.
- **`src/lib/browser/models.py`**: BrowserAgentRequest model handling LLM provider abstraction (anthropic, gemini, openai) with AI gateway integration.
- **`src/lib/gateway.py`**: AI gateway configuration from environment variables.

### Key Dependencies

- `browser-use>=0.7.2` - Web automation library providing Agent and BrowserSession
- `kernel>=0.11.0` - Platform for running the browser agent service
- `zenbase-llml>=0.4.0` - LLM templating used in task construction
- `pydantic>=2.10.6` - Data validation and serialization
- `boto3>=1.40.25` - AWS S3/R2 integration for file storage

### Architecture Flow

1. Request received via Kernel platform
2. LLM client created based on provider/model through AI Gateway
3. Remote browser session established with custom configuration
4. browser-use Agent instantiated with reasoning capabilities
5. Task executed with intelligent planning and step-by-step execution
6. Files automatically uploaded to Cloudflare R2 storage
7. Trajectory and results returned with download links

## Troubleshooting

### Common Issues

- **Environment variables**: Ensure all required environment variables are set
- **Browser timeout**: Increase `browser_timeout` for complex tasks
- **File downloads**: Check R2 bucket permissions and configuration
- **LLM provider errors**: Verify API keys and model availability
- **Deployment issues**: Ensure that the main entrypoint is in the root of the directory

## Contributing

1. Format code: `just fmt`
2. Test changes locally: `just dev`
3. Deploy to staging: `just deploy`
