// Validate every mermaid diagram in the repository against the real parser.
//
// GitHub renders these blocks with mermaid, so approximating the grammar with
// regular expressions is guesswork. This runs mermaid itself and reports what
// it actually says, mapped back to the source file and line.
//
//   npm install --no-save mermaid jsdom
//   node scripts/validate_mermaid.mjs
//
// Exits non-zero if any diagram fails to parse.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { JSDOM } from "jsdom";

const REPO_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const EXCLUDED = new Set([
  ".git",
  ".venv",
  ".venv-adk",
  "node_modules",
  "scratch",
  "assets",
]);

/** Recursively collect markdown files, skipping vendored and generated trees. */
function findMarkdown(dir) {
  const found = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (EXCLUDED.has(entry.name)) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      found.push(...findMarkdown(full));
    } else if (entry.isFile() && entry.name.endsWith(".md")) {
      found.push(full);
    }
  }
  return found;
}

/** Pull out fenced ```mermaid blocks, remembering where each one started. */
function extractBlocks(file) {
  const lines = fs.readFileSync(file, "utf8").split("\n");
  const blocks = [];
  let inside = false;
  let startLine = 0;
  let buffer = [];

  lines.forEach((line, i) => {
    const trimmed = line.trim();
    if (!inside && trimmed === "```mermaid") {
      inside = true;
      startLine = i + 1;
      buffer = [];
    } else if (inside && trimmed === "```") {
      inside = false;
      blocks.push({
        file: path.relative(REPO_ROOT, file),
        line: startLine,
        source: buffer.join("\n"),
      });
    } else if (inside) {
      buffer.push(line);
    }
  });

  if (inside) {
    blocks.push({
      file: path.relative(REPO_ROOT, file),
      line: startLine,
      source: buffer.join("\n"),
      unterminated: true,
    });
  }

  return blocks;
}

// mermaid needs a DOM even just to parse.
const dom = new JSDOM("<!DOCTYPE html><body></body>", { pretendToBeVisual: true });
global.window = dom.window;
global.document = dom.window.document;
// Node 22 defines globalThis.navigator as a getter, so plain assignment throws.
Object.defineProperty(global, "navigator", {
  value: dom.window.navigator,
  configurable: true,
  writable: true,
});

const mermaid = (await import("mermaid")).default;
mermaid.initialize({ startOnLoad: false, securityLevel: "loose" });

console.log(`mermaid ${mermaid.version ? mermaid.version() : ""}`.trim());

const blocks = findMarkdown(REPO_ROOT).flatMap(extractBlocks);
let failures = 0;

for (const block of blocks) {
  const where = `${block.file}:${block.line}`;

  if (block.unterminated) {
    failures += 1;
    console.log(`FAIL  ${where}  unterminated \`\`\`mermaid fence`);
    continue;
  }

  try {
    await mermaid.parse(block.source);
    console.log(`PASS  ${where}`);
  } catch (error) {
    failures += 1;
    const message = (error && (error.str || error.message)) || String(error);
    console.log(`FAIL  ${where}`);
    console.log(
      String(message)
        .split("\n")
        .map((l) => `        ${l}`)
        .join("\n"),
    );
    console.log("");
  }
}

console.log("");
console.log(`${blocks.length - failures}/${blocks.length} diagrams parse cleanly.`);

if (failures > 0) {
  console.log("");
  console.log("The usual cause is an unquoted ( ) [ ] { } inside a label.");
  console.log('Quote it:  A["Label (detail)"]  and  A -->|"1. Step (detail)"| B');
}

process.exit(failures > 0 ? 1 : 0);
