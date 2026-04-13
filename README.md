# kenchiku-mcp

[English](#kenchiku-mcp) | [日本語](#日本語)

Architectural CAD MCP server for ZWCAD with non-uniform block scaling.

## Attribution

Based on [multiCAD-mcp](https://github.com/AnCode666/multiCAD-mcp) v0.2.0 by [AnCode666](https://github.com/AnCode666), SVF-GFA, and JardiMargalefAgusti ([Apache License 2.0](LICENSE)).
See [NOTICE](NOTICE) for modification details.

## Differences from multiCAD-mcp

| Feature       | multiCAD-mcp          | kenchiku-mcp                      |
| ------------- | --------------------- | --------------------------------- |
| Block scaling | Uniform only (`1.5`)  | Uniform + non-uniform (`2.0x1.0`) |
| Focus         | General multi-CAD     | Architectural workflows (ZWCAD)   |
| stdout safety | StreamHandler(stdout) | StreamHandler(stderr)             |
| Logging       | multicad_mcp.log      | kenchiku_mcp.log                  |

## Non-uniform scaling

```
insert|WindowSash|100,0|4.213x1.0|0|window
```

`scale_x` **x** `scale_y` — width 4.213x, depth 1.0x.
Uniform scaling: `insert|Door|10,20|1.5|90|walls`

## Installation

```bash
git clone https://github.com/Sora-bluesky/kenchiku-mcp.git
cd kenchiku-mcp
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

## Claude Code configuration

```json
{
  "command": "<project-path>/.venv/Scripts/python.exe",
  "args": ["src/server.py"],
  "cwd": "<project-path>",
  "env": {
    "DOTENV_CONFIG_QUIET": "true",
    "PYTHONIOENCODING": "utf-8"
  }
}
```

Replace `<project-path>` with the absolute path to your cloned kenchiku-mcp directory.

Permission: `mcp__kenchiku__*`

## License

[Apache License 2.0](LICENSE) — includes code from [multiCAD-mcp](https://github.com/AnCode666/multiCAD-mcp).

---

# 日本語

[English](#kenchiku-mcp) | [日本語](#日本語)

ZWCAD 向け建築CAD MCP サーバー。非均一スケールによるブロック挿入に対応。

## 帰属

[multiCAD-mcp](https://github.com/AnCode666/multiCAD-mcp) v0.2.0 ([AnCode666](https://github.com/AnCode666), SVF-GFA, JardiMargalefAgusti 作、[Apache License 2.0](LICENSE)) をベースにしています。変更点は [NOTICE](NOTICE) を参照。

## multiCAD-mcp との違い

| 機能             | multiCAD-mcp          | kenchiku-mcp              |
| ---------------- | --------------------- | ------------------------- |
| ブロックスケール | 均一のみ (`1.5`)      | 均一 + 非均一 (`2.0x1.0`) |
| 対象             | 汎用マルチCAD         | 建築ワークフロー (ZWCAD)  |
| stdout安全性     | StreamHandler(stdout) | StreamHandler(stderr)     |
| ログファイル     | multicad_mcp.log      | kenchiku_mcp.log          |

## 非均一スケール

```
insert|WindowSash|100,0|4.213x1.0|0|window
```

`scale_x` **x** `scale_y` — 幅4.213倍、奥行1.0倍。
均一スケール: `insert|Door|10,20|1.5|90|walls`

## インストール

```bash
git clone https://github.com/Sora-bluesky/kenchiku-mcp.git
cd kenchiku-mcp
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

## Claude Code 設定

```json
{
  "command": "<project-path>/.venv/Scripts/python.exe",
  "args": ["src/server.py"],
  "cwd": "<project-path>",
  "env": {
    "DOTENV_CONFIG_QUIET": "true",
    "PYTHONIOENCODING": "utf-8"
  }
}
```

`<project-path>` をクローン先の絶対パスに置き換えてください。

パーミッション: `mcp__kenchiku__*`

## ライセンス

[Apache License 2.0](LICENSE) — [multiCAD-mcp](https://github.com/AnCode666/multiCAD-mcp) のコードを含みます。
