p = 'index.html'
s = open(p, encoding='utf-8').read()


def R(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80])
    s = s.replace(a, b)


# ---- CSS：光晕 / 暗角 / 颗粒并进粒子画布，大年份文字不再单独成层
a = s.index('  /* 光晕只画一次')
b = s.index('  .app {')
s = s[:a] + '''  /* 光晕、暗角、颗粒都画在这张画布里：全屏半透明层叠得越多，合成时每帧要混合的像素就越多 */

''' + s[b:]
R('''  /* ---------- Atmosphere: black, haze, grain ---------- */
  #dust { position: fixed; inset: 0; width: 100%; height: 100%; }''',
  '''  /* ---------- Atmosphere: black, haze, grain ---------- */
  #dust { position: fixed; inset: 0; width: 100%; height: 100%; background: #000; }''')
# 滤镜挂在独立合成层上会每帧重算；不单独成层时，模糊结果随外层一起栅格化并缓存
R('''            mask-image: repeating-linear-gradient(to bottom, #000 0 2px, rgba(0, 0, 0, 0.45) 2px 4px);
    will-change: transform, opacity;
  }''', '''            mask-image: repeating-linear-gradient(to bottom, #000 0 2px, rgba(0, 0, 0, 0.45) 2px 4px);
  }''')
R('''<div class="haze" id="haze" aria-hidden="true"></div>
<div class="vignette" aria-hidden="true"></div>
<div class="grain" aria-hidden="true"></div>
''', '')
R('''ghost = $("#ghost"), haze = $("#haze");''', '''ghost = $("#ghost");''')
R('''  setTf(haze, `translateX(${cx.toFixed(1)}px)`);''', '''  drift.focus(M.left + cx);''')

# ---- 画布：底色+颗粒预渲染成一张图，每帧整张贴上；光晕按焦点缓动；暗角折算成粒子透明度
R('''  const cv = $("#dust"), ctx = cv.getContext("2d", { alpha: false });
  let W, H, running = !document.hidden, boost = 0, raf = 0, lastDraw = 0;''',
  '''  const cv = $("#dust"), ctx = cv.getContext("2d", { alpha: false });
  let W, H, dpr = 1, bg, running = !document.hidden, boost = 0, raf = 0, lastDraw = 0;
  let hx = innerWidth / 2, hxTo = hx; // 光晕中心，跟随焦点''')
R('''    boost *= Math.pow(0.94, dt);
    const cx = W * 0.5, cy = H * 0.58, f = Math.max(W, H) * 0.5;
    ctx.globalAlpha = 1;
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = "#fff";''', '''    boost *= Math.pow(0.94, dt);
    hx = reduceMotion ? hxTo : hx + (hxTo - hx) * (1 - Math.exp(-dt / 14));
    const cx = W * 0.5, cy = H * 0.58, f = Math.max(W, H) * 0.5;
    ctx.globalAlpha = 1;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.drawImage(bg, 0, 0);
    // 光晕：横 46vw、纵 38vh 的椭圆，中心压在时间线附近
    ctx.setTransform(dpr * W * 0.46, 0, 0, dpr * H * 0.38, dpr * hx, dpr * H * 0.62);
    ctx.fillStyle = haze;
    ctx.fillRect(-1, -1, 2, 2);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = "#fff";''')
R('''      const near = 1 - p.z;
      ctx.globalAlpha = (0.08 + near * 0.55) * (0.75 + 0.25 * Math.sin(t * 1.3 + p.tw));''',
  '''      const near = 1 - p.z;
      // 暗角：椭圆半径 120% × 95%，55% 以内不压暗
      const vx = (sx - cx) / (W * 1.2), vy = (sy - H * 0.5) / (H * 0.95);
      const vig = Math.min(1, Math.max(0, (Math.sqrt(vx * vx + vy * vy) - 0.55) / 0.45));
      ctx.globalAlpha = (0.08 + near * 0.55) * (0.75 + 0.25 * Math.sin(t * 1.3 + p.tw)) * (1 - vig);''')
R('''  const resize = () => {
    const dpr = Math.min(devicePixelRatio || 1, 1.5);
    W = innerWidth; H = innerHeight;
    cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    draw(performance.now());
  };''', '''  const haze = ctx.createRadialGradient(0, 0, 0, 0, 0, 1);
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
    draw(performance.now());
  };''')
R('''    const busy = now - t0 < 3000 || Math.abs(boost) > 0.0004;''',
  '''    const busy = now - t0 < 3000 || Math.abs(boost) > 0.0004 || Math.abs(hxTo - hx) > 0.5;''')
R('''  return dir => { if (!reduceMotion) boost = Math.max(-0.02, Math.min(0.02, boost + 0.007 * dir)); };
})();''', '''  const fn = dir => { if (!reduceMotion) boost = Math.max(-0.02, Math.min(0.02, boost + 0.007 * dir)); };
  fn.focus = x => {
    if (x === hxTo) return;
    hxTo = x;
    if (reduceMotion) draw(performance.now());
  };
  return fn;
})();''')

open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
