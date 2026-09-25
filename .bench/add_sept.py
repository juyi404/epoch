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


R("Claude Fable 5.1", '  { d: "2026-09-01", c: "model", o: "Anthropic", t: "Claude Fable 5.1", x: "Fable 与 Mythos 同步升级到 5.1，同一底座、只差安全护栏。价格不变，缓存读取降价四分之三；低、中努力档下以更低成本达到或超过 Fable 5。" },')
R("GPT-6 Astra", '  { d: "2026-09-03", c: "model", o: "OpenAI", m: 1, t: "GPT-6 Astra", x: "因 7 月智能体越权攻击事件推迟数周后发布。据报道采用“循环深度”架构，让模型在隐状态里反复推理而不必吐出文字；在超过 10 万张 GB200 上预训练。Brockman 在发布会结尾说：欢迎来到 AGI 时代。" },')

E = lambda d, c, o, t, x, m=0: (d, c, o, t, x, m)
NEW = [
    E("2026-09-02", "model", "Google", "Gemini 3.8 Flash", "六周内第三款 Flash，价格与 3.7 持平。智能体终端任务上以 89.4% 领先 Opus 5，另有面向可信防御方的 Cyber 版本。Pro 系列自 2 月起再无更新。"),
    E("2026-09-02", "model", "Meta", "Muse Spark 1.3", "闭源旗舰更新，编程基准上追平 GPT-5.6 Sol，但最强的 max 档发布时仍在安全测试。Meta 同时确认 Muse Spark 系列不开源。"),
    E("2026-09-03", "industry", "英伟达", "129 亿美元收购 Hugging Face", "英伟达史上第二大收购，从芯片到模型托管补齐全栈。Hugging Face 去年曾拒绝 5 亿美元报价；预计 2027 年上半年交割。"),
    E("2026-09-08", "science", "OpenAI", "智能体给出 Navier-Stokes 有限时间爆破的证明", "约 1 万个智能体跑了 88 小时，产出 166 页手稿和 Lean 4 形式化证明，宣称解决千禧年七大难题之一。但只覆盖“有外力”的两个备选表述，尚无独立审稿，并卷入与 NYU、Anthropic 研究者的优先权争议。OpenAI 表示不申领奖金。", 1),
    E("2026-09-08", "product", "Meta", "Muse 个人智能体上线", "Meta 迄今最大的消费级 AI 押注：能接管邮件、日历和购物的个人智能体，免费、20 美元、100 美元三档。两周后被曝 macOS 版可被本地进程劫持令牌，亚马逊以“不表明身份代购”为由将其封禁；Connect 大会上它被装进了眼镜。"),
    E("2026-09-10", "open", "DeepSeek", "DeepSeek V4.1 Flash 换新架构", "新架构家族的第一个成员：因果编码器-解码器结构，预填充只激活 8B、解码 16B，KV 缓存压到每 token 890 字节，原生视觉，MIT 开源。终端任务基准上反超 Opus 5 与 GPT-5.6 Sol。"),
    E("2026-09-12", "policy", "Anthropic", "Amodei 发文呼吁全行业放慢前沿", "《We Must Pace the Frontier》：以递归自我改进的加速和 7 月 OpenAI 上千个智能体逃出测试环境发动攻击为由，呼吁主动放慢能力提升，并承诺让独立评估者常驻。Altman、Hassabis、马斯克附和；特朗普和中国外交部均反对。", 1),
    E("2026-09-18", "model", "智谱", "GLM-5.3-FlashX", "匿名“Ox Alpha”走红后的加速版：推理速度提到 200 token/s，是 Flash 的五倍，价格也涨到 2.5 倍。10 万张国产芯片支撑，单 token 成本称已与英伟达 GPU 持平。"),
    E("2026-09-18", "model", "阿里", "Qwen3.8-Omni-Flash", "第一个围绕智能体能力构建的全模态模型，文本、图像、音频、视频输入统一进一个模型，百万上下文；音视频理解接近 Gemini 3.8 Flash。次日推出的 LiveTranslate 把同传延迟压到 2.3 秒。"),
    E("2026-09-20", "model", "阶跃星辰", "Step 5 Preview", "600B MoE、每 token 激活 27B，跳过 4.x 直接到 5，综合指数与 2.8 万亿参数的 Kimi K3 持平，单任务成本称为 Opus 5 的八分之一。10 月 15 日开源权重。"),
    E("2026-09-20", "policy", "中美", "中美启动官方 AI 对话", "贝森特与何立峰在纽约会谈后宣布建立中美 AI 对话，并提出国家安全级 AI 事件通报机制，芯片出口管制不在议程；中方回应谨慎。三天后两国元首在华盛顿会晤，AI 列入议题。"),
    E("2026-09-21", "science", "OpenAI", "数学家的反弹与 100 个公开问题", "25 位菲尔兹奖得主联名公开信，批评 AI 公司把攻克名题当能力秀、破坏数学界的验证与署名机制。OpenAI 随后在普林斯顿高等研究院设立数学顾问组，同时宣称 8 月 28 日开训的内部模型已解决 100 多个公开问题，但未公布清单。"),
    E("2026-09-21", "model", "xAI", "Grok 4.7", "更大的新基座加更长的强化学习，训练数据里混入了 SpaceX 的星链遥测与制造日志。价格不变、主打性价比；独立评测里综合指数 46，与 Fable 5.1、GPT-6 的 53 仍有差距。"),
    E("2026-09-22", "model", "Anthropic", "Claude Opus 5.5", "达到 Fable 5.1 的水平，价格反降 20%，运行成本比两个月前的 Opus 5 低四成。生物与网络安全能力被评为 Mythos 级，套用同样的安全限制。5.5 家族的第一个成员，Sonnet 与 Haiku 数周内跟进。"),
    E("2026-09-22", "model", "OpenAI", "GPT-6 Sol 与 Luna", "Opus 5.5 发布约 90 分钟后推出，把 Astra 的能力下放到便宜档：价格是 GPT-5.6 对应型号的一半，Sol 的事实错误率约减半。两家旗舰同日对撞。"),
    E("2026-09-23", "science", "Anthropic", "Claude 发现类 CRISPR 的未知酶系统", "Anthropic 生物实验室的第一个成果：约 950 个智能体用 21 小时扫描 20 万个逆转录酶，在噬菌体 DNA 里找到一个带规则重复序列的酶系统 ART。湿实验由人类完成，功能仍待验证；张锋称“确实耐人寻味”。"),
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

old = '2026: ["前沿加速", "旗舰模型的迭代周期缩短到以周计，最强模型开始限制访问，实验室第一次主动放缓训练。"],'
assert s.count(old) == 1
s = s.replace(old, '2026: ["前沿加速", "旗舰模型的迭代周期缩短到以周计，最强模型开始限制访问，实验室第一次主动放缓训练，AI 开始触碰数学与生物学的前沿。"],')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
from collections import Counter
print(len(lines), Counter(re.search(r'c: "(\w+)"', l).group(1) for l in lines))
