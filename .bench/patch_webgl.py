p = 'index.html'
s = open(p, encoding='utf-8').read()


def R(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:70])
    s = s.replace(a, b)


R('''  #dust { position: fixed; inset: 0; width: 100%; height: 100%; background: #000; }''',
  '''  #galaxy { position: fixed; inset: 0; width: 100%; height: 100%; background: #000; }
  #dust { position: fixed; inset: 0; width: 100%; height: 100%; }''')
R('''<canvas id="dust" aria-hidden="true"></canvas>''',
  '''<canvas id="galaxy" aria-hidden="true"></canvas>
<canvas id="dust" aria-hidden="true"></canvas>''')

a = s.index('/* ---------- Galaxy: a tilted')
b = s.index('/* ---------- Year streak')
s = s[:a] + r'''/* ---------- Galaxy: WebGL 上一张真正透视的旋转星系盘；上层 2D 画布只画核球光、光晕和前景粒子 ---------- */
const drift = (() => {
  const cv = $("#dust"), ctx = cv.getContext("2d");
  const gcv = $("#galaxy");
  const GLO = { alpha: false, antialias: false, depth: false, stencil: false, powerPreference: "low-power" };
  const gl = gcv.getContext("webgl2", GLO) || gcv.getContext("webgl", GLO);
  let W, H, dpr = 1, bg, disc, running = !document.hidden, boost = 0, spin = 0, angle = 0, raf = 0, lastDraw = 0;
  let hx = innerWidth / 2, hxTo = hx; // 光晕中心，跟随焦点
  const mobile = innerWidth < 760;
  const TILT = -0.22, INC = Math.acos(0.56); // 盘面绕视线的倾角，以及绕水平轴的倾斜（决定椭圆的扁度）
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

  /* ---- 4x4 矩阵（列主序），只够用 ---- */
  const I4 = new Float32Array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]);
  const mul = (a, b) => {
    const o = new Float32Array(16);
    for (let c = 0; c < 4; c++) for (let r = 0; r < 4; r++) {
      let v = 0;
      for (let k = 0; k < 4; k++) v += a[k * 4 + r] * b[c * 4 + k];
      o[c * 4 + r] = v;
    }
    return o;
  };
  const Rz = a => { const c = Math.cos(a), s = Math.sin(a); return new Float32Array([c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]); };
  const Rx = a => { const c = Math.cos(a), s = Math.sin(a); return new Float32Array([1, 0, 0, 0, 0, c, s, 0, 0, -s, c, 0, 0, 0, 0, 1]); };
  const Sc = k => new Float32Array([k, 0, 0, 0, 0, k, 0, 0, 0, 0, k, 0, 0, 0, 0, 1]);
  const Tr = (x, y) => new Float32Array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, x, y, 0, 1]);
  const Persp = F => { const m = new Float32Array(I4); m[11] = -1 / F; return m; }; // w = 1 - z/F，观众在 +z 方向 F 处
  const Ortho = () => new Float32Array([2 / W, 0, 0, 0, 0, -2 / H, 0, 0, 0, 0, 0, 0, -1, 1, 0, 1]); // CSS 像素 → NDC

  /* ---- WebGL：一个着色器，画两张贴图（黑底颗粒、星系盘） ---- */
  let prog, uM, uMV, uFade, texBg, texDisc, aniso;
  if (gl) {
    const sh = (type, src) => { const o = gl.createShader(type); gl.shaderSource(o, src); gl.compileShader(o); return o; };
    prog = gl.createProgram();
    gl.attachShader(prog, sh(gl.VERTEX_SHADER, `attribute vec2 p; uniform mat4 m, mv; varying vec2 uv; varying float dz;
      void main() { gl_Position = m * vec4(p, 0., 1.); uv = p * .5 + .5; dz = (mv * vec4(p, 0., 1.)).z; }`));
    gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, `precision mediump float; uniform sampler2D t; uniform vec2 fade; varying vec2 uv; varying float dz;
      void main() { vec4 c = texture2D(t, uv); float f = clamp(.5 + dz / fade.x, 0., 1.); gl_FragColor = c * mix(fade.y, 1., f); }`));
    gl.linkProgram(prog);
    gl.useProgram(prog);
    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    const ap = gl.getAttribLocation(prog, "p");
    gl.enableVertexAttribArray(ap);
    gl.vertexAttribPointer(ap, 2, gl.FLOAT, false, 0, 0);
    uM = gl.getUniformLocation(prog, "m"); uMV = gl.getUniformLocation(prog, "mv"); uFade = gl.getUniformLocation(prog, "fade");
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA); // 贴图按预乘 alpha 上传
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, true);
    aniso = gl.getExtension("EXT_texture_filter_anisotropic");
  }
  const upload = (tex, src, mip) => {
    tex = tex || gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, src);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, mip ? gl.LINEAR_MIPMAP_LINEAR : gl.LINEAR);
    if (mip) {
      gl.generateMipmap(gl.TEXTURE_2D);
      // 各向异性过滤：盘是斜着看的，远端缩得很厉害，没有它星星会糊成一片
      if (aniso) gl.texParameterf(gl.TEXTURE_2D, aniso.TEXTURE_MAX_ANISOTROPY_EXT, Math.min(8, gl.getParameter(aniso.MAX_TEXTURE_MAX_ANISOTROPY_EXT)));
    }
    return tex;
  };

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
    // 星系盘：中心跟着焦点轻微漂移；视角极缓慢地摆动，像镜头在绕着它漂
    const Rg = disc.R, gx = cx + (hx - cx) * 0.08, gy = H * 0.5;
    const tilt = TILT + (reduceMotion ? 0 : 0.03 * Math.sin(t / 9)), inc = INC + (reduceMotion ? 0 : 0.05 * Math.sin(t / 13 + 1));
    if (gl) {
      gl.viewport(0, 0, gcv.width, gcv.height);
      // 1. 黑底 + 颗粒 + 暗角
      gl.bindTexture(gl.TEXTURE_2D, texBg);
      gl.uniformMatrix4fv(uM, false, I4);
      gl.uniformMatrix4fv(uMV, false, I4);
      gl.uniform2f(uFade, 1e9, 1);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      // 2. 星系盘：盘内自转 → 绕水平轴倾斜 → 绕视线转 → 透视 → 放到屏幕上；远端按深度压暗
      const mv = mul(Rz(tilt), mul(Rx(inc), mul(Rz(angle), Sc(Rg))));
      const m = mul(Ortho(), mul(Tr(gx, gy), mul(Persp(Rg * 3.6), mv)));
      gl.bindTexture(gl.TEXTURE_2D, texDisc);
      gl.uniformMatrix4fv(uM, false, m);
      gl.uniformMatrix4fv(uMV, false, mv);
      gl.uniform2f(uFade, 2 * Rg * Math.sin(inc), 0.55);
      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, cv.width, cv.height);
    } else {
      // 没有 WebGL：退回平面的椭圆，不做透视
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.drawImage(bg, 0, 0);
      ctx.setTransform(dpr, 0, 0, dpr, dpr * gx, dpr * gy);
      ctx.rotate(tilt); ctx.scale(1, Math.cos(inc)); ctx.rotate(angle);
      ctx.drawImage(disc, -Rg, -Rg, Rg * 2, Rg * 2);
    }
    // 核球：一团不压扁的暖光鼓在盘心，让中心是个球而不是个点
    ctx.setTransform(dpr * Rg * 0.16, 0, 0, dpr * Rg * 0.16, dpr * gx, dpr * gy);
    ctx.globalAlpha = 1;
    ctx.fillStyle = bulge;
    ctx.fillRect(-1, -1, 2, 2);
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
  const bulge = ctx.createRadialGradient(0, 0, 0, 0, 0, 1);
  bulge.addColorStop(0, "rgba(255, 238, 214, 0.22)");
  bulge.addColorStop(0.3, "rgba(255, 240, 222, 0.07)");
  bulge.addColorStop(1, "rgba(255, 240, 222, 0)");
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
  // 星系盘只画一次：核球 + 两条主臂两条副臂 + 尘埃带 + 盘面散星，之后由 GPU 按透视贴上
  const seed = (() => { let x = 20221130; return () => (x = (x * 1664525 + 1013904223) >>> 0) / 4294967296; })();
  const gauss = () => { let u = 0, v = 0; while (!u) u = seed(); while (!v) v = seed(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
  function makeDisc(size) {
    const Rg = Math.max(innerWidth, innerHeight) * 0.8; // 盘半径（CSS 像素）
    const k = size / (Rg * 2); // 贴图分辨率：桌面 4096，盘上每个 CSS 像素约 1.6 个纹素
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
        const w = Rg * (0.012 + 0.03 * tt), fade = (1 - tt / TMAX) * 0.26;
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
    c.R = Rg;
    return c;
  }
  // 贴图尺寸取 2 的幂，WebGL1 才能生成 mipmap
  const discSize = Math.min(gl ? gl.getParameter(gl.MAX_TEXTURE_SIZE) : 4096, mobile ? 2048 : 4096);
  disc = makeDisc(discSize);
  if (gl) texDisc = upload(null, disc, true);
  const resize = () => {
    dpr = Math.min(devicePixelRatio || 1, 1.5);
    W = innerWidth; H = innerHeight;
    cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    gcv.width = cv.width; gcv.height = cv.height;
    bg = document.createElement("canvas");
    bg.width = cv.width; bg.height = cv.height;
    const bc = bg.getContext("2d", { alpha: false });
    bc.fillStyle = "#000";
    bc.fillRect(0, 0, bg.width, bg.height);
    bc.fillStyle = bc.createPattern(tile, "repeat");
    bc.fillRect(0, 0, bg.width, bg.height);
    // 暗角外圈把颗粒也压暗
    bc.setTransform(bg.width * 1.2, 0, 0, bg.height * 0.95, bg.width / 2, bg.height / 2);
    const vg = bc.createRadialGradient(0, 0, 0, 0, 0, 1);
    vg.addColorStop(0.55, "rgba(0, 0, 0, 0)");
    vg.addColorStop(1, "#000");
    bc.fillStyle = vg;
    bc.fillRect(-1, -1, 2, 2);
    if (gl) texBg = upload(texBg, bg, false);
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
