p = 'index.html'
s = open(p, encoding='utf-8').read()


def R(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)


a = s.index('    // 透视：把盘切成横条')
b = s.index('    // 核球：一团不压扁的暖光鼓在盘心')
s = s[:a] + '''    // 先把盘按当前角度转好，画进一张中间画布
    const Rg = disc.R, Sm = mid.width;
    mc.setTransform(1, 0, 0, 1, 0, 0);
    mc.clearRect(0, 0, Sm, Sm);
    mc.setTransform(Sm / (2 * Rg), 0, 0, Sm / (2 * Rg), Sm / 2, Sm / 2);
    mc.rotate(angle);
    mc.drawImage(disc, -Rg, -Rg, Rg * 2, Rg * 2);
    // 透视：把转好的盘切成横条贴上屏幕，靠近观众的一侧放大、远侧缩小并压暗，平面的椭圆就有了前后
    const P = 0.2, STRIPS = mobile ? 24 : 40;
    const sc = v => 1 / (1 - P * v / Rg); // v>0 为靠近观众的一侧
    const yOf = v => v * sq * sc(v);
    ctx.setTransform(dpr, 0, 0, dpr, dpr * gx, dpr * gy);
    ctx.rotate(tilt);
    for (let j = 0; j < STRIPS; j++) {
      const v0 = -Rg + 2 * Rg * j / STRIPS, v1 = v0 + 2 * Rg / STRIPS, vm = (v0 + v1) / 2;
      const y0 = yOf(v0), y1 = yOf(v1), sm = sc(vm);
      const sy = (v0 + Rg) / (2 * Rg) * Sm, sh = Sm / STRIPS;
      ctx.globalAlpha = 0.5 + 0.5 * (vm + Rg) / (2 * Rg); // 远端压暗
      ctx.drawImage(mid, 0, sy, Sm, sh + 1, -Rg * sm, y0, 2 * Rg * sm, y1 - y0 + 0.7);
    }
''' + s[b:]

R('''  let W, H, dpr = 1, bg, disc, running''', '''  let W, H, dpr = 1, bg, disc, mid, mc, running''')
R('''    disc = makeDisc();
    draw(performance.now());''', '''    disc = makeDisc();
    // 中间画布：装转好角度的盘，封顶 2400px
    mid = document.createElement("canvas");
    mid.width = mid.height = Math.min(disc.width, 2400);
    mc = mid.getContext("2d");
    draw(performance.now());''')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
