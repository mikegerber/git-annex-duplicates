default:
  @just --list

test:
  uv run pytest

check:
  uvx ruff check
  uvx ty check
