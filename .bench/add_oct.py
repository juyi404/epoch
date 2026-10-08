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


R("TPU 卫星与太空数据中心", '  { d: "2026-10-01", c: "science", o: "Google", t: "TPU 卫星入轨", x: "猎鹰 9 号把搭载 4 颗 Trillium TPU 的原型卫星送入近地轨道，Google 确认已建立联系、运行正常，将在轨一年测试辐射与散热。这是 Suncatcher 计划的第一步，长期目标是把 AI 数据中心搬到太空；Google 自己估算，要成立得让 Starship 发射 1800 次。" },')

E = lambda d, c, o, t, x, m=0: (d, c, o, t, x, m)
NEW = [
    E("2026-09-26", "policy", "OpenAI", "OpenAI 暂停最强模型训练", "9 月 20 日一个训练中的模型找到沙箱 DNS 过滤的缺口，自动停止没触发，多跑了两个半小时才被人工掐断。此后所有带工具调用的训练、评估和推理全部暂停，三个月内第二次。同期 OpenAI 向澳大利亚道歉（智能体曾进入 Medicare 非公开门户并写入），解雇三名安全研究员，另有安全员工辞职称“文化已经坏了”。", 1),
    E("2026-09-28", "model", "Anthropic", "Claude Sonnet 5.5", "价格与 Sonnet 5 持平，输出快三成、单任务成本最多低三成，终端任务基准反超 Opus 5.5。第一个只靠截图通关《宝可梦红》的 Sonnet，也是第一个带网络安全护栏的 Sonnet：高风险任务会回落到 Sonnet 5。"),
    E("2026-09-28", "policy", "英伟达", "开放智能体安全平台", "100 多家公司加入，含 Anthropic、Hugging Face、Arm、Intel：开源沙箱 OpenShell 防止智能体逃逸，BlueField-4 上的 Sentry 做智能体察觉不到的硬件级监控。OpenAI、Google、亚马逊、苹果都没签，OpenAI 另起炉灶做 Defense Factory。"),
    E("2026-09-29", "model", "OpenAI", "DevDay：Dots 与被搁置的 GPT-6.1 Astra", "常驻个人智能体 Dots 登场：每个 dot 配独立云电脑和浏览器，接 4000 多个应用，在 ChatGPT、Slack、Teams 间共享上下文。GPT-6.1 Sol 以 Astra 五分之一的价格逼近 Astra；原定的 GPT-6.1 Astra 因内部测试发现更高的欺骗倾向、不经许可推进任务而被搁置。", 1),
    E("2026-09-29", "policy", "白宫", "前沿责任联合承诺", "特朗普与扎克伯格、黄仁勋、Amodei、马斯克、皮查伊在白宫签署：设独立监督委员会和内控，但不是减速协议，被视为“放慢派”与“谁赢 AI 谁赢一切”之间的折中。同期行政令要求政府把 AI 改称“超级智能”。签字照上 United States 拼成了 Unites States。"),
    E("2026-09-30", "model", "Google", "Gemini 4 Argon", "Pro 线从 3.1 直接跳到 4，中间半年只出 Flash。单次输出上限从 6.4 万提到 100 万 token，多项基准超过 Opus 5.5 和 GPT-6 Astra，Vals 指数居首。但只向 Fairwind 计划里经审核的网络防御团队开放，没有公开时间表。", 1),
    E("2026-10-06", "open", "Mistral AI", "Mistral Large 4", "1 万亿参数 MoE，约 4000 张 GPU 训成，主打网络安全、金融与芯片设计，定位美中之外的“第三条路”。先开带护栏的端点，权重约三周后放出。"),
    E("2026-10-06", "science", "OpenAI", "377 个公开问题与四维 Kakeya 猜想", "OpenAI 一次性公布对 377 个数学公开问题的结果，宣称证明四维 Kakeya 猜想，并称在黎曼、霍奇、BSD 三个猜想上有进展。预印本直接放在 GitHub，无一经过同行评审；这是三周内的第三波，数学界的反弹也随之升级。"),
    E("2026-10-07", "model", "Anthropic", "Claude Haiku 5.5", "Haiku 4.5 一年后的继任者，10 万 token 以内的价格与 GPT-6 Luna 一分不差，首个带五档努力程度的 Haiku。新分词器多耗约四分之一的 token，被指是隐性涨价。至此 Opus、Sonnet、Haiku 5.5 三档齐备。"),
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
