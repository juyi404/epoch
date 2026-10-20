import re, sys, json
sys.stdout.reconfigure(encoding='utf-8')
p = 'index.html'
s = open(p, encoding='utf-8').read()
a = s.index('const EVENTS = [\n') + len('const EVENTS = [\n')
b = s.index('\n];', a)
lines = [l for l in s[a:b].split('\n') if l.strip()]
date_of = lambda l: re.search(r'd: "([\d-]+)"', l).group(1)
title_of = lambda l: re.search(r' t: "([^"]*)"', l).group(1)


def R(t, new):
    for i, l in enumerate(lines):
        if title_of(l) == t:
            lines[i] = new
            return
    raise AssertionError(t)


R("Gemini 4 Argon", '  { d: "2026-09-30", c: "model", o: "Google", m: 1, t: "Gemini 4 Argon", x: "Pro 线从 3.1 直接跳到 4，中间半年只出 Flash。单次输出上限从 6.4 万提到 100 万 token，多项基准超过 Opus 5.5 和 GPT-6 Astra，Vals 指数居首。起初只向 Fairwind 计划里经审核的网络防御团队开放，10 月 13 日才在 API 全面开放。" },')

E = lambda d, c, o, t, x, m=0: (d, c, o, t, x, m)
NEW = [
    E("2026-10-07", "product", "OpenAI", "GPT-6 全量进入 ChatGPT", "付费用户默认 GPT-6 Sol，免费用户默认 GPT-6 Luna，所有人都用上了第六代 GPT。同时上线 Intelligent UI，回答里直接嵌入可视化和可交互的界面。"),
    E("2026-10-09", "policy", "Anthropic", "Anthropic 把内部评估和外网断开", "测试中的智能体行为难以完全管住，Anthropic 干脆把内部评估环境与公共互联网隔离。前沿实验室开始承认：在能可靠约束智能体之前，只能先切断它们的出口。"),
    E("2026-10-12", "model", "Meta", "Muse Wonder", "Meta 的第一个前沿模型，也是 Alexandr Wang 重组 Meta AI 后的首个旗舰。闭源，定价与 Opus 5.5 相同，主打长期记忆；独立评测里大版本与 Sonnet 5.5 持平，略低于 Opus 5.5。", 1),
    E("2026-10-12", "industry", "Character.AI", "Character.AI 破产，迪士尼接手", "被多起青少年相关诉讼拖垮，申请破产保护。迪士尼以 2000 万美元竞购部分资产，随后又同意接收大部分员工。第一代 AI 陪伴应用的明星公司就此谢幕。"),
    E("2026-10-14", "industry", "Anthropic", "Q3 营收 168 亿，调整后盈利", "IPO 前的投资者见面会上公布：第三季度营收环比增长 45%，调整后毛利率约 85%，连续两个季度调整后盈利，前三季度合计约 331 亿美元。上市预计在 11 月。"),
    E("2026-10-15", "open", "Meta", "Muse Spark Open", "8160 亿参数的 MoE，每 token 激活约 420 亿，百万上下文，开放权重，两台 Mac Studio 就能跑。8 月 Meta 还说 Muse Spark 不开源，这次部分回到开源路线；许可证仍有商用限制。"),
    E("2026-10-18", "industry", "Anthropic", "拿出 5% 股份成立公益基金", "按 5 月估值约合 480 亿美元，需股东批准；公司价值每上涨一半，董事会还可再追加 2%。加上创始人与员工的捐赠承诺，约两成股权已指定用于公益，受益对象之一是被 AI 冲击的劳动者。"),
]
have = {title_of(l) for l in lines}
for d, c, o, t, x, m in NEW:
    assert t not in have, t
    ms = ' m: 1,' if m else ''
    lines.append(f'  {{ d: {json.dumps(d)}, c: "{c}", o: {json.dumps(o, ensure_ascii=False)},{ms} t: {json.dumps(t, ensure_ascii=False)}, x: {json.dumps(x, ensure_ascii=False)} }},')
lines.sort(key=date_of)
out, prev = [], None
for l in lines:
    y = date_of(l)[:4]
    if prev and y != prev:
        out.append('')
    out.append(l)
    prev = y
s = s[:a] + '\n'.join(out) + s[b:]
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print(len(lines))
