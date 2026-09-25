p = 'index.html'
s = open(p, encoding='utf-8').read()


def R(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80])
    s = s.replace(a, b)


def between(start, end, new):
    global s
    a = s.index(start)
    b = s.index(end)
    s = s[:a] + new + s[b:]


# ---- dust: 不透明画布、像素比封顶 1.5、空闲 30fps、减弱动效时只画一帧
between('/* ---------- Dust:', '/* ---------- Year streak', r'''/* ---------- Dust: sparse white particles drifting toward the viewer ---------- */
const drift = (() => {
  const cv = $("#dust"), ctx = cv.getContext("2d", { alpha: false });
  let W, H, running = !document.hidden, boost = 0, raf = 0, lastDraw = 0;
  const pts = [];
  const N = innerWidth < 760 ? 110 : 200;
  const spawn = (p, z) => {
    p.x = (Math.random() - 0.5) * 2.4; p.y = (Math.random() - 0.5) * 1.6;
    p.z = z ?? Math.random() * 0.9 + 0.1;
    p.tw = Math.random() * Math.PI * 2;
    return p;
  };
  for (let i = 0; i < N; i++) pts.push(spawn({}));
  const t0 = performance.now();
  function draw(now) {
    const t = (now - t0) / 1000;
    const dt = Math.min(3, lastDraw ? (now - lastDraw) / 16.7 : 1); // 以 60fps 为 1，降帧时步长同比放大
    lastDraw = now;
    const v = reduceMotion ? 0 : (0.00022 + 0.008 * Math.exp(-t * 1.2) + boost) * dt;
    boost *= Math.pow(0.94, dt);
    const cx = W * 0.5, cy = H * 0.58, f = Math.max(W, H) * 0.5;
    ctx.globalAlpha = 1;
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = "#fff";
    const streak0 = Math.abs(boost) * 900;
    for (const p of pts) {
      p.z -= v;
      if (p.z <= 0.03) { spawn(p, 1); continue; }
      if (p.z > 1) { spawn(p, 0.1 + Math.random() * 0.2); continue; }
      const sx = cx + p.x / p.z * f, sy = cy + p.y / p.z * f;
      if (sx < -20 || sx > W + 20 || sy < -20 || sy > H + 20) { spawn(p, 1); continue; }
      const near = 1 - p.z;
      ctx.globalAlpha = (0.08 + near * 0.55) * (0.75 + 0.25 * Math.sin(t * 1.3 + p.tw));
      const r = 0.4 + near * 1.3;
      const streak = Math.min(24, streak0 * near); // 跳转时拉出短短的横向拖影
      ctx.fillRect(sx - r - streak, sy - r * 0.5, r * 2 + streak * 2, r);
    }
  }
  const resize = () => {
    const dpr = Math.min(devicePixelRatio || 1, 1.5);
    W = innerWidth; H = innerHeight;
    cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    draw(performance.now());
  };
  // 开场加速和跳转拖影时满帧，平时粒子几乎不动，30fps 足够
  const loop = now => {
    raf = 0;
    if (!running) return;
    const busy = now - t0 < 3000 || Math.abs(boost) > 0.0004;
    if (busy || now - lastDraw >= 32) draw(now);
    raf = requestAnimationFrame(loop);
  };
  const start = () => { if (!reduceMotion && running && !raf) { lastDraw = 0; raf = requestAnimationFrame(loop); } };
  resize();
  addEventListener("resize", resize);
  start();
  document.addEventListener("visibilitychange", () => {
    running = !document.hidden;
    if (running) start(); else { cancelAnimationFrame(raf); raf = 0; }
  });
  return dir => { if (!reduceMotion) boost = Math.max(-0.02, Math.min(0.02, boost + 0.007 * dir)); };
})();

''')

# ---- streak: 只动 transform/opacity，交给合成线程
between('/* ---------- Year streak', '/* ---------- Events ---------- */', r'''/* ---------- Year streak: 换年时拖影从很长收回来（只动 transform/opacity，走合成线程） ---------- */
const ghostText = $("#ghostText");
function streak() {
  if (reduceMotion || !ghostText.animate) return;
  ghostText.animate(
    [{ transform: "scaleX(1.6)", opacity: 0 }, { transform: "scaleX(1.12)", opacity: 1, offset: 0.35 }, { transform: "none", opacity: 1 }],
    { duration: 900, easing: "cubic-bezier(.2, .8, .2, 1)" }
  );
}

''')

# ---- 度量缓存：只在启动和尺寸变化时读一次计算样式
R('''const padX = () => parseFloat(getComputedStyle($("#app")).paddingLeft) || 40;
const radius = () => parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--R")) || 56;
''', r'''const M = {};
function measure() {
  M.W = stage.clientWidth; M.H = stage.clientHeight;
  M.left = stage.getBoundingClientRect().left;
  M.px = parseFloat(getComputedStyle($("#app")).paddingLeft) || 40;
  M.R = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--R")) || 56;
  M.pw = panel.offsetWidth;
  M.gw = ghost.offsetWidth; M.gh = ghost.offsetHeight;
}
// 只在值变化时写入，避免每次切换都让 71 个节点重新算样式
const put = (el, key, val, write) => { if (el[key] !== val) { el[key] = val; write(val); } };
const setTf = (el, v) => put(el, "_tf", v, v => { el.style.transform = v; });
const setOp = (el, v) => put(el, "_op", v, v => { el.style.opacity = v; });
const setCls = (el, name, on) => { if (el.classList.contains(name) !== on) el.classList.toggle(name, on); };
''')
R('''function makeXs() {
  const W = stage.clientWidth;
  const px = padX();
  const r = radius() * 0.8;''', '''function makeXs() {
  const W = M.W;
  const px = M.px;
  const r = M.R * 0.8;''')

between('function layout() {', '/* ---------- Focus ---------- */', r'''function layout() {
  const { H, W, R, px, pw, gw, gh } = M;
  const railY = Math.round(H * (W < 760 ? 0.8 : 0.78));
  put(rail, "_top", railY, v => { rail.style.top = v + "px"; });

  const n = vis.length, xs = makeXs(), wide = W >= 760;
  const near = new Set(), named = new Map();
  // 标签从焦点往两侧贪心铺开：彼此不挤、也不钻进日蚀
  const minGap = wide ? 66 : 50, cx0 = xs[k];
  [-1, 1].forEach(dir => {
    const side = [];
    let last = cx0;
    for (let i = k + dir, step = 1; i >= 0 && i < n && step <= 6; i += dir, step++) {
      const x = xs[i];
      if (Math.abs(x - cx0) < R + 26) continue;
      if (Math.abs(x - last) < (last === cx0 ? R + 26 : minGap)) continue;
      near.add(i);
      side.push(i);
      last = x;
    }
    // 最靠近焦点的两个标签写出事件名，宽度按左右可用空间算，最多两行
    if (!wide) return;
    let prevHalf = 0;
    side.slice(0, 2).forEach((i, j) => {
      const next = side[j + 1];
      const inner = j === 0 ? Math.abs(xs[i] - cx0) - R - 10 : Math.abs(xs[i] - xs[side[j - 1]]) - prevHalf - 8;
      const outer = next === undefined ? 90 : Math.abs(xs[next] - xs[i]) - 20;
      const half = Math.min(inner, outer, 80);
      if (half >= 40) { named.set(i, Math.floor(half * 2)); prevHalf = half; }
      else prevHalf = 17;
    });
  });

  const shown = new Set(vis);
  dots.forEach(el => { if (!shown.has(el) && !el.hidden) el.hidden = true; });
  vis.forEach((el, i) => {
    if (el.hidden) el.hidden = false;
    setTf(el, `translateX(${xs[i].toFixed(1)}px)`);
    const gapL = i > 0 ? xs[i] - xs[i - 1] : 1e9, gapR = i < n - 1 ? xs[i + 1] - xs[i] : 1e9;
    setCls(el, "tick", Math.min(gapL, gapR) < (el._e.m ? 16 : 11));
    setOp(el, Math.max(0.35, 1 - Math.abs(i - k) / 16).toFixed(2));
    setCls(el, "near", near.has(i));
    setCls(el, "named", named.has(i));
    setCls(el, "cur", i === k);
    put(el, "_lw", named.get(i), v => v ? el.style.setProperty("--lw", v + "px") : el.style.removeProperty("--lw"));
  });

  // 年份刻度放在跨年的两个节点之间
  const curYear = vis[k]?._e.d.slice(0, 4);
  const seen = [], used = new Set();
  vis.forEach((el, i) => {
    const y = el._e.d.slice(0, 4);
    if (i === 0 || vis[i - 1]._e.d.slice(0, 4) !== y) {
      const x = i === 0 ? xs[0] - 14 : (xs[i - 1] + xs[i]) / 2;
      const t = yearTicks[y], end = x > W - 70;
      used.add(t);
      setOp(t, "1");
      setTf(t, `translateX(${x.toFixed(1)}px)`);
      setCls(t, "cur", y === curYear);
      setCls(t, "end", end);
      setCls(t, "under", Math.abs(x + (end ? -25 : 25) - xs[k]) < R + 30);
      seen.push([end ? x - 50 : x, t]); // 标签实际起点
    }
  });
  Object.values(yearTicks).forEach(t => { if (!used.has(t)) setOp(t, "0"); });
  seen.forEach(([x, t], j) => setCls(t, "tight", j < seen.length - 1 && seen[j + 1][0] - x < 52));

  const cx = xs[k] ?? W / 2, x0 = (xs[0] ?? cx) - 14;
  setTf(eclipse, `translateX(${cx.toFixed(1)}px)`);
  setTf(railLit, `translateX(${x0.toFixed(1)}px) scaleX(${(Math.max(0, cx - R - x0) / 1000).toFixed(4)})`);
  setTf(haze, `translateX(${cx.toFixed(1)}px)`);

  // 大年份跟着焦点做轻微视差，竖直居中压在时间线上
  const gx = (W - gw) / 2 + (cx - W / 2) * 0.35;
  setTf(ghost, `translate(${gx.toFixed(1)}px, ${(railY - gh / 2).toFixed(1)}px)`);

  // 面板跟随焦点，但不出屏
  const left = Math.max(px, Math.min(W - px - pw, cx - pw * 0.3));
  const bottom = railY - R - (W < 760 ? 20 : 26);
  put(panel, "_bottom", H - bottom, v => { panel.style.bottom = v + "px"; });
  setTf(panel, `translateX(${left.toFixed(1)}px)`);
  put(leader, "_geo", `${bottom}/${railY - R - bottom}`, () => { leader.style.top = bottom + "px"; leader.style.height = (railY - R - bottom) + "px"; });
  setTf(leader, `translateX(${cx.toFixed(1)}px)`);
}

''')

# ---- render：同一帧内多次切换只渲染一次；换年时才量一次大年份尺寸
R('''function render() {
  const el = vis[k]; if (!el) return;''', r'''let renderRaf = 0;
function schedule() {
  if (!renderRaf) renderRaf = requestAnimationFrame(() => { renderRaf = 0; render(); });
}

const $chapter = $("#chapter"), $seq = $("#seq"), $pdate = $("#pdate"), $ptplus = $("#ptplus"), $ptitle = $("#ptitle"),
  $pdesc = $("#pdesc"), $porg = $("#porg"), $pcat = $("#pcat"), $pgap = $("#pgap"), $prev = $("#prev"), $next = $("#next"), $live = $("#live");
let shownEl = null;
function render() {
  cancelAnimationFrame(renderRaf); renderRaf = 0;
  const el = vis[k]; if (!el) return;
  if (shownEl === el) { layout(); return; }
  shownEl = el;''')
R('''  if (ghost.textContent !== y) { ghost.textContent = y; streak(); }
  $("#chapter").innerHTML = `<b>${y}</b>${YEARS[y][0]}`;
  $("#seq").textContent = `${String(k + 1).padStart(2, "0")} / ${vis.length}`;
  const pdate = $("#pdate");
  pdate.textContent = fmtDate(e.d);
  pdate.setAttribute("datetime", e.d);
  const tplus = Math.round((e.time - LAUNCH_DAY) / DAY);
  $("#ptplus").textContent = `T+${e.d.length === 7 ? "约 " : ""}${tplus} 天`;
  decode($("#ptitle"), e.t);
  const desc = $("#pdesc");
  desc.textContent = e.x;
  desc.classList.remove("in");
  void desc.offsetWidth;
  desc.classList.add("in");
  $("#porg").textContent = e.o;
  $("#pcat").textContent = c.name;''', r'''  if (ghostText.textContent !== y) {
    ghostText.textContent = y;
    M.gw = ghost.offsetWidth; M.gh = ghost.offsetHeight;
    streak();
  }
  $chapter.innerHTML = `<b>${y}</b>${YEARS[y][0]}`;
  $seq.textContent = `${String(k + 1).padStart(2, "0")} / ${vis.length}`;
  $pdate.textContent = fmtDate(e.d);
  $pdate.setAttribute("datetime", e.d);
  const tplus = Math.round((e.time - LAUNCH_DAY) / DAY);
  $ptplus.textContent = `T+${e.d.length === 7 ? "约 " : ""}${tplus} 天`;
  decode($ptitle, e.t);
  $pdesc.textContent = e.x;
  if (!reduceMotion && $pdesc.animate) $pdesc.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 500, easing: "ease-out" });
  $porg.textContent = e.o;
  $pcat.textContent = c.name;''')
R('''  $("#pgap").textContent = e.d.length === 7''', '''  $pgap.textContent = e.d.length === 7''')
R('''  $("#prev").disabled = k <= 0;
  $("#next").disabled = k >= vis.length - 1;''', '''  $prev.disabled = k <= 0;
  $next.disabled = k >= vis.length - 1;''')
R('''  $("#live").textContent = `${fmtDate(e.d)}，${e.t}。${e.x}`;''', '''  $live.textContent = `${fmtDate(e.d)}，${e.t}。${e.x}`;''')
R('''  drift(dir);
  render();
}''', '''  drift(dir);
  schedule();
}''')

# ---- scrub：用缓存的舞台位置，拖动时不强制布局
R('''  const r = stage.getBoundingClientRect();
  const px = padX();
  const L = r.left + px + radius() * 0.8, R = r.right - px - radius() * 0.8;''', '''  const L = M.left + M.px + M.R * 0.8, R = M.left + M.W - M.px - M.R * 0.8;''')

# ---- 筛选后序号和总数会变，强制重渲面板
R('''  $("#hint").textContent = `滚动滚轮、按方向键，或沿时间线拖动，共 ${vis.length} 个节点`;
  render();''', '''  $("#hint").textContent = `滚动滚轮、按方向键，或沿时间线拖动，共 ${vis.length} 个节点`;
  shownEl = null;
  render();''')

# ---- 启动：字体最多等 1.2 秒，不让中文字体下载卡住首屏
R('''let resizeT;
addEventListener("resize", () => { clearTimeout(resizeT); resizeT = setTimeout(layout, 100); });
(document.fonts?.ready || Promise.resolve()).then(() => {
  applyFilter();''', '''let resizeT;
addEventListener("resize", () => { clearTimeout(resizeT); resizeT = setTimeout(() => { measure(); layout(); }, 100); });
// 字体晚到时字宽会变，重新量一次
document.fonts?.addEventListener?.("loadingdone", () => { if (M.W) { measure(); layout(); } });
Promise.race([document.fonts?.ready || Promise.resolve(), new Promise(r => setTimeout(r, 1200))]).then(() => {
  measure();
  applyFilter();''')

open(p, 'w', encoding='utf-8', newline='\n').write(s)
print("ok")
