import re, sys
sys.stdout.reconfigure(encoding='utf-8')
p = 'index.html'
s = open(p, encoding='utf-8').read()


def R(t, new):
    """按标题定位整行替换，new 可为多行"""
    global s
    m = re.search(r'^  \{ d: "[\d-]+".* t: "%s",.*\},$' % re.escape(t), s, re.M)
    assert m, t
    s = s[:m.start()] + new + s[m.end():]


R("ChatGPT 月活用户破亿", '  { d: "2023-02-01", c: "industry", o: "OpenAI", t: "ChatGPT 月活用户破亿", x: "瑞银报告估计 ChatGPT 在 1 月的月活已过一亿，上线仅两个月，是当时增长最快的消费级应用。" },')
R("GPT-5.2", '  { d: "2025-12-11", c: "model", o: "OpenAI", t: "GPT-5.2", x: "Gemini 3 发布三周后，Altman 内部拉响“红色警报”，GPT-5.2 提前上线，距 5.1 仅隔四周。" },')
R("Claude Opus 4.6 与 Gemini 3.1 Pro", '''  { d: "2026-02-05", c: "model", o: "Anthropic", t: "Claude Opus 4.6", x: "上下文扩到百万 token、引入自适应思考，同日 OpenAI 推出 GPT-5.3-Codex 应战。" },
  { d: "2026-02-19", c: "model", o: "Google", t: "Gemini 3.1 Pro", x: "ARC-AGI-2 得分较 Gemini 3 Pro 翻倍，新增中等思考档位。此后半年谷歌只更新 Flash，Pro 一直停在预览。" },''')
R("GPT-5.4", '  { d: "2026-03-05", c: "model", o: "OpenAI", t: "GPT-5.4", x: "把 Codex 的编程能力、推理与操作电脑的能力并回一个模型，mini 与 nano 版 3 月 17 日跟进。" },')
R("GPT-5.5", '  { d: "2026-04-23", c: "model", o: "OpenAI", t: "GPT-5.5", x: "代号 Spud，用更少的 token 完成更多步骤；API 因补充网络安全护栏而晚一天开放。" },')
R("Claude Opus 4.8", '  { d: "2026-05-28", c: "model", o: "Anthropic", t: "Claude Opus 4.8", x: "Opus 4.x 系列的最后一版，距 4.7 不到两个月，新增可调的努力程度，Anthropic 同时预告更高一级的模型即将到来。" },')
R("Claude Fable 5 与受限的 Mythos 5", '''  { d: "2026-06-09", c: "model", o: "Anthropic", m: 1, t: "Claude Fable 5 与受限的 Mythos 5", x: "Claude 5 家族登场。Fable 向公众开放，能力更强的 Mythos 只向受限对象提供，最强模型不再默认公开。三天后美国政府以国家安全为由限制出口，两周半后解除。" },
  { d: "2026-06-30", c: "model", o: "Anthropic", t: "Claude Sonnet 5", x: "接替 Sonnet 4.6 成为默认模型，以约一半价格接近 Opus 4.8 的水平。同日 Fable 5 的出口限制解除。" },''')
R("Claude Fable 5.1", '  { d: "2026-09-01", c: "model", o: "Anthropic", t: "Claude Fable 5.1", x: "Fable 与 Mythos 同步升级到 5.1，价格不变，缓存读取降价四分之三。" },')
R("GPT-6", '  { d: "2026-09-03", c: "model", o: "OpenAI", m: 1, t: "GPT-6 Astra", x: "因 7 月智能体越权攻击事件推迟数周后发布，先向获批用户开放，次日面向付费用户。Brockman 在发布会结尾说：欢迎来到 AGI 时代。编年记录暂止于此。" },')

assert not re.search(r'd: "\d{4}-\d{2}"', s), "still has month-only dates"
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok', s.count('{ d: "'))
