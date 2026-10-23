import re, sys, json
sys.stdout.reconfigure(encoding='utf-8')
p = 'index.html'
s = open(p, encoding='utf-8').read()
a = s.index('const EVENTS = [\n') + len('const EVENTS = [\n')
b = s.index('\n];', a)
lines = [l for l in s[a:b].split('\n') if l.strip()]
date_of = lambda l: re.search(r'd: "([\d-]+)"', l).group(1)
title_of = lambda l: re.search(r' t: "([^"]*)"', l).group(1)

E = lambda d, c, o, t, x, m=0: (d, c, o, t, x, m)
NEW = [
    E("2026-10-17", "open", "DeepSeek", "DeepSeek V4.1 Flash 1017", "V4.1 Flash 的新检查点，编程智能体基准 DeepSWE 得 77.0，11 项基准全部超过上一版；同时向所有开发者开放 Search 与 Fetch API，让开源模型也能直接联网检索。"),
    E("2026-10-19", "model", "MiniMax / Inception", "MiniMax M3.1 Flash 与 Mercury 3", "MiniMax 发布约 4280 亿参数的轻量旗舰 M3.1 Flash，前端与界面生成被评接近 Opus 5.5；同日 Inception Labs 推出扩散式语言模型 Mercury 3。"),
    E("2026-10-19", "industry", "Anthropic / Nscale", "与 Nscale 洽谈 450 亿美元算力合同", "继 Akamai 之后，Anthropic 据报又在与英国云厂商 Nscale 谈一笔 450 亿美元的算力合同，IPO 前的算力采购仍在加速。"),
    E("2026-10-21", "policy", "OpenAI / Wiz", "AI 发现 PHP 高危漏洞", "两个严重的远程代码执行漏洞，影响 PHP 过去十年的所有版本，WordPress、Drupal、Joomla 都受波及。发现者是用 GPT-5.6 Sol 的 Calif（OpenAI“Patch the Planet”计划）和用 Gemini 4 Argon 的 Wiz。细节在补丁前泄露，芬兰暂停政府网站，荷兰网络安全机构下线官网；OpenAI 拿出 10 亿美元补贴关键机构使用安全模型 Daybreak。", 1),
    E("2026-10-21", "product", "Anthropic", "Claude Duet", "基于 Opus 5.5 的主动型个人智能体，开放研究预览：在云端虚拟机里运行，接入 6000 多个应用，每天早上给一份摘要，之后只在需要拍板时打扰；发消息、花钱、签文件前必须先经用户同意。至此 Meta Muse、OpenAI Dots、Claude Duet 三家“常驻智能体”到齐。"),
    E("2026-10-21", "industry", "OpenAI / Google", "OpenAI 模型上架 Google Cloud", "GPT-6 Astra、GPT-6.1 Sol、GPT-6 Luna 和 Codex 进入 Google 的 Model Garden，先开私有预览。继 Azure、AWS、Oracle 之后，OpenAI 的模型覆盖了美国三大云，Google 开始转售最直接对手的模型。"),
    E("2026-10-21", "industry", "Meta 等", "AI 融资潮：Meta 新股与独角兽", "Meta 计划发行一类新股票为 AI 基建筹资；成立一年的 Flapping Airplanes 以 60 亿美元估值融资 10 亿，法律 AI 公司 Legora 估值升至 88 亿。"),
    E("2026-10-22", "industry", "DeepSeek", "DeepSeek 融资约 150 亿美元", "美国命令联邦民用机构移除 DeepSeek 产品的两天后，DeepSeek 据报融资约 1000 亿元人民币，宁德时代、腾讯在投资方之列，目标从 500 亿一路提到 1000 亿元，是中国最大的单笔融资之一。"),
    E("2026-10-22", "industry", "OpenAI", "OpenAI 以 1.25 万亿估值再融 300 亿", "据报为 IPO 做准备的新一轮，估值比 9 月传闻的 1.4 万亿略低；此前有报道称其营收比预测少约 200 亿美元。"),
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
