# Justfile – handy task runner (https://just.systems)

# --- settings ---------------------- https://just.systems/man/en/settings.html
set dotenv-load := true
set dotenv-path := ".env"
set ignore-comments := true

[group('ai')]
claude *args:
  bunx @anthropic-ai/claude-code {{args}}

[group('ai')]
gemini *args:
  bunx @google/gemini-cli {{args}}

kernel *args:
  bunx --bun -p @onkernel/cli kernel {{args}}

logs *args:
  just kernel logs browser-agent --follow {{args}}

fmt:
  uv run ruff check --fix && \
  uv run ruff format

lint:
  uv run ruff check && \
  uv run ruff format --check
