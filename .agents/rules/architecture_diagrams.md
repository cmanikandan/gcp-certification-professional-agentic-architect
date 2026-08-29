---
name: architecture-diagrams-nanobanana
description: Enforces that all architecture and technical workflow diagrams in this codebase and project are generated visually using nanobanana (the generate_image tool).
always_on: true
---

# Architecture Diagram Generation Policy (Nanobanana)

## Mandatory Guidelines
1. **Tool Usage**: Whenever creating, updating, or referencing architecture diagrams, multi-agent topologies, security workflows, or system designs in this project, you **MUST** generate a visual diagram image using `generate_image` (nanobanana).
2. **Visual Style**: Diagrams must follow clean, high-resolution, modern Google Cloud dark/blue technical schematic aesthetics.
3. **Storage & Linking**: Store generated diagram images in `assets/diagrams/` and embed them into markdown documentation files (`README.md`, `STUDY_GUIDE.md`, module guides) using standard markdown image syntax: `![Diagram Description](../../assets/diagrams/<name>.jpg)` or `![Diagram Description](assets/diagrams/<name>.jpg)`.
4. **Exceptions**: Do not use ASCII or plain Mermaid code blocks as the sole diagram format when visual nanobanana diagrams can be provided, unless explicitly requested by the user.
