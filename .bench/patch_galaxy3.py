p = 'index.html'
s = open(p, encoding='utf-8').read()


def R(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)


R('''    const gx = cx + (hx - cx) * 0.08, gy = H * 0.5;
    ctx.setTransform(dpr, 0, 0, dpr, dpr * gx, dpr * gy);
    ctx.rotate(TILT);
    ctx.scale(1, SQUASH);
    ctx.rotate(angle);
    ctx.drawImage(disc, -disc.R, -disc.R, disc.R * 2, disc.R * 2);''',
  '''    const gx = cx + (hx - cx) * 0.08, gy = H * 0.5;
    // 视角极缓慢地摆动，像镜头在绕着它漂
    const tilt = TILT + (reduceMotion ? 0 : 0.03 * Math.sin(t / 9)), sq = SQUASH + (reduceMotion ? 0 : 0.03 * Math.sin(t / 13 + 1));
    // 透视：把盘切成横条，近的一条放大、远的一条缩小并压暗，平面的椭圆就有了前后
    const Rg = disc.R, P = 0.32, STRIPS = mobile ? 18 : 28;
    const sc = v => 1 / (1 - P * v / Rg); // v>0 为靠近观众的一侧
    const yOf = v => v * sq * sc(v);
    for (let j = 0; j < STRIPS; j++) {
      const v0 = -Rg + 2 * Rg * j / STRIPS, v1 = v0 + 2 * Rg / STRIPS, vm = (v0 + v1) / 2;
      const y0 = yOf(v0), y1 = yOf(v1), sm = sc(vm);
      ctx.save();
      ctx.setTransform(dpr, 0, 0, dpr, dpr * gx, dpr * gy);
      ctx.rotate(tilt);
      ctx.beginPath();
      ctx.rect(-3 * Rg, y0 - 0.5, 6 * Rg, y1 - y0 + 1);
      ctx.clip();
      ctx.globalAlpha = 0.5 + 0.5 * (vm + Rg) / (2 * Rg); // 远端压暗
      ctx.scale(sm, sm * sq);
      ctx.rotate(angle);
      ctx.drawImage(disc, -Rg, -Rg, Rg * 2, Rg * 2);
      ctx.restore();
    }
    // 核球：一团不压扁的暖光鼓在盘心，让中心是个球而不是个点
    ctx.setTransform(dpr, 0, 0, dpr, dpr * gx, dpr * gy);
    ctx.globalAlpha = 1;
    ctx.fillStyle = bulge;
    ctx.save();
    ctx.scale(Rg * 0.16, Rg * 0.16);
    ctx.fillRect(-1, -1, 2, 2);
    ctx.restore();''')

R('''  const haze = ctx.createRadialGradient(0, 0, 0, 0, 0, 1);''',
  '''  const bulge = ctx.createRadialGradient(0, 0, 0, 0, 0, 1);
  bulge.addColorStop(0, "rgba(255, 238, 214, 0.22)");
  bulge.addColorStop(0.3, "rgba(255, 240, 222, 0.07)");
  bulge.addColorStop(1, "rgba(255, 240, 222, 0)");
  const haze = ctx.createRadialGradient(0, 0, 0, 0, 0, 1);''')

# 尘埃带柔一点，别像两道黑印
R('''        const w = Rg * (0.008 + 0.02 * tt), fade = (1 - tt / TMAX) * 0.5;
        soft(Math.cos(th) * r, Math.sin(th) * r, w, "0, 0, 0", fade);''',
  '''        const w = Rg * (0.012 + 0.03 * tt), fade = (1 - tt / TMAX) * 0.26;
        soft(Math.cos(th) * r, Math.sin(th) * r, w, "0, 0, 0", fade);''')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
