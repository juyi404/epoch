# 智能纪元编年史

自 2022 年 11 月 30 日 ChatGPT 上线以来的 AI 大事记，一条横向时间线，183 个节点，覆盖 2022–2026 年。

在线地址：https://juyi404.github.io/epoch/

## 结构

- `index.html` — 整个网页，单文件。数据、样式、脚本都在里面：
  - `CATS` 事件分类（模型发布 / 开源 / 产品与智能体 / 治理与安全 / 科学 / 产业与资本）
  - `YEARS` 每年一句话
  - `EVENTS` 事件列表，按日期排序，`m: 1` 表示大事件
  - 背景是 WebGL 画的透视旋转星系，没有 WebGL 时退回 2D 画布
- `index.*.html` — 各阶段的备份，改坏了可以退回
- `.bench/` — 开发用的脚本与截图
  - `bench.mjs` 用 CDP 驱动无头 Chrome 测帧数与主线程开销
  - `shot.mjs` 截图
  - `patch_*.py`、`add_*.py`、`fix_*.py` 历次改动脚本
  - `*.png` 各阶段截图

## 本地运行

任何静态服务器都行，例如：

```bash
python -m http.server 5178
```

然后打开 http://localhost:5178/ 。

## 添加事件

在 `index.html` 的 `EVENTS` 数组里加一行：

```js
{ d: "2026-10-01", c: "model", o: "机构", t: "短标题", x: "一两句描述。" },
```

`d` 用 `YYYY-MM-DD`，`c` 取 `CATS` 里的键。页面会自动按日期排序并重新铺开时间线。
