# Living Novel Engine PRD

## 1. 文档信息

| 字段 | 内容 |
| --- | --- |
| 产品名称 | Living Novel Engine |
| 文档类型 | 产品需求文档 PRD |
| 当前版本 | v0.8.0-A 至 v0.8.5-A Long Novel Memory 底座 + ActDirector-A + Discourse-aware Narrator-A + Dynamic Action Registry-A + Emergence Mining-A + Entity Aliases / Entity Resolution + Runtime Memory Consumption-A + Frontend Artifact Panel + Long Upload Productization + v0.8.6 Long Import Review + v0.8.7 Resumable Ingest Jobs + v0.8.8 Long Project Workspace + v0.8.9 Long Replay & Audit UI + v0.8.10-A/B Runner State Execution 已验收；v0.9.0-alpha Long Novel Creation Loop、v0.9.1 Provider & Cost Gateway Lite、v0.9.2 MasterSetting Workspace Lite、v0.9.3 Graph Memory Evaluation Spike、v0.9.4 Advanced Runner Evaluation Spike、v1.0-beta Commercial Hardening Scope-A、v1.0-beta Commercial Audit Log Schema-B、v1.0-beta Permission Matrix Draft-C、v1.0-beta Project Copyright Statement-D、v1.0-beta Quota & Observability Lite-E、v1.0-beta Local Deployment Readiness-F、v1.0-beta Cloud Persistence Boundary-G、v1.0-beta Account Project Space Boundary-H、v1.0-beta Audit Log Append Policy-I、v1.0-beta Project Retention Policy-J、v1.0-beta Copyright Audit Hook-K、v1.0-beta MasterSetting Audit Hook-L、v1.0-beta Worldline Selection Audit Hook-M、v1.0-beta State Execution Audit Hook-N、v1.0-beta Commercial Status Overview-O、v1.0-beta Audit Log UI & Export-P、v1.0-beta Settings Local Smoke Checklist-Q、v1.0-beta Release Preflight Checklist-R、v1.0-beta Rights Approval Checklist-S 与 v1.0-beta Deployment Observability Checklist-T 已整体收口；后续 v1.0-beta 商业化加固需继续拆分 |
| 阶段 | MVP 可交互产品原型 |
| 目标用户 | 网文读者、同人创作者、原创作者、互动叙事爱好者 |
| 核心命题 | 让小说从静态文本变成可运行、可干预、可分叉的故事世界 |

v0.1-v0.8 已完成能力与未做项总览见 [`completed/v0.1-to-v0.8-version-audit.md`](./completed/v0.1-to-v0.8-version-audit.md)。

产品化阶段归类见 [`productization-phase-map.md`](./productization-phase-map.md)。当前 PRD 中的 “MVP” 默认不是单一含义：v0.7-v0.7.5 指短中篇产品化 MVP 已成立；v0.8.0-A-v0.8.5-A 指长篇引擎底座 MVP 已成立；v0.8.6-v0.8.10 是把长篇底座产品化为普通用户工作流；v0.9.0-alpha 已整体收口为长篇共创 alpha 产品闭环，但仍不是商业级平台。

## 2. 背景

传统小说是单向内容消费：作者写好剧情，读者阅读结果。互动小说虽然允许用户选择分支，但大多数仍然依赖预设选项，用户是在选择作者提前准备好的路径。

随着 LLM、多智能体仿真、长上下文记忆和结构化生成能力的发展，文字小说有机会变成一种新的交互媒介：用户不再只是读者，而是进入一个由角色、记忆、世界规则、关系网络共同运行的故事世界。

用户可以观察角色自主行动，也可以像高维存在一样向世界施加变量。角色不一定服从用户，因为角色拥有性格、利益、记忆和命运惯性。当用户多次干预后，角色甚至可能逐渐感知到外部力量，从而打破第四面墙。

《第一玩家》第九世界、第十世界、第十一世界罗瓦莎相关设定为本产品提供了机制启发，包括高维观测、低语干预、多层模拟、世界线、主人公身份、人设约束、剧情修正、创生者等。产品只抽象机制，不复刻原作表达和具体设定。

## 3. 产品定位

### 3.1 一句话定位

不是读小说，而是进入一部正在活着的小说。

### 3.2 产品定义

Living Novel Engine 是一个 AI 驱动的活体小说引擎。它将用户导入的文本解析为可运行的故事世界，通过角色 Agent、多世界线状态、读者干预和叙事渲染，生成属于每个读者自己的动态小说体验。

产品不应要求用户必须先上传小说。正式入口应支持三种创建方式：

- 导入已有小说：从用户自己的文本、原创稿或本地研究文本进入故事世界。
- 主题创世：用户只输入题材、主题、主角、大概内容，AI 生成第一章和可运行世界。
- 内置样例：用户不准备材料也能立即体验。

### 3.3 产品差异

| 类型 | 核心方式 | 局限 | Living Novel Engine 的差异 |
| --- | --- | --- | --- |
| 传统小说 | 作者写死剧情 | 读者只能阅读 | 读者可观察和干预世界 |
| 互动小说 | 选择预设分支 | 自由度低，分支成本高 | 用户输入变量，世界自行消化 |
| AI 续写器 | 根据上文生成下文 | 容易遗忘设定、角色服从 prompt | 先维护世界状态，再生成正文 |
| AI 游戏 NPC | 与单个 NPC 对话 | 通常缺少长篇叙事结构 | 以章节、世界线和小说阅读为核心 |

## 4. 用户与场景

### 4.1 用户画像

#### 网文读者

- 需求：续写断更、拯救意难平、探索不同结局
- 痛点：作者停更、烂尾、角色死亡、剧情不符合期待
- 核心价值：获得个人化世界线

#### 同人创作者

- 需求：快速生成平行世界设定、角色互动和剧情分支
- 痛点：从零写作门槛高，保持人设一致难
- 核心价值：低门槛生成可继续加工的分支故事

#### 原创作者

- 需求：测试大纲、模拟角色行动、验证冲突是否成立
- 痛点：角色容易工具化，反派降智，群像线难管理
- 核心价值：剧情压力测试和角色行为推演

#### 互动叙事爱好者

- 需求：体验非预设分支的开放叙事
- 痛点：传统互动小说选择有限，游戏成本高
- 核心价值：文字版开放世界

## 5. 核心目标

### 5.1 MVP 目标

验证用户是否愿意为了以下动机持续互动：

- 续写断更文本
- 拯救意难平角色
- 探索平行世界线
- 观察角色自主行动
- 体验角色对干预的反抗

### 5.2 非目标

MVP 不做：

- 完整商业阅读平台
- 大规模社区分发
- 多本小说跨作品联动
- 3D 可视化世界
- 全自动长篇连载生成
- 未授权商业小说公开续写分发

## 6. 核心概念

### 6.1 活体小说世界

小说不再只是章节文本，而是由世界规则、角色状态、时间线、伏笔、关系和读者干预共同组成的动态系统。

### 6.2 世界线

每次重大干预都可能产生新世界线。世界线保留：

- 分歧节点
- 干预记录
- 角色状态
- 章节正文
- 伏笔状态
- 关键关系变化

### 6.3 故事合约

故事合约定义世界规则和角色边界：

- 战力体系
- 地理规则
- 时间线
- 人设边界
- 伏笔约束
- 不可破坏的核心设定

### 6.4 读者干预

用户不是选择 A/B/C，而是向世界施加变量：

- 梦境
- 低语
- 信件
- 谣言
- 天气
- 资源
- 危机
- 新事件
- 关键情报

用户输入的自由干预不能直接进入正文或强制角色执行。系统必须先把它编译为结构化的 `AbstractIntervention`：

```text
Raw Reader Input
  -> AbstractIntervention
  -> 世界观兼容性 / 合约风险 / 干预强度判断
  -> In-world Realization（梦境、低语、谣言、道具、事故、异象、拒绝等）
  -> 本次 Branch Axis
  -> 世界线候选
```

不同干预类型对应不同分支轴，不能固定为“相信 / 不信 / 半信半疑”：

| 干预类型 | 示例 | 合理分支轴 |
| --- | --- | --- |
| 信息型干预 | 告诉角色未来会发生某事 | 相信预知 / 怀疑但调查 / 拒绝预兆 |
| 强制行动型干预 | 让角色某时某刻必须做或不做某事 | 主动改道 / 被迫延迟 / 抗拒命运压力 / 干预失败但觉察异常 |
| 资源或物品注入 | 让角色捡到某物 | 同世界合理吸收 / 降级转译 / 拒绝 / 开启异设世界线 |
| 规则改写型干预 | 给主角系统、穿越者身份、现代武器 | 拒绝原世界线 / 转译成本世界规则 / 另开 Alternate Novel |

世界线因此分为两类：

```text
Divergent Worldline
  在原世界规则内分叉，例如预知梦、提前示警、误会、调查、角色改道。

Alternate Novel / AU Worldline
  改写世界前提或题材规则，例如系统降临、现代科技乱入、穿越者介入。
  这类分支应另开异设世界线，并生成新的 story_contract 差异说明，而不是挂成普通三分支。
```

### 6.5 剧情修正

当干预过强或违反合约时，系统触发修正：

- 角色不信
- 角色拒绝
- 世界线分叉
- 代价出现
- 其他势力补位
- 角色感知异常
- 系统提示合约冲突

### 6.6 第四面墙感知

角色可拥有 `fourth_wall_awareness` 数值。干预越频繁、越强烈、越违背角色逻辑，角色越可能察觉“外部力量”。

## 7. MVP 范围

### 7.1 输入范围

MVP 支持：

- 系统内置原创样例
- 用户上传 3-10 章文本
- 用户输入主题 / 题材 / 主角设定 / 大概内容，由 AI 生成第一章和初始故事世界
- 用户手动补充世界观和角色说明

MVP 不支持：

- 超长全文导入
- 自动训练原作者文风
- 多作品混合宇宙
- 公开分享受版权保护文本的生成续作

### 7.2 角色规模

MVP 支持：

- 5-8 个核心角色
- 1 个主角或主人公候选
- 1-2 个关键反派或冲突角色
- 2-4 个配角

### 7.3 推演规模

MVP 支持：

- 单场景推演
- 章节级结果
- 每次生成 2-3 条后续世界线，但分支轴由本次干预动态生成，不固定为相信 / 不信 / 半信半疑
- 每条世界线生成一段章节概要和一段正文样例

## 8. 用户流程

### 8.1 首次创建故事世界

```text
进入产品
  -> 选择入口：导入小说 / 主题创世 / 使用样例
  -> 导入小说：上传 3-10 章内容
  -> 主题创世：输入题材、主题、主角、大概内容
  -> 使用样例：选择内置原创世界
  -> 系统解析或生成角色、关系、世界规则
  -> 用户确认或编辑解析结果
  -> 生成初始故事世界
```

### 8.1.1 主题创世

```text
输入“我想看什么故事”
  -> AI 生成第一章正文
  -> 同步生成 world.yaml / characters.yaml / story_contract.yaml
  -> 生成 Baseline Worldline
  -> 用户选择静观其变或施加干预
```

### 8.2 静观其变

```text
打开阅读视窗
  -> 点击“时间流逝”
  -> 系统运行角色 Agent
  -> 生成无干预 Baseline Worldline 的下一章候选
  -> 用户阅读
  -> 保存为当前世界线新章节
```

### 8.3 干预命运

```text
选择关键节点
  -> 输入干预内容
  -> 干预编译器生成 AbstractIntervention
  -> 系统判断干预类型、世界观兼容性、强度和风险
  -> 判断进入 Divergent Worldline 还是 Alternate Novel
  -> 生成本次专属 Branch Axis
  -> 将干预转译为世界内变量
  -> 多 Agent 推演反应
  -> 生成 2-3 条世界线候选（分支名称随本次分支轴变化）
  -> 用户选择保留或继续推演
```

### 8.4 角色反抗

```text
用户多次强干预
  -> 系统计算角色异常感知
  -> 角色产生怀疑或抗拒
  -> 章节中出现第四面墙迹象
  -> 用户可继续解释、隐藏、加重或撤回干预
```

## 9. 功能需求

### F1. 文本导入

| 项 | 说明 |
| --- | --- |
| 功能描述 | 支持用户导入 3-10 章文本，或从主题创世生成第一章 |
| 输入 | txt/md 文本，或粘贴文本 |
| 输出 | 待解析文本包 |
| 验收标准 | 用户可成功导入文本并进入解析流程 |

### F1.1 主题创世

| 项 | 说明 |
| --- | --- |
| 功能描述 | 用户不上传小说，只输入主题、题材、主角和大概内容，AI 生成第一章与初始故事世界 |
| 输入 | 自由文本 prompt，可选题材、风格、主角设定、冲突方向 |
| 输出 | chapter_001.md、world.yaml、characters.yaml、story_contract.yaml、canon_chapter.md |
| 验收标准 | 生成结果可直接进入阅读、Baseline Worldline、干预和 resume 链路 |

### F2. 世界锚定

| 项 | 说明 |
| --- | --- |
| 功能描述 | 从文本中提取初始世界状态 |
| 提取内容 | 角色、关系、地点、势力、规则、伏笔、时间线 |
| 用户操作 | 确认、修改、补充 |
| 验收标准 | 生成可编辑的世界状态草案 |

### F3. 角色卡

| 项 | 说明 |
| --- | --- |
| 功能描述 | 为核心角色生成结构化 Agent 卡 |
| 字段 | 人设、目标、恐惧、记忆、关系、边界、当前状态 |
| 验收标准 | 每个核心角色拥有可审查的行为依据 |

### F4. 故事合约

| 项 | 说明 |
| --- | --- |
| 功能描述 | 维护世界规则和不可破坏边界 |
| 规则类型 | 战力、地理、时间、身份、伏笔、人设 |
| 验收标准 | 干预和推演会被故事合约审计 |

### F5. 阅读视窗

| 项 | 说明 |
| --- | --- |
| 功能描述 | 展示当前世界线章节正文 |
| 信息 | 当前章节、摘要、角色状态、伏笔提示 |
| 验收标准 | 用户可像阅读小说一样阅读当前世界线 |

### F6. 静观其变

| 项 | 说明 |
| --- | --- |
| 功能描述 | 用户不干预，仅推动时间流逝 |
| 系统行为 | 运行角色 Agent，生成无干预 Baseline Worldline |
| 验收标准 | 输出章节与当前世界状态保持一致，并可作为干预世界线的对照组 |

### F7. 干预面板

| 项 | 说明 |
| --- | --- |
| 功能描述 | 用户输入自由干预 |
| 干预类型 | 梦境、低语、信件、谣言、天气、危机、资源、新事件 |
| 验收标准 | 系统能识别干预对象、强度、可见性和风险 |

### F8. 多世界线生成

| 项 | 说明 |
| --- | --- |
| 功能描述 | 根据同一次干预生成多个可能走向 |
| 输出 | 2-3 条世界线候选；每条线带 branch_axis、divergence_reason、lineage_type |
| 验收标准 | 世界线之间有明确差异，并能说明分歧原因；信息型干预可生成相信/怀疑/拒绝，强制行动型和规则改写型干预必须生成不同分支轴 |

### F9. 世界线浏览器

| 项 | 说明 |
| --- | --- |
| 功能描述 | 展示主线与分支关系 |
| 展示内容 | 分歧点、干预、章节、角色命运变化 |
| 验收标准 | 用户可切换、继续、归档某条世界线 |

### F10. 剧情修正

| 项 | 说明 |
| --- | --- |
| 功能描述 | 处理违反人设或世界合约的干预 |
| 修正方式 | 拒绝、代价、分支、角色抗拒、异常感知 |
| 验收标准 | 用户强行干预时，系统不会无条件服从 |

### F11. 第四面墙感知

| 项 | 说明 |
| --- | --- |
| 功能描述 | 角色逐渐感知读者干预 |
| 触发条件 | 多次强干预、反复改写命运、违反角色边界 |
| 验收标准 | 角色可在章节中自然表达怀疑、追问或抗拒 |

### F12. 正史回放评估

| 项 | 说明 |
| --- | --- |
| 功能描述 | 对已有后续章节的文本，隐藏后续章节作为 holdout，评估无干预续写是否接近原作走向 |
| 输入 | 完结文本或多章节文本；运行时只开放前 N 章 |
| 输出 | canon_replay_report.json |
| 验收标准 | 报告包含事件命中、角色一致性、伏笔延续、主题偏移和相似度说明 |

## 10. 页面设计

### 10.0 视觉与交互原则

产品视觉不走纯赛博极客风。主体应是古风 / 墨水屏 / 纸面阅读质感，像一张安静、精致、可运行的小说书案。

高维系统感只在关键时刻克制出现：

- 施加干预后，允许短暂的文字重组、墨迹散开、世界线重排动效。
- 第四面墙触发时，允许正文局部朱砂色高亮和右侧 Agent 轨迹简短 warning。
- 不做大面积红屏、强闪烁、震屏、持续噪声动画或过度赛博 UI。
- 所有强反馈动效应短、轻、可关闭，优先服务“用户理解因果变化”。

核心设计原则：

- 可解释：用户要知道系统把干预理解成了什么。
- 可回滚：用户要敢于试错。
- 可比较：用户要看见原现实与新世界线的差异。
- 可克制：震撼来自少数关键时刻，不来自常驻特效。

### 10.1 首页

核心元素：

- 产品一句话介绍
- 创建故事世界
- 主题创世入口
- 导入小说入口
- 使用样例世界
- 最近世界线
- 故事封面（可由 Seedream 视觉资产生成；未配置时使用占位图）
- 版权与本地个人探索提示

### 10.2 世界锚定页

核心元素：

- 文本导入区域
- 解析进度
- 角色列表
- 世界规则列表
- 未完成伏笔
- 确认生成故事世界

### 10.3 阅读与干预页

布局：

```text
+-------------------------------------------------------------+
| 阅读视窗                                                     |
| 当前章节正文、上一章摘要、下一章生成结果                    |
+-----------------------------+-------------------------------+
| 角色状态                     | 干预面板                      |
| 头像 / 目标 / 情绪 / 关系 / 记忆 | 输入神谕 / 梦境 / 事件     |
| 人设边界 / 异常感知          | 干预强度 / 可见性 / 风险      |
+-----------------------------+-------------------------------+
| 世界线浏览器                                                 |
| 原作主线 -> 干预分支 -> 新分支                              |
+-------------------------------------------------------------+
```

#### Causal Diff / 因果差异块

用户在正文某一段附近施加干预时，不应默认整章刷新。系统应优先展示局部 Diff：

```text
被抹去的旧现实
  微红底、朱砂边、删除线或墨迹淡出

新凝聚的世界线
  浅青 / 玉绿色底、细边框、流式打字出现

操作
  确立此界线
  抹除这次改写
  回滚到干预前
  查看因果差异
```

交互语义：

- `确立此界线`：采纳新文本，该局部变化坍缩为当前世界线正史。
- `抹除这次改写`：拒绝这次推演，返回干预前局部文本。
- `回滚到干预前`：撤销本次干预及其派生状态，给用户心理安全感。
- `查看因果差异`：展开系统解释，包括 `AbstractIntervention`、branch axis、影响角色、状态变化、检索证据。

该交互借鉴 IDE / Git Diff，但视觉上不应变成代码编辑器；它是“微观世界线编辑器”，服务于读者理解因果链。

#### 干预后的即时反馈

- 正文区：局部文字可有短暂墨迹散开 / 重组 / 打字机效果，但不应遮挡长时间阅读。
- 角色状态：显示增量，例如 `好感 +30 (↑ +5)`、`心境：警惕 -> 平静`。
- Agent 轨迹：滚动展示关键步骤，如检索、角色计划、合约审计、状态投影、章节渲染。
- 回滚按钮：与继续世界线操作相邻，避免用户害怕“改坏了就回不去”。

#### 第四面墙 UI

当角色因多次干预或高智商 persona 觉察到叙事篡改：

- 正文中相关句子可局部朱砂色高亮。
- 右侧 Agent 轨迹显示简短警告，例如：`检测到高维叙事篡改，角色觉察上升`。
- 警告语气要克制，不使用夸张英文终端刷屏或强烈惊吓动效。
- 第四面墙效果应稀有，避免每次干预都高亮，削弱震撼。

### 10.4 世界线详情页

核心元素：

- 世界线树
- 分歧节点
- 干预记录
- 角色命运对比
- 分歧节点缩略图 / 场景图（可选视觉资产）
- 伏笔状态
- 继续推演按钮

### 10.5 故事评估与张力弧线

在 `Worldline Judge` 阶段，右侧故事评估不只展示单个“当前张力”进度条，还应支持 `Story Arc Curve`：

- 横轴：章节 / tick / 世界线节点。
- 纵轴：剧情张力、冲突强度或追读力。
- 展示干预前 baseline 与干预后世界线的走势差异。
- 若曲线长期平直，提示该世界线可能过于平淡。
- 若曲线突然飙升，提示该干预制造了高冲突或强反转。

## 11. 数据结构

### 11.1 StoryWorld

```json
{
  "id": "world_001",
  "title": "示例小说",
  "source_type": "user_owned_text",
  "rules": [],
  "characters": [],
  "locations": [],
  "factions": [],
  "timeline": [],
  "open_threads": [],
  "created_at": "2026-05-28T00:00:00+08:00"
}
```

### 11.2 CharacterAgent

```json
{
  "id": "character_001",
  "name": "角色名",
  "narrative_role": "protagonist_candidate",
  "persona": {
    "traits": [],
    "desires": [],
    "fears": [],
    "boundaries": []
  },
  "memory": [],
  "relationships": {},
  "current_state": {},
  "fourth_wall_awareness": 0
}
```

### 11.3 Intervention

```json
{
  "id": "intervention_001",
  "worldline_id": "canon",
  "target": "character_001",
  "type": "whisper",
  "content": "今晚不要去城外竹林",
  "strength": "soft",
  "visibility": "target_only",
  "contract_risk": "low",
  "created_at": "2026-05-28T00:00:00+08:00"
}
```

### 11.4 Worldline

```json
{
  "id": "worldline_001",
  "parent_id": "canon",
  "divergence_point": "chapter_42",
  "theme": "拯救意难平",
  "interventions": [],
  "chapters": [],
  "state_snapshot": {},
  "status": "active"
}
```

## 12. 生成策略

### 12.1 两阶段生成

第一阶段：结构化推演。

输出角色行动、对话意图、状态变化、冲突结果。

第二阶段：叙事渲染。

将结构化推演结果转为小说正文、章节摘要和状态更新。

### 12.2 模型分层

- 长上下文模型：文本导入与世界锚定
- 轻量模型：角色日常行动推演
- 强模型：章节正文渲染、复杂冲突处理
- 结构化输出：干预解析、状态更新、合约审计

## 13. 验收标准

### 13.1 产品验收

- 用户能导入文本并生成初始故事世界
- 用户不上传小说时，也能通过主题创世生成第一章和初始故事世界
- 系统能生成至少 5 个核心角色卡
- 用户能输入自由干预，而不是选择固定选项
- 系统能生成至少 2 条差异明确的世界线
- 用户能生成一条无干预 Baseline Worldline，并与干预世界线对比
- 角色不会无条件服从明显违背人设的干预
- 世界线浏览器能展示分支关系
- 用户能继续阅读某条世界线

### 13.2 体验验收

- 用户能理解“施加变量”与“选择分支”的区别
- 用户能感受到角色拥有自主性
- 用户能看懂一次干预造成的蝴蝶效应
- 生成内容没有明显前后矛盾
- 至少一个场景中出现合理的角色抗拒或剧情修正

### 13.3 安全与版权验收

- 产品明确提示上传文本版权责任
- 默认不提供公开发布受版权保护文本续写的能力
- 导出内容保留来源和 AI 生成说明
- 样例世界使用原创或公版内容

## 14. 指标

### 14.1 MVP 核心指标

- 创建故事世界成功率
- 主题创世完成率
- 世界锚定确认率
- 首次干预完成率
- 无干预基线继续率
- 世界线保存率
- 单用户平均生成世界线数量
- 用户是否愿意继续同一世界线

### 14.2 质量指标

- 角色一致性评分
- 世界规则冲突率
- 伏笔遗漏率
- 用户对分支差异的主观评分
- 用户对章节可读性的主观评分

## 15. 风险

### 15.1 版权风险

风险：用户上传商业小说并公开分享生成续作。

策略：

- 默认本地个人探索
- 分享前弹出版权确认
- 样例仅使用原创或公版内容
- 生成内容标注非原作者作品

### 15.2 成本风险

风险：多 Agent 推演和章节渲染消耗过高。

策略：

- MVP 限制角色数量和推演轮次
- 结构化推演使用轻量模型
- 仅最终正文使用强模型
- 对世界线生成设置额度

### 15.3 叙事失控风险

风险：角色过度自由导致剧情不可读。

策略：

- 故事合约审计
- 章节目标约束
- 叙事渲染器收敛
- 世界线候选由用户选择

### 15.4 用户预期风险

风险：用户以为可以精确控制结局，但系统强调角色自主性。

策略：

- 明确产品心智：干预变量，不是命令角色
- 干预前显示成功概率或风险
- 干预后解释角色为何没有照做

## 16. 版本规划

### v0.1 概念样例

- 内置原创短篇世界
- 手动角色卡
- 一次干预
- 生成 2-3 条世界线概要

### v0.2 文本导入

- 导入 3-10 章
- 自动提取角色和世界规则
- 可编辑世界锚定结果

### v0.3 长篇上下文检索

- v0.3.0：BM25 lite、章节距离衰减、facts / summaries / story_contract 注入角色决策和章节生成 prompt
- v0.3.1：ChapterBrief / VolumeBrief 轻量版，支撑 20+ 章项目的分层上下文
- 暂不做向量数据库、embedding、完整 MasterSetting 作者工作台和 MiroFish 多 Agent runtime；后续只在 v0.9.2 先做 MasterSetting Workspace Lite

### v0.4 世界线浏览器

- v0.4 / v0.4.1：只读世界线浏览器、分支对比、状态面板、边界加固
- v0.4.2（已验收）：UI polish；`lne browse` 读取各分支 `retrieval_context.json`，按合约约束 / 正史事实 / 章节摘要 / 卷摘要分组展示检索命中与分数

### v0.5 第四面墙（已验收）

- 干预痕迹记忆：`fourth_wall.json` 账本随世界线 lineage 累积（intervene / resume continue / resume intervene）
- 角色异常感知：四类触发器（不可能信息 / 反复救援 / 人设违背 / 命运修正）驱动五级觉察分数
- 角色追问与抗拒：≥unsettled 注入决策 prompt、≥suspicious 放开第四面墙渲染约束，正文出现怀疑/追问/反抗；`state_snapshot` 含 `fourth_wall_awareness`
- 默认开启；可经 `LNE_FOURTH_WALL=0` 完全关闭（不累积、不落盘、不注入）

### v0.6 深度仿真

- v0.6.0（已收口）：Runner Adapter——可插拔 `SceneRunner` + 注册表，`run_scene` 改薄包装，默认 `lightweight` 行为不变；输出契约仅 additive 增 `runner_name`/`runner`，可经 `LNE_SCENE_RUNNER` 切换
- v0.6.1（已收口）：Multi-Agent Runner Protocol——`orchestrator/runners/protocol.py` 定义角色计划/私下信息/误解/延迟行动/关系传播数据结构 + 设计文档；私有/误解默认不泄漏，未接入运行
- v0.6.2（已收口）：`multi_agent_stub` runner——`projection.py` 把 `MultiAgentTrace` 投影回 `AcceptedEvent`/`StateDelta`/`state_snapshot`，强制 reveal/corrected/due_round 规则；非默认（`lightweight` 仍默认），仅 additive 增 `multi_agent_trace`
- v0.6.3（已收口）：`multi_agent_trace` 可视化——`lne browse` 新增「Agent 轨迹」标签页展示角色计划/私下信息/误解/延迟行动/关系信号；后端 additive 增 `has_multi_agent_trace`/`multi_agent_trace_count`，缺失空态/损坏不抛
- v0.6.4（已收口）：自研 `multi_agent_llm` runner——通过 OpenAI-compatible API 调小模型一次性生成 `MultiAgentTrace` JSON，复用共享装配层 `assembly.build_result_from_trace` 与 v0.6.2 投影层；非默认、不本地部署、不引依赖；隐私加固 + 健壮回退（mock/无 API/异常→确定性 stub，不抛）
- v0.6.5（已收口）：多 Agent 推演工程可靠性——`generation_meta`（source/usage/重试/校验，additive 写进 `multi_agent_trace.json`，browse 可区分真 LLM/回退/stub）+ trace 质量校验器 `trace_quality.validate_and_repair_trace`（硬失败/就地修复/告警，绝不抛）+ 有限重试（`LNE_MULTI_AGENT_MAX_RETRIES`，默认 1）+ token usage（`chat_json_with_usage`）；并发/精确成本计算留待 v0.8+
- v0.7.1-A/B/C（已收口）：Intervention Compiler + LLM 编译 + Causal Diff 数据地基。自由输入先转 `AbstractIntervention`，判断 `Divergent Worldline` vs `Alternate Novel`，再生成本次专属分支轴；每个干预分支写出 `causal_diff.json`，供产品前端展示旧现实 / 新世界线差异。
- v0.7（已收口）：Product Web App，React/Vite 产品级前端；已完成三入口、世界锚定、Web 干预、Causal Diff 操作、运行设置与异步 Job 进度；详细 UI 规格见 `docs/completed/v0.7-product-web-app-ui-spec.md`
- v0.7.2（已收口）：Agent Interaction，补 `CharacterAction`、`CharacterProbe`、`InterventionGuardrail` 与轻量角色配置，让角色动作和干预护栏结构化
- v0.7.3（已收口）：Seedream 5.0 Lite 视觉资产层，为角色头像、故事封面、场景背景、世界线节点缩略图提供可选生成与本地缓存
- v0.7.4（已收口）：Baseline & Canon Replay，支持无干预基线、正史 holdout 和 deterministic 回放评估；主题创世入口已由 v0.7 完成
- v0.7.5（已收口）：Worldline Judge，branch 级 `worldline_judgement.json` + deterministic 评审 API/UI，评估角色一致性、合约风险、分支差异、故事弧、转折点、张力、anti-slop 与 emergence_score
- 多角色计划、误解、延迟行动、关系传播
- 小模型推演 + 大模型写正文的分层策略
- Zep Cloud / 图数据库 / GraphRAG 暂不作为主线依赖；仅作为 v0.9.3 Graph Memory Evaluation Spike（长篇记忆、BM25 或 canon ledger 召回明显不足时再评估）
- OASIS / CAMEL / LangGraph 暂不作为主线架构；仅作为 v0.9.4 Advanced Runner Evaluation Spike（v0.8.10 状态执行层不足以表达复杂群体仿真或多轮状态流转时再评估）

### v0.7 产品级前端

- 已完成 React + Vite + TypeScript 独立 Web App
- 普通用户可在 Web 内完成导入小说、主题创世、编辑世界锚定、发起干预、查看干预编译结果、选择分支、阅读世界线
- 已复用现有引擎与 browser API，不重写核心推演逻辑
- `lne browse` 保留为开发者只读 viewer；产品前端承担真正用户体验
- 不要求用户复制 CLI 命令
- 已接入 Causal Diff 确立 / 抹除 / 回滚 artifact 状态、运行设置面板、异步 Job 进度轮询
- 后续只做小 polish：创世徽标、真实 LLM smoke checklist、推荐下一步文案、错误态统一
- 视觉方向必须保持古风纸面 / 中文小说编辑器 / 克制系统感，不做纯赛博极客风

### v0.7.4 Baseline & Canon Replay

> 该阶段收口状态：已收口。后端基线经 Codex 兜底后为 `526 passed`，前端 `pnpm run build` 通过；当时补强了 service 层 id 安全校验，并将 holdout UI 默认覆盖改为 false。当前全项目基线以 `memory.md` 为准。

- 三种入口已由 v0.7 Product Web App 完成：导入已有小说、主题创世、内置样例
- `Baseline Worldline`：无高维干预，角色按人设、记忆、世界规则和伏笔压力自然推进
- `Intervened Worldline`：用户施加变量后产生的世界线
- UI 需要能对比“无干预时世界如何发展”和“干预后世界如何偏离”
- 对完结文本或有后续章节的本地文本，可把后续章节作为 holdout，生成 `canon_replay_report.json`
- 如果只输入第一章，系统只能合理预测后续，不能承诺等于原作；如果导入全本，后续章节只能作为本地评估集，不应泄漏给运行时角色和 narrator

### v0.7.3 Seedream 视觉资产

- 接入用户已有的 Seedream API，模型为 Seedream 5.0 Lite
- 请求地址：`https://ark.cn-beijing.volces.com`
- 用途：角色头像、故事封面、场景背景、世界线节点缩略图
- 资产应本地缓存，并记录 prompt、模型、来源字段、生成时间和文件路径
- 生图失败或未配置 API Key 时，UI 使用占位图，不影响导入、干预、续章和阅读
- 不用受版权保护作品原图或真人演员脸做复刻；导入商业小说时默认生成原创化概念图

### v0.8 Long Novel Memory / 百万字长篇支撑

目标：支持 100 万字以上、乃至 200-600 万字长篇文本的导入、运行、续章和评估，避免角色偏离人设、时间线矛盾、资源状态错乱和伏笔遗忘。

核心原则：

- 不把整本书塞进上下文窗口。
- 上传、解析、索引、评估必须异步化。
- 运行时只注入当前场景真正需要的合约、状态、摘要和证据。
- 写后必须沉淀为正史账本，并通过审计发现矛盾。

#### v0.8.0 Long Novel Ingestion

- 支持 txt / md / epub / zip 大文件导入。
- 前端分片上传，后端创建 `ingest_job`。
- 原文落 `source_raw/`，清洗后落 `source/`。
- 导入任务支持进度、失败恢复、部分完成状态。
- 先完成前若干章即可进入体验，后续章节继续异步索引。
- 导入报告展示：总字数、章节数、缺章/重复章、乱码风险、角色抽取置信度、时间线风险。

当前已完成第一刀：导入落盘统一生成 `source_raw/` 与 `import_report.json`；Web/job 导入支持 `long_mode`（默认仍为 3-10 章，长篇模式最多 200 章）；API 返回导入报告摘要，包含总字数、章节数、前 20 章可体验范围、部分完成标记、疑似乱码、重复章名与缺章编号。

当前已完成上传产品化、导入检查、断点续传、长篇项目工作台、长篇回放审计 UI 和状态执行 A/B：导入页支持 txt/md/zip/epub 文件选择、服务端 ingest session 分片续传、job 进度条和失败空态；后端 `upload` payload 支持 base64 分片还原、txt/md 拆章、zip 内 txt/md 章节、epub 内 html/xhtml 章节；`import_report.json` 会记录来源、章节统计、章节片段、解析 warning、质量风险与建议动作，前端世界锚定页用「导入检查」帮助用户确认“导入了什么、有什么风险、下一步做什么”。`WorkspacePage` 已在未选世界线时集中展示章节、记忆、正史账本、实体别名、检索命中和审计报告；「回放与审计」面板支持单章/范围 Canon Replay、风险维度和实体归一化审计；「机制档案」可生成状态执行 dry-run 报告，并在显式确认后把 low-risk 白名单 delta 写入可回滚的 `state_execution_overlay.json`。角色抽取置信度、时间线语义风险、运行后审计写回和 overlay 自动驱动下一轮 runner 仍留后续小刀。

#### v0.8.6-v0.8.10 Long Novel Productization 收束

v0.8 后半段不直接跳 v0.9，先把“上传成功”推进到“用户能确认、审计、继续创作”的长篇产品闭环前置层。

| 版本 | 名称 | 产品目标 |
| --- | --- | --- |
| v0.8.6 | Long Import Review | 导入报告细化、章节列表/正文片段预览、导入质量空态、坏 zip/epub/空文件/章节过少等错误态收束 |
| v0.8.7 | Resumable Ingest Jobs | 服务端分片 session、断点续传/恢复、hash 校验、重复 chunk 幂等、过期清理 |
| v0.8.8 | Long Project Workspace | 长篇项目详情页展示章节、记忆、正史账本、实体别名、检索命中、审计报告，并支持从项目发起 baseline/intervention |
| v0.8.9 | Long Replay & Audit UI | 长篇 Canon Replay / Consistency Audit 前端产品化，支持章节范围、风险维度和实体归一化审计展示 |
| v0.8.10-A | Runner State Execution Spike | 已收口：opt-in 评估动作计划、动作注册表、涌现节点是否能安全转成状态变化；不改默认行为 |
| v0.8.10-B | Runner State Execution MVP | 已收口：low-risk 白名单 delta 写入可回滚 overlay，保持 artifact/API additive |

#### v0.9.0-alpha Long Novel Creation Loop

v0.9.0-alpha 已整体收口，已经串起完整用户路径：

```text
上传原作/设定 -> 查看记忆与导入报告 -> 发起分支运行 -> 审计偏移 -> 选择世界线 -> 导出章节
```

当前已完成的 v0.9.0-alpha 子刀：

- **Chapter Export**：所选世界线可通过只读 API 和阅读区按钮导出 Markdown，导出内容包含来源说明、AI 生成说明、评审摘要与章节正文；不写回 `chapter.md`，不导出上传原作全文或 holdout 私有正文。
- **Chapter Collection Export**：当前分支可沿父链导出连续章节合集，合集只包含生成章节、来源 run/branch 和安全 warning，不导出上传原作全文。
- **Export Share Guard**：单章导出与合集导出均返回 `share_guard`，Markdown 写入「版权与分享边界」，前端下载前要求中文确认版权责任；v1.0-beta Copyright-D 后会附带项目级 `rights_basis`，但该 guard 不等于公开分享发布能力。
- **Creation Loop Completion Gate**：`creation_loop` 返回 `completion`，显示完成/总数、阻塞项、summary 与 `can_mark_alpha_complete`，前端展示闭环完成度；该判定只读，不替代人工版本收口。
- **Creation Loop Action Hints**：`completion.actions` 把缺失评审、未选起点、未跑审计等阻塞项转成可执行/可跳转动作；前端可直接生成推荐世界线评审或跳转审计页。
- **Creation Loop Readiness Evidence**：`completion.evidence` 把清单项映射到 artifact、API 或页面依据；前端完成度区展示判定来源，方便用户复盘“为什么还没收口”。
- **Creation Loop Audit Quick Run**：当已选世界线缺少范围回放且存在 baseline/holdout 时，`completion.actions` 返回 `run_replay_range` payload；前端可直接运行范围回放并刷新工作台。
- **Creation Loop Alpha Ready State**：补齐导入质量、候选世界线、评审、静态审计、选择后审计、章节导出和版权 guard 后，`can_mark_alpha_complete=true`；前端标题状态显示「可收口」。
- **Creation Loop Alpha Closeout Report**：`creation_loop.closeout` 汇总 alpha 收口状态、剩余阻塞、判定依据和下一步建议；前端显示「Alpha 收口」面板。
- **Creation Loop Closeout API**：`GET /api/stories/<slug>/creation-loop-closeout` 直接返回 `completion_status`、`actions` 与 `closeout`，供真实样例或导入项目做自动验收和阻塞补齐；`closeout.remaining_blocker_ids` 给出稳定阻塞项 id，`worldline_judgement` 与 `select_worldline` action 带可直接 POST 的 payload，`replay_audit` action 带只读 requirements 说明缺少的审计前置条件。
- **Requirements UI Display**：前端「创作闭环」完成度区会展示 action requirements 的中文前置条件，解释为什么当前只能跳转审计页或需要先补起点、baseline、holdout。
- **Builtin Holdout Blocked Requirement**：内置样例无法录入 holdout 时，`canon_holdout` requirement 标为 `blocked` 并提示需导入长篇项目后录入 holdout，避免把只读样例误判为普通缺失。
- **Creation Loop Closeout CLI**：`lne creation-loop-closeout <slug>` 可本地验收 closeout 状态，`--json` 输出与 HTTP 同构 payload，`--require-ready` 在未 ready 时失败，用于导入项目 alpha 收口闸门。
- **Creation Loop Closeout Record**：`lne creation-loop-closeout <slug> --write-report` 仅在 ready 后写入项目级 `creation_loop_alpha_closeout.json`，记录 closeout 依据；未 ready 或 builtin 样例不落盘。
- **Low-risk Audit Closeout**：静态审计中 `risk_level=low` 的 info 提示不再阻断 alpha ready；中高风险、缺失实体、缺评审、缺选择、缺导出仍阻断。
- **Creation Loop Checklist**：长篇项目工作台新增只读 `creation_loop`，展示推荐世界线、候选分支、导入/分支/评审/审计/导出五步清单和下一步提醒。
- **Continuation Hint**：推荐世界线下展示 CLI 续写入口 `lne resume continue <run_id> --branch <branch_id> --mock`，作为 HTTP resume job 前的最小继续创作入口。
- **Resume Continue HTTP Job**：推荐世界线可通过显式按钮触发 `/api/jobs/resume-continue`，沿父分支生成新的 `linear` 下一章并跳转阅读；不改 `run_scene` 默认行为。
- **Worldline Selection Persistence**：用户可把推荐或候选世界线「设为起点」，写入 `selected_worldline.json` 并在 `creation_loop.selected` 中读回。
- **Post-run Audit Entry**：`creation_loop.post_run_audit` 围绕已选世界线展示评审、Causal Diff、静态一致性审计、范围回放风险、缺失实体和下一步审计入口。

v0.9.0-alpha 已通过本地导入项目 `v090-alpha-proof` 写入 `creation_loop_alpha_closeout.json` 完成 alpha 收口声明；公开分享发布、provider/cost gateway 不在该版本内。运行后审计目前是只读入口，尚未写回正史账本或驱动下一轮 runner。

#### v0.8.1 Hierarchical Memory

项目应逐步升级为分层记忆结构：

```text
master_setting.yaml
volumes/volume_001.yaml
chapters/chapter_0001.yaml
scenes/chapter_0001_scene_01.yaml
character_states/<character_id>.yaml
timeline.yaml
plot_threads.yaml
propagation_debts.yaml
```

当前已完成第一刀：导入项目会生成 `memory/` 目录与 `memory_manifest.json`，并写入 `master_setting.yaml`、volume/chapter memory、character states、timeline、plot_threads、propagation_debts。当前这些 artifact 只作为可审计骨架和后续能力输入，不改变 runner 默认行为。

分层职责：

- Contract Layer：世界规则、人设边界、题材规则、战力上限。
- Timeline Layer：时间、地点、事件顺序、角色同时性。
- State Layer：角色状态、关系、资源、伤势、秘密、第四面墙觉察。
- Retrieval Layer：facts / summaries / briefs / raw chunks 的相关证据。
- Audit Layer：写完后反查矛盾。

#### v0.8.2 Canon Ledger

将 `facts.jsonl` 升级为正史账本，记录：

- events
- state changes
- relationships
- resources
- timeline facts
- foreshadowing / unresolved threads

每条记录应包含章节、场景、实体、事实陈述、来源引用、置信度、有效期和真伪状态。

当前已完成第一刀：导入时生成 `memory/canon_ledger.jsonl`，并在 `memory_manifest.json` 记录账本 layer。账本从章节事件、角色状态、角色关系和开放伏笔生成统一字段；旧 `canon/facts.jsonl` 继续保留，保证现有检索链路不变。

#### v0.8.3 Hybrid Retrieval

检索链路：

```text
query
  -> entity extraction
  -> BM25
  -> chapter distance decay
  -> entity boost
  -> source weight
  -> optional vector / reranker
  -> prompt budget pack
```

Prompt 预算：

- 固定必带：story contract、当前角色状态、当前时间线。
- 近邻必带：最近 3-5 章摘要、最近事件。
- 检索补充：与当前场景相关的事实、伏笔、旧章节证据。
- 审计反馈：上一轮发现的矛盾和待修复项。

向量库、embedding、reranker 不作为 v0.8.0 必选项；当 50+ 章或 100 万字以上作品中 BM25 召回不足时再启用。

当前已完成第一刀：现有 BM25 检索会读取 `memory/canon_ledger.jsonl`，以 `canon_ledger` source 进入 `retrieval_context.json`，并保留 entities、ledger_type、confidence。暂不接向量库、embedding、reranker。

当前已完成 v0.8.x entity aliases 第一刀：导入时生成 `memory/entity_aliases.yaml`，从角色、地点、势力和 canon ledger entities 形成 deterministic alias skeleton；检索读取 alias map，对 query 与 corpus 做轻量别名扩展，命中项可返回 `resolved_entities`；一致性报告记录 `entity_alias_count`；世界锚定页只读展示别名状态。暂不做 LLM/NER 抽取、人工别名编辑或跨 run 写回。

当前已完成 Runtime Memory Consumption-A：新增 `runtime_memory_context.json` 分支 artifact，把 entity aliases 状态、resolved query entities、retrieval/canon ledger 命中和 consumed layers 打包为只读运行时记忆上下文；干预、baseline 与 CLI resume 通过既有 `retrieved_context` 参数注入角色 Agent 与 narrator，不改 `run_scene` 默认行为。别名文件缺失/损坏只降级为 warning，不阻断生成。当前已完成 Frontend Artifact Panel：React 右侧解释面板新增「机制档案」，统一只读展示运行记忆、动作计划、动作注册表、叙事诊断、涌现节点；暂不让 `act_director_plan`、`dynamic_action_registry` 或 `emergence_nodes` 驱动状态变化。

#### v0.8.4 Consistency Audit

审计维度：

- 角色一致性：目标、恐惧、关系、口癖、能力边界。
- 时间线一致性：日期、地点、同时性、事件先后。
- 资源一致性：道具、伤势、货币、灵力、身份、秘密。
- 合约一致性：世界规则、战力体系、题材边界。
- 伏笔债务：未解伏笔是否遗忘，设定改动是否产生 propagation debt。

输出 `consistency_report.json`，包含冲突位置、证据、风险等级和修复建议。

当前已完成第一刀：导入时生成 `memory/consistency_report.json`，并在 manifest 中记录 consistency layer。报告先做静态审计：把导入报告中的乱码、重复章名、缺章风险转成 timeline/resource 风险，把开放伏笔登记为待追踪项；后续再接运行后的角色漂移、资源凭空变化和写后审计。

#### v0.8.5 Long Canon Replay Evaluation

完结文本导入时，系统应区分：

```text
runtime_visible/
  前 N 章，角色、narrator、retrieval 可见

holdout_private/
  后续章节，只给 evaluator 可见
```

要求：

- holdout 不得进入角色、narrator、多 Agent runner 或检索 prompt。
- evaluator 可读取 holdout，生成 `canon_replay_report.json`。
- 如果只上传第一章，系统只能合理预测后续，不承诺复现原作。
- 如果上传全本，默认只作为本地个人评估，不提供公开分发受保护文本续写的能力。

当前已完成第一刀：写入 holdout 时会生成 `canon/visibility_manifest.json`，并镜像私有章节到 `holdout_private/`。`runtime_visible` 明确列出 `source/` 可见章节，`holdout_private` 只给 evaluator；`get_holdout()` 返回该 manifest 摘要，检索链路不会读取私有章节正文。

验收：

- 可导入 100 万字以上文本并生成导入报告。
- 导入任务可恢复。
- 无干预续章能引用远期相关正史证据。
- 至少能发现一类人设、时间线、资源或伏笔矛盾。
- 隐藏评估集不会泄漏给运行时。

### v0.9.x / v1.0+ 产品化与商业化排期

v0.9 不再定义成“重依赖商业化增强”的大包。v0.9 先服务长篇共创闭环，优先把现有文件型引擎做成稳定产品；Zep、图数据库、OASIS/CAMEL、LangGraph 等外部重依赖只在明确触发条件满足后进入 spike，不作为 v0.9.0 默认主线。

| 版本 | 名称 | 范围 | 触发条件 |
| --- | --- | --- | --- |
| v0.9.0-alpha | Long Novel Creation Loop | 上传 -> 记忆 -> 分支运行 -> 审计 -> 选择世界线 -> 导出章节，形成第一条长篇共创闭环 | 已整体收口，见 `completed/v0.9.0-alpha-long-creation-loop.md` |
| v0.9.1 | Provider & Cost Gateway Lite | 多 provider 配置、模型路由、成本/用量估算、失败回退、Key 脱敏展示 | 已整体收口，见 `docs/completed/v0.9.1-provider-cost-gateway-lite.md`；不默认接 Zep / 图数据库 / OASIS / CAMEL / LangGraph |
| v0.9.2 | MasterSetting Workspace Lite | 项目级世界设定、人物、时间线、道具、伏笔、章节摘要的只读/轻编辑工作台 | 已整体收口，见 `completed/v0.9.2-master-setting-workspace-lite.md`；项目工作台已展示设定、人物、时间线、伏笔和章节摘要，并支持 `master_setting.yaml` 白名单后端保存与前端最小写控件 |
| v0.9.3 | Graph Memory Evaluation Spike | 评估 Zep / 图数据库 / GraphRAG 是否替换或增强现有 `canon_ledger` + BM25 + entity aliases | 已整体收口，见 `completed/v0.9.3-graph-memory-evaluation-spike.md`；当前只保留触发报告、检索 probe 与失败样例收集，不进入重依赖实现 |
| v0.9.4 | Advanced Runner Evaluation Spike | 评估 LangGraph 局部 runner、OASIS/CAMEL 可选 runner 是否值得接入 | 已整体收口，见 `completed/v0.9.4-advanced-runner-evaluation-spike.md`；当前只保留触发报告、runner probe 与失败样例收集，不进入重依赖实现 |
| v1.0-beta Scope-A | Commercial Hardening Scope | 账号/项目空间、权限、云端持久化、配额、审计日志、版权提示、部署与观测范围复核 | 已收口，见 `completed/v1.0-beta-commercial-hardening-scope-a.md`；当前只保留只读范围报告，不进入云端多租户、对象存储或计费系统 |
| v1.0-beta Schema-B | Commercial Audit Log | 本地项目审计日志 schema 与只读聚合 | 已收口，见 `completed/v1.0-beta-commercial-audit-log-schema-b.md`；追加写入口已在 Audit-I 收口 |
| v1.0-beta Matrix-C | Permission Matrix Draft | owner/editor/viewer 权限矩阵草案 | 已收口，见 `completed/v1.0-beta-permission-matrix-draft-c.md`；继续只读，不接认证系统、不拦截请求 |
| v1.0-beta Copyright-D | Project Copyright Statement | 项目级版权/来源声明 schema | 已收口，见 `completed/v1.0-beta-project-copyright-statement-d.md`；继续不提供公开发布入口 |
| v1.0-beta Quota-E | Quota & Observability Lite | 本地配额、用量、job 状态与观测摘要 | 已收口，见 `completed/v1.0-beta-quota-observability-lite-e.md`；不接真实计费系统或云端监控平台 |
| v1.0-beta Deploy-F | Local Deployment Readiness | 本地部署健康检查、环境脱敏、静态资源/API 冒烟和运行步骤 | 已收口；不接云端托管或多租户账号 |
| v1.0-beta Cloud-G | Cloud Persistence Boundary | 本地 artifact 到未来平台资源的映射、保留规则和迁移边界 | 已收口；不接对象存储、数据库或持久队列 |
| v1.0-beta Account-H | Account Project Space Boundary | 本地账号语义、项目空间清单和未来团队归属边界 | 已收口；不接真实认证、团队空间或请求级 ACL |
| v1.0-beta Audit-I | Audit Log Append Policy | 本地项目审计日志白名单追加策略 | 已收口；不接云端不可篡改审计存储或真实账号 |
| v1.0-beta Retention-J | Project Retention Policy | 本地项目删除/保留策略 artifact 与 API | 已收口；不实际删除文件、不接对象存储或数据库 |
| v1.0-beta Audit Hook-K | Copyright Audit Hook | 版权/来源声明写入接入本地审计日志 | 已收口；不改变版权 API 行为、不接云端不可篡改存储 |
| v1.0-beta Audit Hook-L | MasterSetting Audit Hook | 设定轻编辑写入接入本地审计日志 | 已收口；不改变设定编辑 API 行为、不接云端不可篡改存储 |
| v1.0-beta Audit Hook-M | Worldline Selection Audit Hook | 世界线选择写入接入本地审计日志 | 已收口；不改变选择 API 行为、不接云端不可篡改存储 |
| v1.0-beta Audit Hook-N | State Execution Audit Hook | 状态 overlay apply/rollback 接入本地审计日志 | 已收口；不改变状态执行规则、不接云端不可篡改存储 |
| v1.0-beta Status-O | Commercial Status Overview | 设置页商业化状态总览 | 已收口；只读展示本地商业化状态，不执行认证/云端/计费 |
| v1.0-beta Audit UI-P | Audit Log UI & Export | 项目工作台审计时间线展示与 Markdown 导出 | 已收口；导出不含事件 metadata，不代表不可篡改审计证明 |
| v1.0-beta Smoke-Q | Settings Local Smoke Checklist | 设置页本地冒烟清单 | 已收口；只生成 checklist，不主动打请求、不接真实部署系统 |
| v1.0-beta Preflight-R | Release Preflight Checklist | 发布前只读检查清单 | 已收口；只读聚合本地证据，不执行真实发布、不接云端部署系统 |
| v1.0-beta Rights-S | Rights Approval Checklist | 项目版权审批准备度只读检查 | 已收口；不执行真实审批、不开放公开发布、不接云端不可篡改审计 |
| v1.0-beta Observe-T | Deployment Observability Checklist | 部署观测只读清单 | 已收口；不 tail 日志、不接云端观测或持久队列 |

明确不作为当前排期默认项：

- 不在 v0.9.0-alpha 直接接 Zep / 图数据库。
- 不在 v0.9.0-alpha 直接接 OASIS / CAMEL。
- 不把 LangGraph 替换为主架构；最多作为某个 opt-in runner 的内部实现。
- 不先做完整作者工作台；先做 `MasterSetting Workspace Lite`，只覆盖长篇闭环必须字段。

## 17. 开放问题

- 世界线是默认自动分叉，还是用户确认后分叉？
- 干预编译后，用户是否必须确认 `AbstractIntervention` / `Branch Axis` 才生成世界线？
- `Alternate Novel` 是否默认另开项目级 AU，还是挂在原故事下作为特殊 lineage？
- 主题创世生成的第一章是否允许用户多次重抽，还是进入世界后只能通过干预改变？
- Canon Replay 的 holdout 章节是否由用户手动指定，还是系统自动拆分？
- 百万字上传时，用户是否可以在完整索引完成前先体验前 20 章？
- 长篇导入的分卷边界由用户确认，还是系统自动推断后允许编辑？
- 向量检索是否作为项目级可选开关，还是超过章节/字数阈值后自动启用？
- `holdout_private` 是否允许用户在本地查看评估详情，还是只展示聚合分数？
- 干预是否需要成本系统，防止用户无限强改？
- 角色第四面墙感知是否默认开启，还是由故事类型决定？
- 受版权保护文本是否只允许本地使用？
- MVP 优先做“续写断更”还是“拯救意难平”？
- 是否需要将“主人公/配角/反派身份”作为显式系统状态？
