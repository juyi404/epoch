p = 'index.html'
s = open(p, encoding='utf-8').read()


def R(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:70])
    s = s.replace(a, b)


# ---- CSS：面板不再用 backdrop-filter，毛玻璃由面板里的一张小画布画
R('''    /* 毛玻璃：底色放淡，靠背景模糊透出后面的星系；顶部一道细高光模拟玻璃边 */
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0) 40%), rgba(14, 14, 18, 0.42);
    -webkit-backdrop-filter: blur(14px);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.12);''',
  '''    /* 毛玻璃：backdrop-filter 会让浏览器每帧重新模糊面板后面的整块画面，太贵；
       改由面板里的 .glass 小画布按 1/3 分辨率截取背景画布并模糊，成本只有原来的零头 */
    background: none;
    border: 1px solid rgba(255, 255, 255, 0.12);''')
R('''  @supports not (backdrop-filter: blur(1px)) { .panel { background: var(--glass); } }
''', '''  .glass { position: absolute; inset: 0; width: 100%; height: 100%; border-radius: inherit; }
  .panel::before { content: ""; position: absolute; inset: 0; z-index: 1; border-radius: inherit; pointer-events: none;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0) 40%); }
''')
R('''    <article class="panel" id="panel" style="--k: var(--c-model)">''',
  '''    <article class="panel" id="panel" style="--k: var(--c-model)">
      <canvas class="glass" id="glass" aria-hidden="true"></canvas>''')

# ---- JS：核球光、光晕、粒子全部搬进 WebGL，只剩一张不透明画布；2D 画布只在没有 WebGL 时使用
a = s.index('/* ---------- Galaxy: WebGL')
b = s.index('/* ---------- Year streak')
s = s[:a] + r'''/* ---------- Galaxy: 一张 WebGL 画布画完全部背景（黑底颗粒、透视星系盘、核球光、光晕、前景粒子）；
   没有 WebGL 时退回 2D 画布；面板的毛玻璃由 .glass 小画布低分辨率截取背景再模糊 ---------- */
const drift = (() => {
  const cv = $("#dust"), gcv = $("#galaxy"), panelEl = $("#panel"), glassEl = $("#glass"), gctx = glassEl.getContext("2d");
  const GLO = { alpha: false, antialias: false, depth: false, stencil: false, powerPreference: "low-power" };
  const gl = gcv.getContext("webgl2", GLO) || gcv.getContext("webgl", GLO);
  const ctx = gl ? null : cv.getContext("2d", { alpha: false });
  if (gl) cv.hidden = true; else gcv.hidden = true;
  const src = gl ? gcv : cv; // 毛玻璃从哪张画布取样
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
    const ti = Math.random() < 0.7 ? 0 : Math.random() < 0.6 ? 1 : 2;
    p.c = TINT[ti]; p.ti = ti;
    return p;
  };
  for (let i = 0; i < N; i++) pts.push(spawn({}));
  const RGB = TINT.map(t => t.split(",").map(v => v / 255));
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
  const Sc = (x, y = x) => new Float32Array([x, 0, 0, 0, 0, y, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]);
  const Tr = (x, y) => new Float32Array([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, x, y, 0, 1]);
  const Persp = F => { const m = new Float32Array(I4); m[11] = -1 / F; return m; }; // w = 1 - z/F，观众在 +z 方向 F 处
  let ortho; // CSS 像素 → NDC，尺寸变化时重算

  /* ---- 径向渐变贴图：核球光、光晕都用它，颜色烘进贴图 ---- */
  const gradTex = stops => {
    const c = document.createElement("canvas");
    c.width = c.height = 128;
    const g = c.getContext("2d"), gr = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    stops.forEach(([o, col]) => gr.addColorStop(o, col));
    g.fillStyle = gr;
    g.fillRect(0, 0, 128, 128);
    return c;
  };
  const bulgeImg = gradTex([[0, "rgba(255, 238, 214, 0.22)"], [0.3, "rgba(255, 240, 222, 0.07)"], [1, "rgba(255, 240, 222, 0)"]]);
  const hazeImg = gradTex([[0, "rgba(255, 255, 255, 0.045)"], [1, "rgba(255, 255, 255, 0)"]]);

  /* ---- WebGL：两个着色器（贴图四边形 / 纯色三角形） ---- */
  let texProg, colProg, uM, uMV, uFade, uCM, texBg, texDisc, texBulge, texHaze, aniso, quadBuf, ptBuf, aP, aC;
  const ptData = new Float32Array(N * 6 * 6);
  if (gl) {
    const sh = (type, code) => { const o = gl.createShader(type); gl.shaderSource(o, code); gl.compileShader(o); return o; };
    const link = (vs, fs) => { const pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, fs)); gl.linkProgram(pr); return pr; };
    texProg = link(`attribute vec2 p; uniform mat4 m, mv; varying vec2 uv; varying float dz;
      void main() { gl_Position = m * vec4(p, 0., 1.); uv = p * .5 + .5; dz = (mv * vec4(p, 0., 1.)).z; }`,
      `precision mediump float; uniform sampler2D t; uniform vec2 fade; varying vec2 uv; varying float dz;
      void main() { vec4 c = texture2D(t, uv); float f = clamp(.5 + dz / fade.x, 0., 1.); gl_FragColor = c * mix(fade.y, 1., f); }`);
    colProg = link(`attribute vec2 p; attribute vec4 c; uniform mat4 m; varying vec4 vc;
      void main() { gl_Position = m * vec4(p, 0., 1.); vc = c; }`,
      `precision mediump float; varying vec4 vc; void main() { gl_FragColor = vc; }`);
    quadBuf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, quadBuf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
    ptBuf = gl.createBuffer();
    uM = gl.getUniformLocation(texProg, "m"); uMV = gl.getUniformLocation(texProg, "mv"); uFade = gl.getUniformLocation(texProg, "fade");
    uCM = gl.getUniformLocation(colProg, "m");
    aP = gl.getAttribLocation(colProg, "p"); aC = gl.getAttribLocation(colProg, "c");
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA); // 贴图与顶点色都按预乘 alpha
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, true);
    aniso = gl.getExtension("EXT_texture_filter_anisotropic");
  }
  const upload = (tex, img, mip) => {
    tex = tex || gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, mip ? gl.LINEAR_MIPMAP_LINEAR : gl.LINEAR);
    if (mip) {
      gl.generateMipmap(gl.TEXTURE_2D);
      // 各向异性过滤：盘是斜着看的，远端缩得很厉害，没有它星星会糊成一片
      if (aniso) gl.texParameterf(gl.TEXTURE_2D, aniso.TEXTURE_MAX_ANISOTROPY_EXT, Math.min(4, gl.getParameter(aniso.MAX_TEXTURE_MAX_ANISOTROPY_EXT)));
    }
    return tex;
  };
  // 画一张贴图四边形：m 为完整变换，mv 只到视图空间（算深度压暗用），fade=[深度范围, 远端亮度]
  const quad = (tex, m, mv, fx, fy) => {
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.uniformMatrix4fv(uM, false, m);
    gl.uniformMatrix4fv(uMV, false, mv);
    gl.uniform2f(uFade, fx, fy);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
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
    // 前景粒子：先推进，再各自算出屏幕位置和亮度
    const streak0 = Math.abs(boost) * 900;
    let n = 0;
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
      const al = (0.08 + near * 0.55) * (0.75 + 0.25 * Math.sin(t * 1.3 + p.tw)) * (1 - vig);
      const r = 0.4 + near * 1.3;
      const streak = Math.min(24, streak0 * near); // 跳转时拉出短短的横向拖影
      p.sx = sx; p.sy = sy; p.al = al; p.r = r; p.st = streak;
      if (gl) {
        // 两个三角形，顶点色预乘 alpha
        const x0 = sx - r - streak, x1 = sx + r + streak, y0 = sy - r * 0.5, y1 = sy + r * 0.5, c = RGB[p.ti];
        const cr = c[0] * al, cg = c[1] * al, cb = c[2] * al;
        const put = (x, y) => { ptData[n++] = x; ptData[n++] = y; ptData[n++] = cr; ptData[n++] = cg; ptData[n++] = cb; ptData[n++] = al; };
        put(x0, y0); put(x1, y0); put(x0, y1); put(x0, y1); put(x1, y0); put(x1, y1);
      }
    }
    if (gl) {
      gl.viewport(0, 0, gcv.width, gcv.height);
      gl.useProgram(texProg);
      gl.bindBuffer(gl.ARRAY_BUFFER, quadBuf);
      gl.enableVertexAttribArray(aP);
      gl.disableVertexAttribArray(aC);
      gl.vertexAttribPointer(aP, 2, gl.FLOAT, false, 0, 0);
      // 1. 黑底 + 颗粒 + 暗角
      quad(texBg, I4, I4, 1e9, 1);
      // 2. 星系盘：盘内自转 → 绕水平轴倾斜 → 绕视线转 → 透视 → 放到屏幕上；远端按深度压暗
      const mv = mul(Rz(tilt), mul(Rx(inc), mul(Rz(angle), Sc(Rg))));
      quad(texDisc, mul(ortho, mul(Tr(gx, gy), mul(Persp(Rg * 3.6), mv))), mv, 2 * Rg * Math.sin(inc), 0.55);
      // 3. 核球：一团不压扁的暖光鼓在盘心；4. 光晕：横 46vw、纵 38vh 的椭圆，中心压在时间线附近
      quad(texBulge, mul(ortho, mul(Tr(gx, gy), Sc(Rg * 0.16))), I4, 1e9, 1);
      quad(texHaze, mul(ortho, mul(Tr(hx, H * 0.62), Sc(W * 0.46, H * 0.38))), I4, 1e9, 1);
      // 5. 粒子
      gl.useProgram(colProg);
      gl.uniformMatrix4fv(uCM, false, ortho);
      gl.bindBuffer(gl.ARRAY_BUFFER, ptBuf);
      gl.bufferData(gl.ARRAY_BUFFER, ptData.subarray(0, n), gl.DYNAMIC_DRAW);
      gl.enableVertexAttribArray(aP);
      gl.enableVertexAttribArray(aC);
      gl.vertexAttribPointer(aP, 2, gl.FLOAT, false, 24, 0);
      gl.vertexAttribPointer(aC, 4, gl.FLOAT, false, 24, 8);
      gl.drawArrays(gl.TRIANGLES, 0, n / 6);
    } else {
      // 没有 WebGL：2D 画布，平面的椭圆星系，不做透视
      ctx.globalAlpha = 1;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.drawImage(bg, 0, 0);
      ctx.setTransform(dpr, 0, 0, dpr, dpr * gx, dpr * gy);
      ctx.rotate(tilt); ctx.scale(1, Math.cos(inc)); ctx.rotate(angle);
      ctx.drawImage(disc, -Rg, -Rg, Rg * 2, Rg * 2);
      ctx.setTransform(dpr * Rg * 0.16, 0, 0, dpr * Rg * 0.16, dpr * gx, dpr * gy);
      ctx.drawImage(bulgeImg, -1, -1, 2, 2);
      ctx.setTransform(dpr * W * 0.46, 0, 0, dpr * H * 0.38, dpr * hx, dpr * H * 0.62);
      ctx.drawImage(hazeImg, -1, -1, 2, 2);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      let cur = "";
      for (const p of pts) {
        if (p.al === undefined) continue;
        ctx.globalAlpha = p.al;
        if (p.c !== cur) { cur = p.c; ctx.fillStyle = `rgb(${cur})`; }
        ctx.fillRect(p.sx - p.r - p.st, p.sy - p.r * 0.5, p.r * 2 + p.st * 2, p.r);
      }
    }
    glass();
  }
  // 毛玻璃：按面板当前位置从背景画布截一块，缩到 1/3 分辨率再模糊，最后压一层深色
  function glass() {
    const r = panelEl.getBoundingClientRect();
    if (!r.width) return;
    const gw = Math.ceil(r.width / 3), gh = Math.ceil(r.height / 3), pad = 6;
    if (glassEl.width !== gw || glassEl.height !== gh) { glassEl.width = gw; glassEl.height = gh; }
    gctx.clearRect(0, 0, gw, gh);
    gctx.filter = "blur(4px)";
    const k = dpr / 3;
    gctx.drawImage(src, (r.left - pad * 3) * dpr, (r.top - pad * 3) * dpr, (r.width + pad * 6) * dpr, (r.height + pad * 6) * dpr, -pad, -pad, gw + pad * 2, gh + pad * 2);
    gctx.filter = "none";
    gctx.fillStyle = "rgba(14, 14, 18, 0.42)";
    gctx.fillRect(0, 0, gw, gh);
  }
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
''' + s[s.index('  // 星系盘只画一次：核球'):b] + s[b:]

# 贴图上传：核球光与光晕
R('''  disc = makeDisc(discSize);
  if (gl) texDisc = upload(null, disc, true);''', '''  disc = makeDisc(discSize);
  if (gl) { texDisc = upload(null, disc, true); texBulge = upload(null, bulgeImg, false); texHaze = upload(null, hazeImg, false); }''')
R('''    cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    gcv.width = cv.width; gcv.height = cv.height;''', '''    const pw = Math.round(W * dpr), ph = Math.round(H * dpr);
    if (gl) { gcv.width = pw; gcv.height = ph; } else { cv.width = pw; cv.height = ph; }
    ortho = new Float32Array([2 / W, 0, 0, 0, 0, -2 / H, 0, 0, 0, 0, 0, 0, -1, 1, 0, 1]);''')
R('''    bg = document.createElement("canvas");
    bg.width = cv.width; bg.height = cv.height;''', '''    bg = document.createElement("canvas");
    bg.width = pw; bg.height = ph;''')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
