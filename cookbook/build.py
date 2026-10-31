"""
Render cookbook recipes to markdown.

Each recipe in recipes/ is a runnable Python file in the "percent" cell format
(the format used by Jupytext, VS Code, and PyCharm):

    # %% [markdown]
    # # Title
    # Prose, written as comment lines.

    # %%
    code = "runs as-is"

This script turns markdown cells into markdown and code cells into fenced
python blocks, writes one .md per recipe to markdown/, and writes an index.

    python cookbook/build.py
"""

import re
from pathlib import Path


ROOT = Path(__file__).parent
RECIPES = ROOT / "recipes"
OUT = ROOT / "markdown"

CELL_MARKER = re.compile(r"^# %%(?P<markdown>\s*\[markdown\])?\s*$")


def split_cells(source: str) -> list:
    cells = []
    kind, lines = None, []
    for line in source.splitlines():
        match = CELL_MARKER.match(line)
        if match:
            if kind is not None:
                cells.append((kind, lines))
            kind = "markdown" if match.group("markdown") else "code"
            lines = []
        elif kind is not None:
            lines.append(line)
    if kind is not None:
        cells.append((kind, lines))
    return cells


def strip_blank_edges(lines: list) -> list:
    while lines and not lines[0].strip():
        lines = lines[1:]
    while lines and not lines[-1].strip():
        lines = lines[:-1]
    return lines


def uncomment(line: str) -> str:
    if line.startswith("# "):
        return line[2:]
    if line.startswith("#"):
        return line[1:]
    return line


def render(source: str) -> str:
    blocks = []
    for kind, lines in split_cells(source):
        lines = strip_blank_edges(lines)
        if not lines:
            continue
        if kind == "markdown":
            blocks.append("\n".join(uncomment(line) for line in lines))
        else:
            blocks.append("```python\n" + "\n".join(lines) + "\n```")
    return "\n\n".join(blocks) + "\n"


def title_of(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def main() -> None:
    OUT.mkdir(exist_ok=True)
    index = [
        "# AskNews SDK Cookbook",
        "",
        "Runnable recipes for the AskNews Python SDK. Each page is generated from",
        "the matching file in `cookbook/recipes/`.",
        "",
    ]
    for recipe in sorted(RECIPES.glob("[0-9][0-9]_*.py")):
        markdown = render(recipe.read_text())
        target = OUT / f"{recipe.stem}.md"
        target.write_text(markdown)
        index.append(f"- [{title_of(markdown)}]({target.name})")
        print(f"wrote {target.relative_to(ROOT)}")
    (OUT / "index.md").write_text("\n".join(index) + "\n")
    print(f"wrote {(OUT / 'index.md').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
