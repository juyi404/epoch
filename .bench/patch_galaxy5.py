p = 'index.html'
s = open(p, encoding='utf-8').read()


def R(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)


a = s.index('    // 星系盘：先倾斜压扁成椭圆')
b = s.index('    // 光晕：横 46vw')
s = s[:a] + '''    // 星系盘：中心跟着焦点轻微漂移；视角极缓慢地摆动，像镜头在绕着它漂
    const gx = cx + (hx - cx) * 0.08, gy = H * 0.5;
    const tilt = TILT + (reduceMotion ? 0 : 0.03 * Math.sin(t / 9)), sq = SQUASH + (reduceMotion ? 0 : 0.03 * Math.sin(t / 13 + 1));
    // 投影很贵，转动极慢时只在角度/视角/位置变了一点点之后才重投影，平时贴缓存
    const moving = now - t0 < 3000 || Math.abs(boost) > 0.0004 || Math.abs(hxTo - hx) > 0.5;
    if (moving || Math.abs(angle - lp.angle) > 0.0006 || Math.abs(tilt - lp.tilt) > 0.002 || Math.abs(sq - lp.sq) > 0.002 || Math.abs(gx - lp.gx) > 0.5) {
      project(gx, gy, tilt, sq);
      lp.angle = angle; lp.tilt = tilt; lp.sq = sq; lp.gx = gx;
    }
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.drawImage(gal, 0, 0);
''' + s[b:]

R('''  const haze = ctx.createRadialGradient(0, 0, 0, 0, 0, 1);''', '''  const lp = { angle: 1e9, tilt: 0, sq: 0, gx: 0 };
  function project(gx, gy, tilt, sq) {
    // 先把盘按当前角度转好，画进一张中间画布
    const Rg = disc.R, Sm = mid.width;
    mc.setTransform(1, 0, 0, 1, 0, 0);
    mc.clearRect(0, 0, Sm, Sm);
    mc.setTransform(Sm / (2 * Rg), 0, 0, Sm / (2 * Rg), Sm / 2, Sm / 2);
    mc.rotate(angle);
    mc.drawImage(disc, -Rg, -Rg, Rg * 2, Rg * 2);
    // 透视：把转好的盘切成横条贴上，靠近观众的一侧放大、远侧缩小并压暗，平面的椭圆就有了前后
    const P = 0.2, STRIPS = mobile ? 24 : 36;
    const sc = v => 1 / (1 - P * v / Rg); // v>0 为靠近观众的一侧
    const yOf = v => v * sq * sc(v);
    gc.setTransform(1, 0, 0, 1, 0, 0);
    gc.clearRect(0, 0, gal.width, gal.height);
    gc.setTransform(dpr, 0, 0, dpr, dpr * gx, dpr * gy);
    gc.rotate(tilt);
    for (let j = 0; j < STRIPS; j++) {
      const v0 = -Rg + 2 * Rg * j / STRIPS, v1 = v0 + 2 * Rg / STRIPS, vm = (v0 + v1) / 2;
      const y0 = yOf(v0), y1 = yOf(v1), sm = sc(vm);
      const sy = (v0 + Rg) / (2 * Rg) * Sm, sh = Sm / STRIPS;
      gc.globalAlpha = 0.5 + 0.5 * (vm + Rg) / (2 * Rg); // 远端压暗
      gc.drawImage(mid, 0, sy, Sm, sh + 1, -Rg * sm, y0, 2 * Rg * sm, y1 - y0 + 0.7);
    }
    // 核球：一团不压扁的暖光鼓在盘心，让中心是个球而不是个点
    gc.setTransform(dpr * Rg * 0.16, 0, 0, dpr * Rg * 0.16, dpr * gx, dpr * gy);
    gc.globalAlpha = 1;
    gc.fillStyle = bulge;
    gc.fillRect(-1, -1, 2, 2);
  }
  const haze = ctx.createRadialGradient(0, 0, 0, 0, 0, 1);''')

R('''  let W, H, dpr = 1, bg, disc, mid, mc, running''', '''  let W, H, dpr = 1, bg, disc, mid, mc, gal, gc, running''')
R('''    mid.width = mid.height = Math.min(disc.width, 2400);
    mc = mid.getContext("2d");
    draw(performance.now());''', '''    mid.width = mid.height = Math.min(disc.width, 1800);
    mc = mid.getContext("2d");
    // 投影结果缓存在一张屏幕大小的画布里
    gal = document.createElement("canvas");
    gal.width = cv.width; gal.height = cv.height;
    gc = gal.getContext("2d");
    lp.angle = 1e9;
    draw(performance.now());''')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
