# AtCoder Problem Converter

Convert AtCoder problem HTML pages to clean Markdown.

## Install (with uv)

```bash
# Ensure uv is installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# In project directory, create virtual env & install
uv sync
```

## Usage

CLI entry point (installed as `atcoder-problem-converter`):

```bash
uv run atcoder-problem-converter problem.html                # outputs problem.md
uv run atcoder-problem-converter problem.html out.md         # custom output file
uv run atcoder-problem-converter problem.html -l en          # English extraction
```

Or directly:

```bash
uv run python main.py problem.html
```

## Development

```bash
uv sync --dev         # install dev dependencies (pytest)
uv run pytest -q      # run tests
```

## Test HTML Example

Save an AtCoder task page as `sample.html` and run:

```bash
uv run atcoder-problem-converter sample.html
```

## License

MIT
