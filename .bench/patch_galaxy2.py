p = 'index.html'
s = open(p, encoding='utf-8').read()


def R(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)


# 位置：盘心放到屏幕正中，只随焦点极轻微漂移；倾角稍大一点，旋臂走对角线
R('const TILT = -0.14, SQUASH = 0.5;', 'const TILT = -0.22, SQUASH = 0.56;')
R('const gx = cx + (hx - cx) * 0.18, gy = H * 0.6;', 'const gx = cx + (hx - cx) * 0.08, gy = H * 0.5;')

a = s.index('  function makeDisc() {')
b = s.index('    c.R = Rg;\n    return c;\n  }', a)
s = s[:a] + r'''  function makeDisc() {
    const Rg = Math.max(W, H) * 0.95; // 盘半径（CSS 像素），旋臂能扫过整个视口
    const k = Math.min(dpr, 3000 / (Rg * 2)); // 离屏画布封顶 3000px，省显存
    const size = Math.ceil(Rg * 2 * k);
    const c = document.createElement("canvas");
    c.width = c.height = size;
    const g = c.getContext("2d");
    g.setTransform(k, 0, 0, k, size / 2, size / 2);
    const A = 0.055, B = 0.9, TMAX = 3.3; // 对数螺旋 r = A·Rg·e^(B·θ)，每条臂绕约 190°
    const armR = tt => Rg * A * Math.exp(B * tt);
    const soft = (x, y, w, rgb, alpha) => { // 一团柔光
      const gr = g.createRadialGradient(x, y, 0, x, y, w);
      gr.addColorStop(0, `rgba(${rgb}, ${alpha.toFixed(3)})`);
      gr.addColorStop(0.5, `rgba(${rgb}, ${(alpha * 0.35).toFixed(3)})`);
      gr.addColorStop(1, `rgba(${rgb}, 0)`);
      g.fillStyle = gr;
      g.fillRect(x - w, y - w, w * 2, w * 2);
    };
    // 沿臂的明暗起伏：几段正弦叠出来，让臂有疏密而不是一根均匀的管子
    const ripple = (tt, ph) => 0.7 + 0.3 * Math.sin(tt * 3.1 + ph) * Math.sin(tt * 1.7 + ph * 0.6 + 1);
    // 1. 盘面底光：核心暖白，往外迅速转成冷蓝灰，占整个盘
    const glow = g.createRadialGradient(0, 0, 0, 0, 0, Rg);
    glow.addColorStop(0, "rgba(255, 240, 220, 0.42)");
    glow.addColorStop(0.05, "rgba(250, 238, 224, 0.2)");
    glow.addColorStop(0.16, "rgba(226, 230, 248, 0.07)");
    glow.addColorStop(0.5, "rgba(214, 222, 248, 0.03)");
    glow.addColorStop(1, "rgba(0, 0, 0, 0)");
    g.fillStyle = glow;
    g.fillRect(-Rg, -Rg, Rg * 2, Rg * 2);
    // 2. 两条主臂 + 两条弱一半的副臂（错开 90°），副臂只到一半长
    const arms = [[0, 1, TMAX], [Math.PI, 1, TMAX], [Math.PI / 2, 0.42, TMAX * 0.62], [-Math.PI / 2, 0.42, TMAX * 0.62]];
    arms.forEach(([off, str, tmax], ai) => {
      for (let tt = 0.15; tt < tmax; tt += 0.035) {
        const r = armR(tt), th = tt + off;
        const w = Rg * (0.022 + 0.052 * tt);
        const fade = Math.pow(1 - tt / (tmax + 0.4), 1.4) * ripple(tt, ai * 2.3);
        soft(Math.cos(th) * r, Math.sin(th) * r, w, "222, 228, 250", 0.075 * str * fade);
      }
    });
    // 3. 尘埃带：贴着每条主臂内侧压一道暗痕，臂就有了"厚度"
    arms.slice(0, 2).forEach(([off]) => {
      for (let tt = 0.5; tt < TMAX * 0.9; tt += 0.035) {
        const r = armR(tt) * 0.9, th = tt + off;
        const w = Rg * (0.008 + 0.02 * tt), fade = (1 - tt / TMAX) * 0.5;
        soft(Math.cos(th) * r, Math.sin(th) * r, w, "0, 0, 0", fade);
      }
    });
    // 4. 星点
    const star = (x, y, r, alpha, tint) => {
      g.globalAlpha = alpha;
      g.fillStyle = `rgb(${tint})`;
      g.fillRect(x - r, y - r, r * 2, r * 2);
    };
    const n = mobile ? 3200 : 6500;
    for (let i = 0; i < n; i++) {
      const u = seed();
      let r, th, onArm = 0;
      if (u < 0.16) { // 核球：高斯团
        r = Math.abs(gauss()) * Rg * 0.07; th = seed() * Math.PI * 2;
      } else if (u < 0.84) { // 旋臂：沿臂密度跟着柔光的疏密走
        const [off, str, tmax] = arms[seed() < 0.8 ? (seed() < 0.5 ? 0 : 1) : (seed() < 0.5 ? 2 : 3)];
        const tt = 0.1 + Math.sqrt(seed()) * (tmax - 0.1);
        if (seed() > ripple(tt, 0) * str) continue;
        r = armR(tt) + gauss() * Rg * (0.008 + 0.03 * tt);
        th = tt + off + gauss() * 0.08;
        onArm = 1;
      } else { // 盘面散星：越靠外越稀
        r = Math.sqrt(seed()) * Rg * (0.35 + seed() * 0.65); th = seed() * Math.PI * 2;
      }
      if (r > Rg * 0.98) continue;
      const edge = 1 - Math.pow(r / Rg, 2.4); // 外缘渐隐
      const x = Math.cos(th) * r, y = Math.sin(th) * r;
      const big = seed() < 0.09;
      // 臂上多蓝白的年轻星，核球偏暖
      const tint = TINT[seed() < (onArm ? 0.5 : 0.7) ? 0 : seed() < (r < Rg * 0.12 ? 0.25 : 0.75) ? 1 : 2];
      if (big && seed() < 0.3) soft(x, y, 3 + seed() * 4, tint, 0.35 * edge); // 少数亮星带一圈光晕
      star(x, y, big ? 1.1 + seed() * 0.9 : 0.5 + seed() * 0.5, (big ? 1 : 0.4 + seed() * 0.5) * edge, tint);
    }
    g.globalAlpha = 1;
''' + s[b:]
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
