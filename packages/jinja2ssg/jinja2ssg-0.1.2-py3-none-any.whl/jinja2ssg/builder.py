import os
from typing import List
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def build(*, src: str, dest: str, ext: List[str]):
    src_path = Path(src).resolve()
    dest_path = Path(dest).resolve()
    env = Environment(loader=FileSystemLoader(str(src)))
    if not dest_path.exists():
        os.makedirs(dest_path)
    for path in src_path.glob("**/*"):
        if path.name.startswith("_") or path.is_dir() or path.suffix not in ext:
            continue
        out_path = dest_path / path.relative_to(src_path)
        if not out_path.parent.exists():
            os.makedirs(out_path.parent)
        template_path = str(path.relative_to(src_path))
        print(f"{template_path} -> {out_path}")
        template = env.get_template(template_path)
        html = template.render()
        with open(out_path, "w", encoding="utf-8") as fl:
            fl.write(html)
