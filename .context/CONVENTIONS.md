# Conventions

- Follow [code-quality skill standards](C:\Users\uig55220\.gemini\antigravity\skills\code-quality\SKILL.md)
- Use `uv` for dependency management
- Use `pytest` for testing
- Use `ruff` for linting and formatting
- Keep JSON artifact presentation self-contained: render root `*_data.json` files into static HTML without requiring React, npm, or a running server
- Keep non-render commands resilient to missing optional runtime dependencies by importing network/XBRL integrations lazily where possible
