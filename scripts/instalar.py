#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instalador Multiplataforma (Windows / personal-device / Linux) — AGY-CONFIG
Restaura toda a configuração do Antigravity:
- ~/.gemini/config (AGENTS.md, config.json, hooks.json, hooks/, mcp_config.json, skills.json, plugins/, skills/, agents/)
- ~/.gemini/antigravity (mcp/, ollama_router/, hooks/, mcp_config.json, settings.json)
- Reescreve dinamicamente os caminhos para o diretório home do usuário na máquina de destino.
"""
import os
import shutil
from pathlib import Path

def copy_tree_merge(src: Path, dst: Path):
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            copy_tree_merge(item, target)
        else:
            shutil.copy2(item, target)

def rewrite_paths(file_path: Path, home: Path):
    if not file_path.exists():
        return
    txt = file_path.read_text(encoding="utf-8", errors="replace")
    home_fwd = str(home).replace("\\", "/")
    home_esc = str(home).replace("\\", "\\\\")
    txt = txt.replace("C:~", home_fwd).replace("c:~", home_fwd)
    txt = txt.replace("C:\\\\Users\\\\local-user", home_esc).replace("c:\\\\Users\\\\local-user", home_esc)
    txt = txt.replace("C:\\Users\\local-user", str(home)).replace("c:\\Users\\local-user", str(home))
    file_path.write_text(txt, encoding="utf-8")

def main():
    repo_root = Path(__file__).resolve().parent.parent
    home = Path.home()
    gemini_cfg = home / ".gemini" / "config"
    gemini_agy = home / ".gemini" / "antigravity"
    claude_hooks = home / ".claude" / "hooks"

    print("=" * 68)
    print("  Instalador Multiplataforma: AGY-CONFIG (Antigravity Full Setup)")
    print("  Cérebro: Argon -> Opus | Rápidos: Flash 3.8 -> Sonnet | Ollama")
    print("=" * 68)

    copy_tree_merge(repo_root / "config", gemini_cfg)
    print(f"[+] Configuração principal instalada em: {gemini_cfg}")

    scripts_src = repo_root / "config" / "hooks" / "scripts"
    if scripts_src.exists():
        copy_tree_merge(scripts_src, claude_hooks)
        print(f"[+] Scripts auxiliares de hooks instalados em: {claude_hooks}")

    copy_tree_merge(repo_root / "antigravity", gemini_agy)
    print(f"[+] Schemas MCP, ollama_router e hooks GSD instalados em: {gemini_agy}")

    for f in [
        gemini_cfg / "hooks.json",
        gemini_cfg / "mcp_config.json",
        gemini_cfg / "skills.json",
        gemini_cfg / "hooks" / "agy_hooks.py",
        gemini_agy / "settings.json",
    ]:
        rewrite_paths(f, home)
    print(f"[+] Caminhos ajustados automaticamente para: {home}")
    print("\nInstalação do AGY-CONFIG concluída com sucesso!")

if __name__ == "__main__":
    main()