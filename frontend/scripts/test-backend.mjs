// Browser tests start their own backend with disposable storage and no API key.
import { spawn } from "node:child_process";
import { mkdtempSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const root = resolve("..");
const folder = mkdtempSync(join(tmpdir(), "incidentlens-browser-"));
const localPython = join(
  root,
  "venv",
  process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
);
const child = spawn(
  existsSync(localPython) ? localPython : "python",
  ["-m", "uvicorn", "backend.app.main:app", "--port", "8010"],
  {
    cwd: root,
    stdio: "inherit",
    env: {
      ...process.env,
      DATABASE_URL: `sqlite:///${join(folder, "test.db").replaceAll("\\", "/")}`,
      CHROMA_PATH: join(folder, "chroma"),
      GEMINI_API_KEY: "",
      DEBUG: "false",
    },
  },
);
child.on("exit", (code) => process.exit(code || 0));
for (const signal of ["SIGINT", "SIGTERM"])
  process.on(signal, () => child.kill(signal));
