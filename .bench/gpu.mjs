import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs"; import { tmpdir } from "node:os"; import { join } from "node:path";
const extra = process.argv.slice(2);
const port = 9900 + Math.floor(Math.random() * 90);
const proc = spawn("C:/Program Files/Google/Chrome/Application/chrome.exe", [`--remote-debugging-port=${port}`, `--user-data-dir=${mkdtempSync(join(tmpdir(), "g-"))}`, "--headless=new", ...extra, "about:blank"], { stdio: "ignore" });
const sleep = ms => new Promise(r => setTimeout(r, ms)); let ws;
for (let i = 0; i < 50; i++) { try { const l = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); const p = l.find(t => t.type === "page"); if (p) { ws = new WebSocket(p.webSocketDebuggerUrl); break; } } catch {} await sleep(200); }
await new Promise(r => ws.addEventListener("open", r));
ws.addEventListener("message", m => { const d = JSON.parse(m.data); if (d.id === 1) { console.log(extra.join(" ") || "(default)", "=>", d.result.result.value); ws.close(); proc.kill(); process.exit(0); } });
ws.send(JSON.stringify({ id: 1, method: "Runtime.evaluate", params: { expression: `(()=>{const g=document.createElement("canvas").getContext("webgl");if(!g)return "no webgl";const e=g.getExtension("WEBGL_debug_renderer_info");return g.getParameter(e.UNMASKED_RENDERER_WEBGL)})()`, returnByValue: true } }));
