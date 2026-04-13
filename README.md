# kenchiku-mcp

Architectural CAD MCP server for ZWCAD with non-uniform block scaling.

## Attribution

This project is based on [multiCAD-mcp](https://github.com/AnCode666/multiCAD-mcp) v0.2.0, originally created by [AnCode666](https://github.com/AnCode666), SVF-GFA, and JardiMargalefAgusti, and licensed under the [Apache License 2.0](LICENSE).

See [NOTICE](NOTICE) for details on modifications.

## What's different from multiCAD-mcp

| Feature              | multiCAD-mcp         | kenchiku-mcp                      |
| -------------------- | -------------------- | --------------------------------- |
| Block insert scaling | Uniform only (`1.5`) | Uniform + non-uniform (`2.0x1.0`) |
| Focus                | General multi-CAD    | Architectural workflows (ZWCAD)   |

## Non-uniform scaling

```
insert|WindowSash|100,0|4.213x1.0|0|window
```

Format: `scale_x` **x** `scale_y` (e.g., `4.213x1.0` scales width 4.213x, keeps depth 1.0x).

Uniform scaling still works as before: `insert|Door|10,20|1.5|90|walls`

## Installation

```bash
git clone https://github.com/Sora-bluesky/kenchiku-mcp.git
cd kenchiku-mcp
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

## License

[Apache License 2.0](LICENSE)

This project includes code from [multiCAD-mcp](https://github.com/AnCode666/multiCAD-mcp) (Apache-2.0).
