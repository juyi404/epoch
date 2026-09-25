p = 'index.html'
s = open(p, encoding='utf-8').read()
a = s.index('/* ---------- Dust:')
b = s.index('/* ---------- Year streak')
s = s[:a] + r'''/* ---------- Galaxy: a tilted spiral disc turning slowly behind the timeline, with dust drifting toward the viewer ---------- */
const drift = (() => {
  const cv = $("#dust"), ctx = cv.getContext("2d", { alpha: false });
  let W, H, dpr = 1, bg, disc, running = !document.hidden, boost = 0, spin = 0, angle = 0, raf = 0, lastDraw = 0;
  let hx = innerWidth / 2, hxTo = hx; // 光晕中心，跟随焦点
  const mobile = innerWidth < 760;
  const TILT = -0.2, SQUASH = 0.34; // 星系盘的倾角与压扁程度
  // 三种星色：白、冷蓝白、暖金白
  const TINT = ["255,255,255", "214,226,255", "255,236,208"];
  const pts = [];
  const N = mobile ? 90 : 160;
  const spawn = (p, z) => {
    p.x = (Math.random() - 0.5) * 2.4; p.y = (Math.random() - 0.5) * 1.6;
    p.z = z ?? Math.random() * 0.9 + 0.1;
    p.tw = Math.random() * Math.PI * 2;
    p.c = TINT[Math.random() < 0.7 ? 0 : Math.random() < 0.6 ? 1 : 2];
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
    spin *= Math.pow(0.95, dt);
    // 常速约 12 分钟一圈，开场快转后减速，切换节点时顺着方向再推一把
    if (!reduceMotion) angle += (0.00014 + 0.004 * Math.exp(-t * 1.2) + spin) * dt;
    hx = reduceMotion ? hxTo : hx + (hxTo - hx) * (1 - Math.exp(-dt / 14));
    const cx = W * 0.5, cy = H * 0.58, f = Math.max(W, H) * 0.5;
    ctx.globalAlpha = 1;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.drawImage(bg, 0, 0);
    // 星系盘：先倾斜压扁成椭圆，再在盘面内自转，中心跟着焦点轻微漂移
    const gx = cx + (hx - cx) * 0.18, gy = H * 0.6;
    ctx.setTransform(dpr, 0, 0, dpr, dpr * gx, dpr * gy);
    ctx.rotate(TILT);
    ctx.scale(1, SQUASH);
    ctx.rotate(angle);
    ctx.drawImage(disc, -disc.width / 2 / dpr, -disc.height / 2 / dpr, disc.width / dpr, disc.height / dpr);
    // 光晕：横 46vw、纵 38vh 的椭圆，中心压在时间线附近
    ctx.setTransform(dpr * W * 0.46, 0, 0, dpr * H * 0.38, dpr * hx, dpr * H * 0.62);
    ctx.fillStyle = haze;
    ctx.fillRect(-1, -1, 2, 2);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const streak0 = Math.abs(boost) * 900;
    let cur = "";
    for (const p of pts) {
      p.z -= v;
      if (p.z <= 0.03) { spawn(p, 1); continue; }
      if (p.z > 1) { spawn(p, 0.1 + Math.random() * 0.2); continue; }
      const sx = cx + p.x / p.z * f, sy = cy + p.y / p.z * f;
      if (sx < -20 || sx > W + 20 || sy < -20 || sy > H + 20) { spawn(p, 1); continue; }
      const near = 1 - p.z;
      // 暗角：椭圆半径 120% × 95%，55% 以内不压暗
      const vx = (sx - cx) / (W * 1.2), vy = (sy - H * 0.5) / (H * 0.95);
      const vig = Math.min(1, Math.max(0, (Math.sqrt(vx * vx + vy * vy) - 0.55) / 0.45));
      ctx.globalAlpha = (0.08 + near * 0.55) * (0.75 + 0.25 * Math.sin(t * 1.3 + p.tw)) * (1 - vig);
      if (p.c !== cur) { cur = p.c; ctx.fillStyle = `rgb(${cur})`; }
      const r = 0.4 + near * 1.3;
      const streak = Math.min(24, streak0 * near); // 跳转时拉出短短的横向拖影
      ctx.fillRect(sx - r - streak, sy - r * 0.5, r * 2 + streak * 2, r);
    }
  }
  const haze = ctx.createRadialGradient(0, 0, 0, 0, 0, 1);
  haze.addColorStop(0, "rgba(255, 255, 255, 0.045)");
  haze.addColorStop(1, "rgba(255, 255, 255, 0)");
  // 颗粒：一块随机噪点平铺在黑底上，只在尺寸变化时生成一次
  const tile = document.createElement("canvas");
  tile.width = tile.height = 192;
  {
    const tc = tile.getContext("2d"), img = tc.createImageData(192, 192), d = img.data;
    for (let i = 0; i < d.length; i += 4) {
      d[i] = d[i + 1] = d[i + 2] = 255;
      d[i + 3] = (Math.random() + Math.random()) * 0.5 * 0.9 * 0.05 * 255;
    }
    tc.putImageData(img, 0, 0);
  }
  // 星系盘只画一次：核球 + 两条对数螺旋臂 + 盘面散星，之后每帧整张旋转贴上
  const seed = (() => { let x = 20221130; return () => (x = (x * 1664525 + 1013904223) >>> 0) / 4294967296; })();
  const gauss = () => { let u = 0, v = 0; while (!u) u = seed(); while (!v) v = seed(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
  function makeDisc() {
    const Rg = Math.max(W, H) * 0.62; // 盘半径（CSS 像素）
    const size = Math.ceil(Rg * 2 * dpr);
    const c = document.createElement("canvas");
    c.width = c.height = size;
    const g = c.getContext("2d");
    g.setTransform(dpr, 0, 0, dpr, size / 2, size / 2);
    // 盘面的乳白底光：核心亮、外缘散尽
    const glow = g.createRadialGradient(0, 0, 0, 0, 0, Rg);
    glow.addColorStop(0, "rgba(255, 244, 228, 0.16)");
    glow.addColorStop(0.12, "rgba(235, 236, 250, 0.07)");
    glow.addColorStop(0.45, "rgba(220, 226, 250, 0.022)");
    glow.addColorStop(1, "rgba(0, 0, 0, 0)");
    g.fillStyle = glow;
    g.fillRect(-Rg, -Rg, Rg * 2, Rg * 2);
    const star = (x, y, r, alpha, tint) => {
      g.globalAlpha = alpha;
      g.fillStyle = `rgb(${tint})`;
      g.fillRect(x - r, y - r, r * 2, r * 2);
    };
    const n = mobile ? 1400 : 2600;
    for (let i = 0; i < n; i++) {
      const u = seed();
      let r, th;
      if (u < 0.22) { // 核球：高斯团
        r = Math.abs(gauss()) * Rg * 0.1; th = seed() * Math.PI * 2;
      } else if (u < 0.78) { // 旋臂：r = a·e^(bθ)，两臂相差 180°，沿臂散开
        const arm = seed() < 0.5 ? 0 : Math.PI;
        const tt = seed() * 2.6;
        r = Rg * 0.07 * Math.exp(0.95 * tt) + gauss() * Rg * (0.02 + 0.045 * tt);
        th = tt + arm + gauss() * 0.16;
      } else { // 盘面散星：越靠外越稀
        r = Math.sqrt(seed()) * Rg * (0.5 + seed() * 0.5); th = seed() * Math.PI * 2;
      }
      if (r > Rg * 0.98) continue;
      const edge = 1 - Math.pow(r / Rg, 2.2); // 外缘渐隐
      const big = seed() < 0.06;
      const tint = TINT[seed() < 0.62 ? 0 : seed() < 0.55 ? 1 : 2];
      star(Math.cos(th) * r, Math.sin(th) * r, big ? 0.9 + seed() * 0.6 : 0.35 + seed() * 0.45, (big ? 0.5 : 0.14 + seed() * 0.3) * edge, tint);
    }
    return c;
  }
  const resize = () => {
    dpr = Math.min(devicePixelRatio || 1, 1.5);
    W = innerWidth; H = innerHeight;
    cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    bg = document.createElement("canvas");
    bg.width = cv.width; bg.height = cv.height;
    const bc = bg.getContext("2d", { alpha: false });
    bc.fillStyle = "#000";
    bc.fillRect(0, 0, bg.width, bg.height);
    bc.fillStyle = bc.createPattern(tile, "repeat");
    bc.fillRect(0, 0, bg.width, bg.height);
    // 暗角外圈把颗粒也压暗，和原来叠在上面的效果一致
    bc.setTransform(bg.width * 1.2, 0, 0, bg.height * 0.95, bg.width / 2, bg.height / 2);
    const vg = bc.createRadialGradient(0, 0, 0, 0, 0, 1);
    vg.addColorStop(0.55, "rgba(0, 0, 0, 0)");
    vg.addColorStop(1, "#000");
    bc.fillStyle = vg;
    bc.fillRect(-1, -1, 2, 2);
    disc = makeDisc();
    draw(performance.now());
  };
  // 开场加速和跳转拖影时满帧，平时星系转得极慢，30fps 足够
  const loop = now => {
    raf = 0;
    if (!running) return;
    const busy = now - t0 < 3000 || Math.abs(boost) > 0.0004 || Math.abs(hxTo - hx) > 0.5;
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
  const fn = dir => {
    if (reduceMotion) return;
    boost = Math.max(-0.02, Math.min(0.02, boost + 0.007 * dir));
    spin = Math.max(-0.012, Math.min(0.012, spin + 0.0025 * dir));
  };
  fn.focus = x => {
    if (x === hxTo) return;
    hxTo = x;
    if (reduceMotion) draw(performance.now());
  };
  return fn;
})();

''' + s[b:]
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
