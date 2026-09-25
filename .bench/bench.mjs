// 用法: node .bench/bench.mjs <url> [label]
// 通过 CDP 驱动 Chrome：等页面启动后连续切换 40 个节点，再空闲 4 秒，统计帧与主线程开销。
import { spawn } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const url = process.argv[2];
const label = process.argv[3] || url;
const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const port = 9300 + Math.floor(Math.random() * 500);
const proc = spawn(CHROME, [
  `--remote-debugging-port=${port}`, `--user-data-dir=${mkdtempSync(join(tmpdir(), "bench-"))}`,
  "--headless=new", "--window-size=1536,760", "--force-device-scale-factor=2",
  "--no-first-run", "--disable-extensions", "about:blank",
], { stdio: "ignore" });

const sleep = ms => new Promise(r => setTimeout(r, ms));
let ws;
for (let i = 0; i < 50; i++) {
  try {
    const list = await (await fetch(`http://127.0.0.1:${port}/json`)).json();
    const page = list.find(t => t.type === "page");
    if (page) { ws = new WebSocket(page.webSocketDebuggerUrl); break; }
  } catch {}
  await sleep(200);
}
await new Promise(r => ws.addEventListener("open", r, { once: true }));
let id = 0; const pending = new Map();
ws.addEventListener("message", m => { const d = JSON.parse(m.data); if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); } });
const send = (method, params = {}) => new Promise(r => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const evalJs = async expr => (await send("Runtime.evaluate", { expression: expr, awaitPromise: true, returnByValue: true })).result?.result?.value;

await send("Performance.enable");
await send("Page.enable");
await send("Emulation.setDeviceMetricsOverride", { width: 1536, height: 760, deviceScaleFactor: 2, mobile: false });
await send("Page.navigate", { url });
await sleep(6000); // 等字体 + 启动动画
if (process.argv[4]) await evalJs(`(() => { const s = document.createElement("style"); s.textContent = ${JSON.stringify(process.argv[4])}; document.head.append(s); })()`);
await sleep(300);

const metrics = async () => Object.fromEntries((await send("Performance.getMetrics")).result.metrics.map(m => [m.name, m.value]));
const FRAMES = `(() => { const out = []; let last = performance.now(), on = true;
  const f = t => { out.push(t - last); last = t; if (on) requestAnimationFrame(f); }; requestAnimationFrame(f);
  window.__stopFrames = () => { on = false; return out; }; })()`;

async function phase(name, body) {
  await evalJs(FRAMES);
  const a = await metrics();
  await body();
  const b = await metrics();
  const fr = await evalJs("__stopFrames()");
  fr.shift();
  fr.sort((x, y) => x - y);
  const d = k => +(b[k] - a[k]).toFixed(3);
  const p = q => +fr[Math.floor(q * (fr.length - 1))].toFixed(1);
  return {
    phase: name, frames: fr.length, p50: p(0.5), p95: p(0.95), max: p(1),
    janky: fr.filter(x => x > 20).length,
    layouts: d("LayoutCount"), styles: d("RecalcStyleCount"),
    layoutMs: +(d("LayoutDuration") * 1000).toFixed(1), styleMs: +(d("RecalcStyleDuration") * 1000).toFixed(1),
    scriptMs: +(d("ScriptDuration") * 1000).toFixed(1), taskMs: +(d("TaskDuration") * 1000).toFixed(1),
  };
}

const rows = [];
rows.push(await phase("navigate x40", async () => {
  for (let i = 0; i < 40; i++) {
    await send("Input.dispatchKeyEvent", { type: "keyDown", key: "ArrowRight", code: "ArrowRight", windowsVirtualKeyCode: 39 });
    await send("Input.dispatchKeyEvent", { type: "keyUp", key: "ArrowRight", code: "ArrowRight", windowsVirtualKeyCode: 39 });
    await sleep(150);
  }
  await sleep(1200);
}));
rows.push(await phase("idle 4s", () => sleep(4000)));
const errs = await evalJs("window.__errs || []");
console.log(JSON.stringify({ label, rows, errs }));
ws.close(); proc.kill();
process.exit(0);
