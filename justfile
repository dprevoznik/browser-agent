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
  bunx -p @onkernel/cli kernel {{args}}

deploy *args:
  just kernel deploy src/app.py --env-file .env {{args}}

logs *args:
  just kernel logs browser-agent --follow {{args}}

fmt:
  uv run ruff check --fix && \
  uv run ruff format
