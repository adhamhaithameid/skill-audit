#!/usr/bin/env node
const { spawnSync } = require("child_process");
const path = require("path");
const script = path.join(__dirname, "..", "skills", "skill-audit", "scripts", "audit.py");
const r = spawnSync("python3", [script, ...process.argv.slice(2)], { stdio: "inherit" });
if (r.error) {
  console.error("skill-audit needs Python 3.9 or newer. Install Python, then retry.");
  process.exit(1);
}
process.exit(r.status === null ? 1 : r.status);