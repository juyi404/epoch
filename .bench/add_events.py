import re, sys, json
sys.stdout.reconfigure(encoding='utf-8')
p = 'index.html'
s = open(p, encoding='utf-8').read()

a = s.index('const EVENTS = [\n') + len('const EVENTS = [\n')
b = s.index('\n];', a)
lines = [l for l in s[a:b].split('\n') if l.strip()]


def date_of(l):
    return re.search(r'd: "([\d-]+)"', l).group(1)


def title_of(l):
    return re.search(r' t: "([^"]*)"', l).group(1)


# ---- 按参考站更精确的日期修正已有条目
FIX = {
    "DeepSeek V4": '  { d: "2026-04-24", c: "open", o: "DeepSeek", t: "DeepSeek V4 预览", x: "Pro 与 Flash 预览版以 MIT 许可开源，百万上下文、思考模式与智能体编程并入同一家族；同月 Qwen 3.6、Kimi K2.6 相继发布。" },',
    "Claude Fable 5 与受限的 Mythos 5": '  { d: "2026-06", c: "model", o: "Anthropic", m: 1, t: "Claude Fable 5 与受限的 Mythos 5", x: "Claude 5 家族登场，Sonnet 5 同月跟进。Fable 面向长时间运行的高难度智能体，能力更强的 Mythos 只向受限对象提供，最强模型不再默认公开。" },',
    "Claude Sonnet 5 与 Opus 5": '  { d: "2026-07-24", c: "model", o: "Anthropic", t: "Claude Opus 5", x: "定价与 Opus 4.8 持平、能力逼近 Fable，成为 Claude Max 的默认模型，支持百万 token 上下文。" },',
    "Kimi K3": '  { d: "2026-07-16", c: "open", o: "月之暗面", t: "Kimi K3", x: "2.8 万亿总参数的 MoE，原生视觉与百万上下文。7 月 27 日开放权重，成为当时参数最大的开源模型。" },',
}
seen = set()
for i, l in enumerate(lines):
    t = title_of(l)
    if t in FIX:
        lines[i] = FIX[t]
        seen.add(t)
assert seen == set(FIX), set(FIX) - seen

E = lambda d, c, o, t, x, m=0: (d, c, o, t, x, m)
NEW = [
    # 2022
    E("2022-12-07", "product", "Perplexity", "Perplexity 上线", "把检索和生成合成一个“答案引擎”，直接给出带来源的回答，对话式 AI 搜索由此起步。"),
    E("2022-12-15", "policy", "Anthropic", "Constitutional AI", "用一份写定的原则让模型批评、改写自己的输出，再以 AI 反馈做强化学习，减少对人工有害性标注的依赖。"),
    # 2023
    E("2023-01-13", "policy", "艺术家群体", "艺术家起诉图像生成公司", "Stability AI、Midjourney 等被指用受版权保护的作品训练模型，训练数据的合法性之争就此开打。"),
    E("2023-03-13", "open", "斯坦福", "Alpaca 低成本复刻", "用 5.2 万条 GPT-3.5 生成的指令微调 LLaMA-7B，花费约 600 美元，引发复刻闭源模型的热潮。"),
    E("2023-03-14", "model", "Anthropic", "Claude 发布", "与 GPT-4 同日，Anthropic 通过 API 与 Slack、Notion 等合作入口推出第一代 Claude。"),
    E("2023-03-23", "product", "OpenAI", "ChatGPT 插件", "第三方用 OpenAPI 描述接口，模型自行决定何时调用；浏览器与代码解释器插件一并推出。"),
    E("2023-03-30", "product", "开源社区", "AutoGPT", "让 GPT-4 自己拆目标、调工具、循环执行。它还很粗糙，却让“智能体”成了最热的词。"),
    E("2023-04-05", "open", "Meta", "SAM 分割一切", "可零样本分割任意图像中的任意物体，配套 10 亿个掩码的数据集，被视作视觉领域的基础模型。"),
    E("2023-04-07", "product", "阿里", "通义千问开启测试", "阿里自研大模型对外开放，此后沿 API 与开源 Qwen 两条路线扩张。"),
    E("2023-05-06", "product", "科大讯飞", "讯飞星火", "认知大模型发布，把大模型和讯飞的语音、教育业务绑在一起。"),
    E("2023-06-05", "open", "智谱", "ChatGLM 开源", "面向中文场景优化的对话模型，成为国产开源大模型的早期代表。"),
    E("2023-06-13", "product", "OpenAI", "函数调用", "开发者用 JSON Schema 声明函数，模型返回函数名和参数，工具调用从此有了标准接口。"),
    E("2023-06-15", "open", "百川智能", "Baichuan-7B 开源", "王小川创立的百川首个模型即开源，以开源加商业的双轨切入。"),
    E("2023-06-20", "open", "UC Berkeley", "vLLM 与 PagedAttention", "把 KV 缓存切成可分页映射的块，大幅减少显存浪费，成为大模型推理服务的事实标准。"),
    E("2023-07-06", "open", "上海 AI 实验室", "书生 InternLM", "科研机构主导的开源大模型，配套开源完整工具链。"),
    E("2023-08-01", "product", "Continue", "Continue 开源编程助手", "以 VS Code 与 JetBrains 扩展提供对话、补全和代码库上下文，开发者可自带模型。"),
    E("2023-08-03", "open", "阿里", "Qwen-7B 开放权重", "2.2 万亿 token 预训练，月活一亿以下可直接商用，Qwen 开源系列由此开始。"),
    E("2023-08-17", "product", "字节跳动", "豆包", "依托云雀大模型的对话助手，借字节的流量与免费策略，很快成为国内用户最多的 AI 应用之一。"),
    E("2023-08-30", "product", "MiniMax", "MiniMax 与海螺 AI", "自研大模型与对话应用同步推出，主打多模态与效率。"),
    E("2023-09-07", "model", "腾讯", "腾讯混元", "覆盖文本、代码与图像，接入微信和腾讯云。至此，国内互联网巨头都有了自研大模型。"),
    E("2023-09-21", "product", "微软", "Copilot 铺满全线", "Bing、Windows 与 Microsoft 365 统一以 Copilot 命名接入 AI，助手成为软件的新交互层。"),
    E("2023-09-27", "open", "Mistral AI", "Mistral 7B", "以 Apache 2.0 许可发布，小模型在多项基准上超过 Llama 2 13B，欧洲开源力量登场。"),
    E("2023-10-09", "product", "月之暗面", "Kimi 智能助手", "以长上下文、能读长文档为卖点，在国产对话产品中迅速出圈。"),
    E("2023-10-10", "science", "普林斯顿", "SWE-bench", "把 2294 个真实 GitHub Issue 变成可执行的评测任务，此后成为编程智能体的主要标尺。"),
    E("2023-10-17", "model", "百度", "文心大模型 4.0", "百度称综合能力与 GPT-4 相当，并接入搜索、地图、网盘等全线产品。"),
    E("2023-11-02", "open", "零一万物", "Yi-34B", "李开复创立的零一万物发布 Yi 系列，34B 版本跻身开源模型第一梯队。"),
    E("2023-11-04", "model", "xAI", "Grok", "马斯克的 xAI 发布首个模型，实时接入 X 平台，风格少约束。"),
    E("2023-11-15", "model", "阶跃星辰", "Step 系列", "姜大昕创立的阶跃星辰发布 Step 大模型，主打万亿参数与多模态，“六小龙”格局成形。"),
    E("2023-12-21", "model", "Midjourney", "Midjourney V6", "提示遵循和图中文字显著进步，生图从“调氛围”走向按描述出图。"),
    # 2024
    E("2024-01-16", "model", "智谱", "GLM-4", "对标同期 GPT-4，同时延续开源路线。"),
    E("2024-01-30", "science", "Neuralink", "首例人体脑机植入", "患者术后能用意念控制电脑光标，脑机接口进入临床阶段。"),
    E("2024-02-01", "open", "面壁智能", "MiniCPM", "小参数、中文友好的开源模型，主打在手机等端侧设备上运行。"),
    E("2024-02-02", "product", "Apple", "Vision Pro 发售", "以眼动、手势和语音交互，空间计算第一次成为可以买到的产品。"),
    E("2024-02-15", "model", "Google", "Gemini 1.5 百万上下文", "与 Sora 同日发布，一次可读数小时视频、整本书或整个代码库，长上下文从演示变成可用能力。"),
    E("2024-02-21", "open", "Google", "Gemma", "谷歌首次向社区开放自家模型权重，巨头开始开源闭源两线作战。"),
    E("2024-02-22", "model", "Stability AI", "Stable Diffusion 3", "改用多模态扩散 Transformer 架构，文字渲染与多主体遵循明显改善。"),
    E("2024-03-12", "product", "Cognition", "Devin", "在沙箱里规划、写代码、跑命令、查文档的软件工程智能体，把“AI 程序员”带进大众视野。"),
    E("2024-03-18", "product", "月之暗面", "Kimi 200 万字上下文", "一次读完几十本书或整份招股书，成为年初最出圈的国产 AI 应用。"),
    E("2024-03-28", "open", "AI21 Labs", "Jamba 混合架构", "首个把 Mamba 状态空间模型与 Transformer 结合的大规模模型，长上下文吞吐更高。"),
    E("2024-04-23", "model", "商汤", "日日新 5.0", "强调知识、数学、推理与代码，CV 起家的商汤全面转向通用大模型。"),
    E("2024-04-27", "model", "生数科技", "Vidu", "强调动态一致与角色稳定，是 Sora 之后最早可以试用的国产视频生成产品之一。"),
    E("2024-05-06", "open", "DeepSeek", "DeepSeek-V2 与价格战", "MLA 注意力加稀疏 MoE，API 价格远低于同行，直接引爆国内大模型价格战。"),
    E("2024-05-08", "science", "DeepMind / Isomorphic", "AlphaFold 3", "从蛋白质扩展到 DNA、RNA、小分子等多类生物分子的联合结构预测。"),
    E("2024-05-14", "model", "Google", "Veo", "在 I/O 大会上发布的文生视频模型，与 Sora 正面对位。"),
    E("2024-05-30", "product", "Anthropic", "Claude 工具调用正式可用", "Claude 返回结构化的工具调用请求，执行与权限检查仍交给客户端。"),
    E("2024-06-01", "model", "昆仑万维", "天工 / Skywork", "以搜索增强对话、多模态和开放权重推进，坚持全栈自研模型。"),
    E("2024-06-06", "open", "阿里", "Qwen2", "0.5B 到 72B 全尺寸开源，开源生态从单个模型走向完整系列。"),
    E("2024-06-17", "model", "Runway", "Gen-3 Alpha", "运动、时序一致性与可控性明显提升，巩固了在广告与影视预演中的位置。"),
    E("2024-06-21", "model", "华为", "盘古 5.0", "覆盖语言、多模态、视觉与科学计算，把昇腾硬件、模型和云绑成国产全栈。"),
    E("2024-07-12", "policy", "欧盟", "AI 法案刊登公报", "禁止用途、高风险系统、透明度与通用模型的分层规则正式成文，20 天后生效。"),
    E("2024-07-18", "model", "OpenAI", "GPT-4o mini", "以极低价格提供接近 GPT-4o 的能力，小模型加低价成为主流选择。"),
    E("2024-08-01", "open", "Black Forest Labs", "FLUX.1", "Stable Diffusion 原班人马出走后的作品，很快成为社区默认的高质量开放生图模型。"),
    E("2024-08-13", "model", "xAI", "Grok-2", "支持图像理解与生成，xAI 进入第一梯队，也引来关于约束尺度的争议。"),
    E("2024-08-22", "industry", "Anysphere", "Cursor 融资", "完成 6000 万美元 A 轮。它把对话、代码库索引与生成式编辑直接做进编辑器，AI 原生 IDE 路线确立。"),
    E("2024-09-13", "industry", "World Labs", "李飞飞创办 World Labs", "专注“空间智能”，让 AI 理解三维世界的几何与物理，世界模型从概念走向产品。"),
    E("2024-10-31", "product", "OpenAI", "ChatGPT 搜索", "对话中直接联网检索并附来源链接，正面挑战传统搜索引擎。"),
    E("2024-11-13", "product", "Codeium", "Windsurf", "以 Cascade 智能体处理跨文件任务，与 Cursor 争夺 AI 原生 IDE 市场。"),
    E("2024-12-03", "model", "亚马逊", "Amazon Nova", "覆盖文本、多模态与视频生成的自研模型家族，通过 Bedrock 提供给企业。"),
    E("2024-12-03", "open", "腾讯", "HunyuanVideo 开源", "大参数视频生成模型开放权重，进入开源视频模型第一梯队。"),
    E("2024-12-09", "science", "Google", "Willow 量子芯片", "量子比特越多、错误率反而指数下降，量子纠错迈过关键门槛。"),
    # 2025
    E("2025-01-15", "model", "Luma", "Ray2", "训练算力约为前代十倍，运动更快更连贯。"),
    E("2025-01-20", "model", "月之暗面", "Kimi K1.5", "与 R1 同日发布，用强化学习训练长链推理，多项基准对齐国际头部推理模型。"),
    E("2025-02-17", "model", "xAI", "Grok 3", "在约 10 万张 GPU 的 Colossus 集群上训练，主打推理与数学，xAI 进入前沿竞争核心圈。"),
    E("2025-03-11", "product", "OpenAI", "Responses API 与 Agents SDK", "内置网页搜索、文件搜索和电脑操作工具，并开源管理交接、护栏和追踪的智能体框架。"),
    E("2025-03-16", "model", "百度", "文心 4.5 与 X1", "原生多模态与深度思考模型同日上线，文心一言随之免费。"),
    E("2025-04-16", "product", "OpenAI", "Codex CLI", "与 o3 同日开源的终端编程智能体，在本地读仓库、改文件、跑命令。"),
    E("2025-05-16", "product", "OpenAI", "云端 Codex", "每个任务在隔离的云端环境里读仓库、改代码、跑测试，返回可审查的补丁。"),
    E("2025-06-11", "model", "字节跳动", "Seedance 1.0", "支持文、图输入与多镜头叙事，接入豆包，字节的视频生成走到台前。"),
    E("2025-08-20", "open", "DeepSeek", "DeepSeek V3.1", "扩展上下文、强化工具调用，延续高性价比开源旗舰路线。"),
    E("2025-11-13", "model", "OpenAI", "GPT-5.1", "GPT-5 的稳定升级，重点改进推理速度、成本与工具调用的稳定性。"),
    E("2025-12-15", "open", "DeepSeek", "DeepSeek V3.2", "更激进的稀疏注意力把推理成本继续压低。"),
    # 2026
    E("2026-02-12", "policy", "字节跳动", "Seedance 2.0 与版权风暴", "写实视频生成迅速出圈，数日内好莱坞片方和行业协会密集发函，全球上线受阻。"),
    E("2026-04-26", "product", "OpenAI", "Sora 停服", "Sora 网页与应用停止服务，API 于 9 月 24 日关停。短视频生成旗舰成了可持续性的反例。"),
    E("2026-05-19", "model", "Google", "Gemini 3.5 Flash", "定位高强度智能体与编程任务的主力模型，成为 Flash 系列默认版本。"),
    E("2026-07-03", "model", "字节跳动", "Seedance 2.5", "单次生成最长约 30 秒的连续片段，视频模型的竞争从画质转向原生时长。"),
    E("2026-07-08", "product", "OpenAI", "GPT-Live 全双工语音", "ChatGPT 语音能同时听和说，支持同声传译，成为付费与免费用户的默认语音模型。"),
    E("2026-07-09", "model", "OpenAI", "GPT-5.6", "Sol、Terra、Luna 三档分别覆盖旗舰能力、成本平衡与高吞吐，并加入多智能体编排与持久推理。"),
    E("2026-07-21", "model", "Google", "Gemini 3.6 Flash", "降低输出价格、保持百万上下文；官方确认 3.5 Pro 仍在测试，Gemini 4 已开始预训练。"),
    E("2026-07-31", "open", "DeepSeek", "DeepSeek-V4-Flash 正式版", "取代预览版，思考与非思考双模式；一周后整体上调 API 价格，低价策略出现转折。"),
    E("2026-08-02", "policy", "欧盟", "AI 法扩大执法", "面向公众的系统须表明 AI 身份，深度伪造须带机器可读标识，通用模型提供商开始受 AI 办公室监管。"),
    E("2026-08-03", "open", "阿里", "Qwen3.8 与 Qwen3.8-Max", "2.4 万亿总参数的稀疏 MoE，原生多模态、百万上下文，并宣布开源 Max 权重。"),
    E("2026-08-04", "science", "Google DeepMind", "Gemini Robotics 2", "视觉-语言-动作模型、具身推理与端侧模型一并发布，在人形机器人上演示。"),
    E("2026-08-05", "model", "字节跳动", "SeedRealtime", "音频、视频与文本统一在一个端到端全双工模型里，豆包全量上线视频通话。"),
    E("2026-08-06", "industry", "Google", "谷歌 AI 领导层重组", "Hassabis 转任 Alphabet 首席科学家，Koray Kavukcuoglu 接管 Gemini；Jeff Dean、Oriol Vinyals 等元老离职创业。", 1),
    E("2026-08-07", "product", "OpenAI", "GPT-5.6 Luna 向免费用户开放", "免费档默认模型换成 Luna，可无限次文本聊天，并第一次能主动调用更高推理。"),
    E("2026-08-10", "open", "Meta", "Muse Glimmer 开源", "约 30B 的稠密多模态智能体模型，由闭源 Muse Spark 蒸馏而来，可在消费级显卡上本地运行，Meta 重返开源。"),
    E("2026-08-12", "model", "xAI", "Grok 4.6", "约 1.5 万亿参数的 MoE，综合智能指数与 GPT-5.6 Sol 持平，价格明显更低。"),
    E("2026-08-13", "open", "DeepSeek", "DeepSeek-V4 Pro 正式版", "1.6 万亿参数，首次原生支持图像推理，编程智能体基准从 12.8 跃升到 62.7。"),
    E("2026-08-13", "model", "Google", "Gemini 3.7 Flash", "距 3.6 仅三周，编程基准从 49% 升到 65%，Flash 的迭代周期缩到以周计。"),
    E("2026-08-14", "model", "智谱", "GLM-5.3", "基座不变，靠大规模强化学习后训练把编程能力提升约五成，主打智能体编程与防御性网络安全。"),
    E("2026-08-18", "policy", "OpenAI", "OpenAI 主动放缓前沿训练", "内部评估认为下一代旗舰的网络攻防能力可能越过关键阈值，OpenAI 暂停部分训练、加固研究环境，前沿实验室首次公开踩刹车。", 1),
    E("2026-08-25", "industry", "OpenAI / 博通", "Jalapeño 推理芯片", "在 Hot Chips 公布成绩，每瓦性能为英伟达参照系统的 1.5 至 1.9 倍，年底前部署到自有机房。"),
    E("2026-08-26", "open", "智谱", "GLM-5.3-Flash 开源", "此前匿名登顶 OpenRouter 的 Ox Alpha 身份揭晓：GLM-5 系列首个原生多模态模型，约 10 万张国产芯片训练，MIT 许可开源。"),
    E("2026-08-26", "open", "阿里", "Qwen3.8-Flash 开源", "125B 总参、仅激活 6B，采用稀疏与线性混合注意力，训练成本下降约九成。"),
    E("2026-08-28", "open", "腾讯", "混元 Hy4 预览版开源", "770B 总参、49B 激活，上下文破百万，以 Apache 2.0 许可开放，并首次参与自身研发。"),
]

have = {title_of(l) for l in lines}
for d, c, o, t, x, m in NEW:
    assert t not in have, t
    ms = ' m: 1,' if m else ''
    lines.append(f'  {{ d: {json.dumps(d)}, c: "{c}", o: {json.dumps(o, ensure_ascii=False)},{ms} t: {json.dumps(t, ensure_ascii=False)}, x: {json.dumps(x, ensure_ascii=False)} }},')

lines.sort(key=date_of)  # 稳定排序：同日保持原有顺序在前
out, prev = [], None
for l in lines:
    y = date_of(l)[:4]
    if prev and y != prev:
        out.append('')
    out.append(l)
    prev = y
s = s[:a] + '\n'.join(out) + s[b:]

# 2026 年的描述跟着新条目更新
s = s.replace('2026: ["前沿加速", "旗舰模型的迭代周期缩短到以周计，访问受限的最强模型开始出现。"],',
              '2026: ["前沿加速", "旗舰模型的迭代周期缩短到以周计，最强模型开始限制访问，实验室第一次主动放缓训练。"],')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
from collections import Counter
print(len(lines), Counter(re.search(r'c: "(\w+)"', l).group(1) for l in lines))
